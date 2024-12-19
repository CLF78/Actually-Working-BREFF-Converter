#!/usr/bin/env python3

# header.py
# Effect header definitions

from common.field import *
from common.nw4r import NameString
from emitter.emitter import EmitterData
from particle.particle import ParticleData
from animations.anim import Animations

class Effect(Structure):
    emitter = StructField(EmitterData)
    particle = StructField(ParticleData)
    animations = StructField(Animations, unroll=True)


class EffectTableEntry(Structure):
    name = StructField(NameString, unroll=True)
    data_offset = u32()
    data_size = u32()
    data = raw(length=data_size, cond=skip_all) # Handled manually

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent: Optional[Structure] = None) -> tuple[Structure, int]:
        instance, offset = super().from_bytes(data, offset, parent)
        instance.data = EffectTableEntry.data.from_bytes(data, instance.data_offset, instance)[0]
        return instance, offset


class EffectTable(Structure):
    table_size = u32()
    entry_count = u16('H2x')
    entries = ListField(StructField(EffectTableEntry), entry_count)

    def to_bytes(self) -> bytes:

        # Get entries
        entries: list[EffectTableEntry] = self.entries

        # Calculate table size and entry count
        self.table_size = 0
        self.entry_count = 0
        for entry in entries:
            self.entry_count += 1
            self.table_size += entry.size(end_field=EffectTableEntry.data_size)
            entry.data_size = len(entry.data)

        # Assign data offsets
        data_offset = self.table_size
        for entry in entries:
            entry.data_offset = data_offset
            data_offset += entry.data_size

        # Encode result
        result = super().to_bytes()

        # Append effect data for each entry
        for entry in entries:
            result += entry.data
        return result


class EffectProject(Structure):
    def get_data_size(self) -> int:
        return self.get_parent(BinaryBlockHeader).block_size - self.project_header_size

    project_header_size = u32('I8x', cond=skip_json)
    project_name_length = u16('H2x', cond=skip_json)
    project_name = string(alignment=4)
    project_data = raw(length=get_data_size, cond=skip_json)

    def to_bytes(self) -> bytes:
        self.project_header_size = self.size(end_field=EffectProject.project_name)
        self.project_name_length = len(self.project_name) + 1
        return super().to_bytes()


class BinaryBlockHeader(Structure):
    magic = raw(default=b'REFF', length=4, cond=skip_json)
    block_size = u32(cond=skip_json)
    project = StructField(EffectProject, unroll=True)

    def to_bytes(self) -> bytes:
        self.block_size = self.project.size()
        return super().to_bytes()


class BinaryFileHeader(Structure):
    magic = raw(default=b'REFF', length=4, cond=skip_json)
    bom = u16(default=0xFEFF, cond=skip_json)
    version = u16()
    file_length = u32(cond=skip_json)
    header_length = u16(default=0x10, cond=skip_json)
    block_count = u16(default=1, cond=skip_json)
    block = StructField(BinaryBlockHeader, unroll=True)

    def to_bytes(self) -> bytes:
        self.file_length = self.size()
        return super().to_bytes()
