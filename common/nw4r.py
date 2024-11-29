#!/usr/bin/env python3

# nw4r.py
# Common nw4r definitions

from common.field import *

class VEC2(Structure):
    x = f32()
    y = f32()


class VEC3(Structure):
    x = f32()
    y = f32()
    z = f32()


class MTX23(Structure):
    _00 = f32()
    _01 = f32()
    _02 = f32()
    _10 = f32()
    _11 = f32()
    _12 = f32()
