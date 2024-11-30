#!/usr/bin/env python3

# tables.py
# Animation table definitions

from enum import auto
from common.common import CEnum
from common.field import *
from common.nw4r import NameString

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
    Mask = auto()


class KeyFrameBase(Structure):
    frame = u16(default=0, cond=lambda x: not x.parent.parent.is_init)
    value_type = EnumField(KeyType, 'Bx')


##############
# Name Table #
##############

class NameTable(AnimDataTable):
    name_ptrs = ListField(u32(), lambda x: x.entry_count)
    names = ListField(StructField(NameString), lambda x: x.entry_count)

    def to_bytes(self) -> bytes:
        self.name_ptrs = [u32(), 0] * len(self.names)
        self.name_table_size = len(self.names)
        return super().to_bytes()
