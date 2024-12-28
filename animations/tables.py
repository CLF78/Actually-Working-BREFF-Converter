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


class KeyCurveFlag(IntFlag):
    StartSlopeAdjust = 1 << 2
    EndSlopeAdjust = 1 << 3


class KeyFrameBase(Structure):
    frame = u16()
    value_type = EnumField(KeyType, 'Bx')


class KeyCurve(Structure):
    def has_curve_flag(self, is_json: bool) -> bool:
        return is_json and self.interpolation == KeyCurveType.Hermite

    raw_curve = u8(cond=skip_json)
    interpolation = EnumField(KeyCurveType, default=KeyCurveType.Linear, cond=skip_binary)
    slope_adjust = FlagEnumField(KeyCurveFlag, default=KeyCurveFlag(0), cond=has_curve_flag)

    def decode(self) -> None:
        self.interpolation = KeyCurveType(self.raw_curve & KeyCurveType.Mask)
        self.slope_adjust = KeyCurveFlag(self.raw_curve & 0xC)
        return super().decode()

    def encode(self) -> None:
        self.raw_curve = self.interpolation.value | self.slope_adjust.value
        return super().encode()

##############
# Name Table #
##############

class NameTable(AnimDataTable):
    name_ptrs = ListField(u32(), AnimDataTable.entry_count)
    names = ListField(StructField(NameString), AnimDataTable.entry_count)

    def encode(self) -> None:
        self.entry_count = len(self.names)
        self.name_ptrs = [0] * len(self.names)
        super().encode()

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
