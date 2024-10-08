#!/usr/bin/env python3

# params.py
# Emitter parameter definitions

from dataclasses import dataclass, field
from emitter.flags import EmitterShape

from common import BaseBinary, IGNORE_JSON, STRUCT

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
    nothing: int = field(default=0, metadata=IGNORE_JSON | STRUCT('23xB'))


@dataclass
class DiscParams(BaseBinary):
    x_size: float = field(default=0.0, metadata=STRUCT('f'))
    inner_radius: float = field(default=0.0, metadata=STRUCT('f'))
    angle_start: float = field(default=0.0, metadata=STRUCT('f'))
    angle_end: float = field(default=0.0, metadata=STRUCT('f'))
    z_size: float = field(default=0.0, metadata=STRUCT('f4x'))


@dataclass
class LineParams(BaseBinary):
    length: float = field(default=0.0, metadata=STRUCT('f'))
    x_rot: float = field(default=0.0, metadata=STRUCT('f'))
    y_rot: float = field(default=0.0, metadata=STRUCT('f'))
    z_rot: float = field(default=0.0, metadata=STRUCT('f8x'))


@dataclass
class CubeParams(BaseBinary):
    x_size: float = field(default=0.0, metadata=STRUCT('f'))
    y_size: float = field(default=0.0, metadata=STRUCT('f'))
    z_size: float = field(default=0.0, metadata=STRUCT('f'))
    inner_radius: float = field(default=0.0, metadata=STRUCT('f8x'))


@dataclass
class CylindereSphereTorusParams(BaseBinary):
    x_size: float = field(default=0.0, metadata=STRUCT('f'))
    inner_radius: float = field(default=0.0, metadata=STRUCT('f'))
    angle_start: float = field(default=0.0, metadata=STRUCT('f'))
    angle_end: float = field(default=0.0, metadata=STRUCT('f'))
    y_size: float = field(default=0.0, metadata=STRUCT('f'))
    z_size: float = field(default=0.0, metadata=STRUCT('f'))
