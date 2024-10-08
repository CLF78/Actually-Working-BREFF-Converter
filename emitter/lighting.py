#!/usr/bin/env python3

# lighting.py
# Lighting definitions

from enum import Enum, auto
from dataclasses import dataclass, field
from common import BaseBinary, VEC3, STRUCT
from emitter.gx import GXColor

class LightingMode(Enum):
    Off = 0
    Simple = auto()
    Hardware = auto()


class LightingType(Enum):
    NoLighting = 0
    Ambient = auto()
    Point = auto()


@dataclass
class Lighting(BaseBinary):
    mode: LightingMode = field(default=0, metadata=STRUCT('B'))
    type: LightingType = field(default=0, metadata=STRUCT('B'))
    ambient_color: GXColor = None
    diffuse_color: GXColor = None
    radius: float = field(default=0.0, metadata=STRUCT('f'))
    position: VEC3 = None
