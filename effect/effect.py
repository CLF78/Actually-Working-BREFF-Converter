#!/usr/bin/env python3

# header.py
# Effect header definitions

from common.field import *
from emitter.emitter import EmitterData
from particle.particle import ParticleData
from animations.anim import Animations

class Effect(Structure):
    emitter = StructField(EmitterData)
    particle = StructField(ParticleData)
    animations = StructField(Animations)


class EffectTableEntry(Structure):
    name_len = u16(skip_json=True)
    name = string()
    data_offset = u32()
    data_size = u32()
    data = raw(length=lambda x: x.data_size, skip_binary=True) # Handled manually

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent: Structure | None = None) -> tuple[Structure, int]:
        instance, offset = super().from_bytes(data, offset, parent)
        instance.data = EffectTableEntry.data.from_bytes(data, instance.data_offset, instance)[0]
        return instance, offset

    def to_bytes(self) -> bytes:
        self.name_len = len(self.name) + 1
        self.data_size = len(self.data)
        return super().to_bytes()


class EffectTable(Structure):
    table_size = u32()
    entry_count = u16('H2x')
    entries = ListField(StructField(EffectTableEntry), lambda x: x.entry_count)


class EffectProject(Structure):
    project_header_size = u32('I8x', skip_json=True)
    project_name_length = u16('H2x', skip_json=True)
    project_name = string(alignment=4)
    project_data = raw(length=lambda x: x.parent.block_size - x.project_header_size, skip_json=True)

    def to_bytes(self) -> bytes:
        self.project_header_size = self.size(end_field=EffectProject.project_name)
        self.project_name_length = len(self.project_name) + 1
        return super().to_bytes()


class BinaryBlockHeader(Structure):
    magic = raw(default=b'REFF', length=4, skip_json=True)
    block_size = u32(skip_json=True)
    project = StructField(EffectProject, unroll=True)

    def to_bytes(self) -> bytes:
        self.block_size = self.project.size()
        return super().to_bytes()


class BinaryFileHeader(Structure):
    magic = raw(default=b'REFF', length=4, skip_json=True)
    bom = u16(default=0xFEFF, skip_json=True)
    version = u16()
    file_length = u32(skip_json=True)
    header_length = u16(default=0x10, skip_json=True)
    block_count = u16(default=1, skip_json=True)
    block = StructField(BinaryBlockHeader, unroll=True)

    def to_bytes(self) -> bytes:
        self.file_length = self.size()
        return super().to_bytes()
