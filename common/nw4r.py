#!/usr/bin/env python3

# nw4r.py
# Common nw4r definitions

from dataclasses import dataclass
from common.common import BaseBinary, fieldex

@dataclass
class VEC3(BaseBinary):
    x: float = fieldex('f')
    y: float = fieldex('f')
    z: float = fieldex('f')
