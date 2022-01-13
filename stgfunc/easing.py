from __future__ import annotations

from typing import Tuple
from abc import ABC, abstractmethod
from math import sqrt, pow, sin, cos, pi


class EasingBase(ABC):
    limit: Tuple[int, int] = (0, 1)

    def __init__(self, start: int = 0, end: int = 1, duration: int = 1) -> None:
        self.start = start
        self.end = end
        self.duration = duration

    @abstractmethod
    def func(self, t: float) -> float:
        pass

    def ease(self, alpha: float) -> float:
        t = self.limit[0] * (1 - alpha) + self.limit[1] * alpha / self.duration
        a = self.func(t)
        return self.end * a + self.start * (1 - a)


class Linear(EasingBase):
    def func(self, t: float) -> float:
        return t


class QuadEaseIn(EasingBase):
    def func(self, t: float) -> float:
        return pow(t, 2)


class QuadEaseOut(EasingBase):
    def func(self, t: float) -> float:
        return -(t * (t - 2))


class QuadEaseInOut(EasingBase):
    def func(self, t: float) -> float:
        if t < 0.5:
            return 2 * QuadEaseIn().func(t)
        return (-2 * t * t) + (4 * t) - 1


class CubicEaseIn(EasingBase):
    def func(self, t: float) -> float:
        return pow(t, 3)


class CubicEaseOut(EasingBase):
    def func(self, t: float) -> float:
        return pow(t - 1, 3) + 1


class CubicEaseInOut(EasingBase):
    def func(self, t: float) -> float:
        if t < 0.5:
            return 4 * CubicEaseIn().func(t)
        return 0.5 * CubicEaseOut().func(2 * t - 1)


class QuarticEaseIn(EasingBase):
    def func(self, t: float) -> float:
        return pow(t, 4)


class QuarticEaseOut(EasingBase):
    def func(self, t: float) -> float:
        return pow(t - 1, 4) + 1


class QuarticEaseInOut(EasingBase):
    def func(self, t: float) -> float:
        if t < 0.5:
            return 8 * QuarticEaseIn().func(t)
        return -8 * QuarticEaseOut().func(t)


class QuinticEaseIn(EasingBase):
    def func(self, t: float) -> float:
        return pow(t, 5)


class QuinticEaseOut(EasingBase):
    def func(self, t: float) -> float:
        return pow(t - 1, 5) + 1


class QuinticEaseInOut(EasingBase):
    def func(self, t: float) -> float:
        if t < 0.5:
            return 16 * QuinticEaseIn().func(t)
        return 0.5 * QuinticEaseOut().func((2 * t) - 1)


class SineEaseIn(EasingBase):
    def func(self, t: float) -> float:
        return sin((t - 1) * pi / 2) + 1


class SineEaseOut(EasingBase):
    def func(self, t: float) -> float:
        return sin(t * pi / 2)


class SineEaseInOut(EasingBase):
    def func(self, t: float) -> float:
        return 0.5 * (1 - cos(t * pi))


class CircularEaseIn(EasingBase):
    def func(self, t: float) -> float:
        return 1 - sqrt(1 - pow(t, 2))


class CircularEaseOut(EasingBase):
    def func(self, t: float) -> float:
        return sqrt((2 - t) * t)


class CircularEaseInOut(EasingBase):
    def func(self, t: float) -> float:
        if t < 0.5:
            return 0.5 * (1 - sqrt(1 - 4 * pow(t, 2)))
        return 0.5 * (sqrt(-((2 * t) - 3) * ((2 * t) - 1)) + 1)


class ExponentialEaseIn(EasingBase):
    def func(self, t: float) -> float:
        if t == 0:
            return 0
        return pow(2, 10 * (t - 1))


class ExponentialEaseOut(EasingBase):
    def func(self, t: float) -> float:
        if t == 1:
            return 1
        return 1 - pow(2, -10 * t)


class ExponentialEaseInOut(EasingBase):
    def func(self, t: float) -> float:
        if t in (0, 1):
            return t

        if t < 0.5:
            return 0.5 * pow(2, (20 * t) - 10)
        return -0.5 * pow(2, (-20 * t) + 10) + 1


class ElasticEaseIn(EasingBase):
    def func(self, t: float) -> float:
        return sin(13 * pi / 2 * t) * pow(2, 10 * (t - 1))


class ElasticEaseOut(EasingBase):
    def func(self, t: float) -> float:
        return sin(-13 * pi / 2 * (t + 1)) * pow(2, -10 * t) + 1


class ElasticEaseInOut(EasingBase):
    def func(self, t: float) -> float:
        if t < 0.5:
            return 0.5 * ElasticEaseIn().func(2 * t)
        return 0.5 * ElasticEaseOut().func(2 * t - 1) + 1


class BackEaseIn(EasingBase):
    def func(self, t: float) -> float:
        return pow(t, 3) - t * sin(t * pi)


class BackEaseOut(EasingBase):
    def func(self, t: float) -> float:
        return 1 - BackEaseIn().func(1 - t)


class BackEaseInOut(EasingBase):
    def func(self, t: float) -> float:
        if t < 0.5:
            return 0.5 * BackEaseIn().func(t * 2)

        return 0.5 * (1 - BackEaseOut().func(t * 2 - 1)) + 0.5


class BounceEaseIn(EasingBase):
    def func(self, t: float) -> float:
        return 1 - BounceEaseOut().func(1 - t)


class BounceEaseOut(EasingBase):
    def func(self, t: float) -> float:
        t2 = pow(t, 2)

        if t < 4 / 11:
            return 121.0 * t2 / 16.0
        elif t < 8 / 11:
            return (363.0 / 40.0 * t2) - (99.0 / 10.0 * t) + 17.0 / 5.0
        elif t < 9 / 10:
            return (4356.0 / 361.0 * t2) - (35442.0 / 1805.0 * t) + 16061.0 / 1805.0
        return (54.0 / 5.0 * t2) - (513.0 / 25.0 * t) + 268.0 / 25.0


class BounceEaseInOut(EasingBase):
    def func(self, t: float) -> float:
        if t < 0.5:
            return 0.5 * BounceEaseIn().func(t * 2)

        return 0.5 * BounceEaseOut().func(t * 2 - 1) + 0.5
