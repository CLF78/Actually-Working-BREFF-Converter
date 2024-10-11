#!/usr/bin/env python3

# project.py
# Effect project definitions

from dataclasses import dataclass, Field

from common.common import BaseBinary, fieldex
from effect.effect import Effect

@dataclass
class EffectTable(BaseBinary):
    table_size: int = fieldex('I', ignore_json=True)
    entry_count: int = fieldex('H2x', ignore_json=True)
    entries: list[Effect] = fieldex(ignore_binary=True)
    offset: int = fieldex(ignore_binary=True, ignore_json=True)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent: BaseBinary = None) -> 'EffectTable':

        # Parse fields and validate them
        table: EffectTable = super().from_bytes(data, offset, parent)
        table.offset = offset

        # Parse table entries after the table header
        offset += table.size(None, 'entry_count')
        for _ in range(table.entry_count):
            effect = Effect.from_bytes(data, offset, table)
            table.entries.append(effect)
            offset += effect.size(None, 'data_size')

        # Return result
        return table

    def to_bytes(self) -> bytes:

        # Set the table size and entry count
        self.entry_count = len(self.entries)
        for entry in self.entries:
            self.table_size += entry.size()

        # Pack the effect table header
        data = super().to_bytes()
        eff_data = b''

        # Calculate the data offsets and sizes, then encode each table entry and the related data
        offset = self.table_size
        for effect in self.entries:
            effect.data_offset = offset
            data += effect.to_bytes()

            offset += effect.data_size
            eff_data += effect.data.to_bytes()

        # Combine the results
        return data + eff_data

    def validate(self, max_length: int, field: Field) -> None:
        match field.name:
            case 'table_size':
                if not 8 <= self.table_size <= self.parent.parent.block_size:
                    raise ValueError("Invalid table size")

            case 'entry_count':
                if self.entry_count < 1:
                    raise ValueError("Invalid entry count")


@dataclass
class EffectProject(BaseBinary):
    project_header_size: int = fieldex('I8x', ignore_json=True)
    project_name_length: int = fieldex('H2x', ignore_json=True)
    project_name: str = fieldex(export_name='name', align_pad=4)
    effect_table: EffectTable = fieldex(unroll_content=True)

    def to_bytes(self) -> bytes:

        # Set project header size and name length, then pack everything
        self.project_header_size = self.size(None, 'project_name')
        self.project_name_length = len(self.project_name) + 1
        return super().to_bytes()

    def validate(self, max_length: int, field: Field) -> None:
        match field.name:
            case 'project_name':
                if self.project_header_size != self.size(None, 'project_name'):
                    raise ValueError('Invalid project header size')
                if self.project_name_length != len(self.project_name) + 1:
                    raise ValueError('Project name length mismatch')
