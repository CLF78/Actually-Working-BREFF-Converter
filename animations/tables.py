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
    def has_frame(self, is_json: bool) -> bool:
        from animations.common import get_anim_header
        return not is_json or not get_anim_header(self).is_init

    frame = u16(default=0, cond=has_frame)
    value_type = EnumField(KeyType, 'Bx')

##############
# Name Table #
##############

class NameTable(AnimDataTable):
    name_ptrs = ListField(u32(), AnimDataTable.entry_count)
    names = ListField(StructField(NameString), AnimDataTable.entry_count)

    def to_bytes(self) -> bytes:
        self.entry_count = len(self.names)
        self.name_ptrs = [0] * len(self.names)
        return super().to_bytes()

    def add_entry(self, entry_name: str) -> int:

        # First check if it's already there
        for i, name in enumerate(self.names):
            if name.name == entry_name:
                return i

        # Else add it
        new_entry = NameString(self)
        new_entry.name = entry_name
        self.names.append(new_entry)
        return len(self.names) - 1
