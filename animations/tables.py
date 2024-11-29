#!/usr/bin/env python3

# tables.py
# Animation table definitions

from enum import auto
from common.common import CEnum
from common.field import *

#################
# Generic Table #
#################

class AnimDataTable(Structure):
    entry_count = u16('H2x')


#############
# Key Table #
#############

class KeyType(CEnum):
    Fixed = auto()  # Use data embedded in the key frame
    Range  = auto() # Use random clamping on the data at the given index in the range table
    Random = auto() # Pick a random range from the random table and use it for clamping


class KeyCurveType(CEnum):
    Linear = auto()
    Hermite = auto()
    Step = auto()


class KeyFrameBase(Structure):
    frame = u16()
    value_type = EnumField(KeyType, 'Bx')


##############
# Name Table #
##############

class NameTableEntry(Structure):
    name_len = u16()
    name = string()

    def to_bytes(self) -> bytes:
        self.name_len = len(self.name) + 1
        return super().to_bytes()


class NameTable(Structure):
    base = StructField(AnimDataTable)
    name_ptrs = ListField(u32(), lambda x: x.base.entry_count)
    names = ListField(StructField(NameTableEntry), lambda x: x.base.entry_count)

    def to_bytes(self) -> bytes:
        self.name_ptrs = [0] * len(self.names)
        self.name_table_size = len(self.names)
        return super().to_bytes()
