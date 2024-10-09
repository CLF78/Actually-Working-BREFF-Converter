#!/usr/bin/env python3

# params.py
# Emitter parameter definitions

from dataclasses import dataclass

from common.common import BaseBinary, fieldex
from emitter.flags import EmitterShape

class Params(BaseBinary):
    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent: BaseBinary = None):
        shape = parent.emitter_flags.shape
        if shape == EmitterShape.Point:
            return PointParams.from_bytes(data, offset, parent)
        elif shape == EmitterShape.Disc:
            return DiscParams.from_bytes(data, offset, parent)
        elif shape == EmitterShape.Line:
            return LineParams.from_bytes(data, offset, parent)
        elif shape == EmitterShape.Cube:
            return CubeParams.from_bytes(data, offset, parent)
        else:
            return CylindereSphereTorusParams.from_bytes(data, offset, parent)

    @classmethod
    def from_json(cls, data: dict, parent: BaseBinary = None):
        shape = data['shape']
        if shape == EmitterShape.Point:
            return PointParams.from_json(data, parent)
        elif shape == EmitterShape.Disc:
            return DiscParams.from_json(data, parent)
        elif shape == EmitterShape.Line:
            return LineParams.from_json(data, parent)
        elif shape == EmitterShape.Cube:
            return CubeParams.from_json(data, parent)
        else:
            return CylindereSphereTorusParams.from_json(data, parent)


@dataclass
class PointParams(BaseBinary):
    nothing: int = fieldex('23xB', ignore_json=True)


@dataclass
class DiscParams(BaseBinary):
    x_size: float = fieldex('f')
    inner_radius: float = fieldex('f')
    angle_start: float = fieldex('f')
    angle_end: float = fieldex('f')
    z_size: float = fieldex('f4x')


@dataclass
class LineParams(BaseBinary):
    length: float = fieldex('f')
    x_rot: float = fieldex('f')
    y_rot: float = fieldex('f')
    z_rot: float = fieldex('f8x')


@dataclass
class CubeParams(BaseBinary):
    x_size: float = fieldex('f')
    y_size: float = fieldex('f')
    z_size: float = fieldex('f')
    inner_radius: float =  fieldex('f8x')


@dataclass
class CylindereSphereTorusParams(BaseBinary):
    x_size: float = fieldex('f')
    inner_radius: float = fieldex('f')
    angle_start: float = fieldex('f')
    angle_end: float = fieldex('f')
    y_size: float = fieldex('f')
    z_size: float = fieldex('f')
