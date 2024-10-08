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
            return PointParams.from_bytes(data, offset)
        elif shape == EmitterShape.Disc:
            return DiscParams.from_bytes(data, offset)
        elif shape == EmitterShape.Line:
            return LineParams.from_bytes(data, offset)
        elif shape == EmitterShape.Cube:
            return CubeParams.from_bytes(data, offset)
        else:
            return CylindereSphereTorusParams.from_bytes(data, offset)

    @staticmethod
    def from_json(data: dict):
        shape = data['shape']
        if shape == EmitterShape.Point:
            return PointParams.from_json(data)
        elif shape == EmitterShape.Disc:
            return DiscParams.from_json(data)
        elif shape == EmitterShape.Line:
            return LineParams.from_json(data)
        elif shape == EmitterShape.Cube:
            return CubeParams.from_json(data)
        else:
            return CylindereSphereTorusParams.from_json(data)


@dataclass
class PointParams(BaseBinary):
    nothing: int = fieldex('23xB', ignore_json=True, default=0)


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
