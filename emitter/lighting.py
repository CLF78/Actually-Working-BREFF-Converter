#!/usr/bin/env python3

# lighting.py
# Emitter lighting definitions

from enum import auto
from dataclasses import dataclass
from common.common import BaseBinary, CEnum, fieldex
from common.nw4r import VEC3
from common.gx import GXColor

class LightingMode(CEnum):
    Off = auto()
    Simple = auto()
    Hardware = auto()


class LightingType(CEnum):
    NoLighting = auto()
    Ambient = auto()
    Point = auto()


@dataclass
class Lighting(BaseBinary):
    mode: LightingMode = fieldex('B')
    type: LightingType = fieldex('B')
    ambient_color: GXColor = fieldex()
    diffuse_color: GXColor = fieldex()
    radius: float = fieldex('f')
    position: VEC3 = fieldex()
