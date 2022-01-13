from math import ceil
import lvsfunc as lvf
import vapoursynth as vs
from functools import partial
from enum import Enum, IntEnum
from fractions import Fraction
from lvsfunc.util import clamp_values
from lvsfunc.kernels import Kernel, Catrom
from typing import NamedTuple, Type, Union, Tuple
from vsutil import insert_clip, disallow_variable_format

from .easing import EasingBaseMeta, Linear, OnAxis
from .utils import checkSimilarClips, change_fps

core = vs.core


def fade(
    clipa: vs.VideoNode, clipb: vs.VideoNode, invert: bool, start: int,
    end: int, function: Type[EasingBaseMeta] = Linear
) -> vs.VideoNode:
    clipa_cut = clipa[start:end]
    clipb_cut = clipb[start:end]

    if invert:
        fade = crossfade(clipa_cut, clipb_cut, function)
    else:
        fade = crossfade(clipb_cut, clipa_cut, function)

    return insert_clip(clipa, fade, start)


def fade_freeze(
    clipa: vs.VideoNode, clipb: vs.VideoNode, invert: bool, start: int,
    end: int, function: Type[EasingBaseMeta] = Linear
) -> vs.VideoNode:
    return fade(
        lvf.rfs(clipa, clipa[start if invert else end] * clipa.num_frames, (start, end)),
        lvf.rfs(clipb, clipb[end if invert else start] * clipb.num_frames, (start, end)),
        invert, start, end, function
    )


def fade_in(clip: vs.VideoNode, start: int, end: int, function: Type[EasingBaseMeta] = Linear) -> vs.VideoNode:
    return fade(clip, clip.std.BlankClip(), False, start, end, function)


def fade_out(clip: vs.VideoNode, start: int, end: int, function: Type[EasingBaseMeta] = Linear) -> vs.VideoNode:
    return fade(clip, clip.std.BlankClip(), True, start, end, function)


def fade_in_freeze(clip: vs.VideoNode, start: int, end: int, function: Type[EasingBaseMeta] = Linear) -> vs.VideoNode:
    return fade_in(lvf.rfs(clip, clip[end] * clip.num_frames, (start, end)), start, end, function)


def fade_out_freeze(clip: vs.VideoNode, start: int, end: int, function: Type[EasingBaseMeta] = Linear) -> vs.VideoNode:
    return fade_out(lvf.rfs(clip, clip[start] * clip.num_frames, (start, end)), start, end, function)


def crossfade(
        clipa: vs.VideoNode, clipb: vs.VideoNode, function: Type[EasingBaseMeta],
        debug: Union[bool, int, Tuple[int, int]] = False) -> vs.VideoNode:
    if not checkSimilarClips(clipa, clipb):
        raise ValueError('crossfade: Both clips must have the same length, dimensions and format.')

    ease_function = function(0, 1, clipa.num_frames)

    def _fading(n: int) -> vs.VideoNode:
        weight = ease_function.ease(n)
        merge = clipa.std.Merge(clipb, weight)
        return merge.text.Text(str(weight), 9, 2) if debug else merge

    return clipa.std.FrameEval(_fading)


class PanDirection(IntEnum):
    NORMAL = 0
    INVERTED = 1


class PanFunction(NamedTuple):
    direction: PanDirection = PanDirection.NORMAL
    function_x: Type[EasingBaseMeta] = OnAxis
    function_y: Type[EasingBaseMeta] = OnAxis


class PanFunctions(PanFunction, Enum):
    VERTICAL_TTB = PanFunction(function_y=Linear)
    HORIZONTAL_LTR = PanFunction(function_x=Linear)
    VERTICAL_BTT = PanFunction(PanDirection.INVERTED, function_y=Linear)
    HORIZONTAL_RTL = PanFunction(PanDirection.INVERTED, function_x=Linear)


@disallow_variable_format
def panner(
    clip: vs.VideoNode, stitched: vs.VideoNode, pan_func: PanFunction = PanFunctions.VERTICAL_TTB,
    fps: Fraction = Fraction(24000, 1001), kernel: Kernel = Catrom()
) -> vs.VideoNode:
    assert clip.format
    assert stitched.format

    if (stitched.format.subsampling_h, stitched.format.subsampling_w) != (0, 0):
        raise ValueError("stgfunc.panner: stitched can't be subsampled!")

    clip_cfps = change_fps(clip, fps)

    offset_x, offset_y = (stitched.width - clip.width), (stitched.height - clip.height)

    ease_x = pan_func.function_x(0, offset_x, clip_cfps.num_frames).ease
    ease_y = pan_func.function_y(0, offset_y, clip_cfps.num_frames).ease

    clamp_x = partial(clamp_values, max_val=offset_x, min_val=0)
    clamp_y = partial(clamp_values, max_val=offset_y, min_val=0)

    def _pan(n: int) -> vs.VideoNode:
        x_e, x_v = divmod(clamp_x(ease_x(n)), 1)
        y_e, y_v = divmod(clamp_y(ease_y(n)), 1)

        if n == clip_cfps.num_frames - 1:
            x_e, y_e = clamp_x(offset_x - 1), clamp_y(offset_y - 1)
            x_v, y_v = int(x_e == offset_x - 1), int(y_e == offset_y - 1)

        x_c, y_c = ceil(x_v), ceil(y_v)

        cropped = stitched.std.CropAbs(
            clip.width + x_c, clip.height + y_c, int(x_e), int(y_e)
        )

        shifted = kernel.shift(cropped, (y_v, x_v))

        return shifted.std.Crop(bottom=y_c, right=x_c)

    newpan = clip_cfps.std.FrameEval(_pan)

    return newpan[::-1] if pan_func.direction == PanDirection.INVERTED else newpan