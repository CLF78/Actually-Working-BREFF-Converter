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


class NameString(Structure):
    name_len = u16(cond=skip_json)
    name = string()

    def encode(self) -> None:
        self.name_len = len(self.name) + 1
        super().encode()
