#!/usr/bin/env python3

# nw4r.py
# Common nw4r definitions

from dataclasses import dataclass
from common.common import BaseBinary, fieldex

@dataclass
class VEC2(BaseBinary):
    x: float = fieldex('f')
    y: float = fieldex('f')


@dataclass
class VEC3(BaseBinary):
    x: float = fieldex('f')
    y: float = fieldex('f')
    z: float = fieldex('f')


@dataclass
class MTX23(BaseBinary):
    _00: float = fieldex('f')
    _01: float = fieldex('f')
    _02: float = fieldex('f')
    _10: float = fieldex('f')
    _11: float = fieldex('f')
    _12: float = fieldex('f')
