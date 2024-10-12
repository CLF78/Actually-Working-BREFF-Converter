#!/usr/bin/env python3

# project.py
# Effect project definitions

from dataclasses import dataclass, Field
from common.common import BaseBinary, fieldex

@dataclass
class EffectTableEntry(BaseBinary):
    name_len: int = fieldex('H')
    name: str = fieldex()
    data_offset: int = fieldex('I')
    data_size: int = fieldex('I')
    data: bytes = fieldex(ignore_binary=True) # Handled manually

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent: BaseBinary = None) -> 'EffectTableEntry':

        # Get effect
        effect = super().from_bytes(data, offset, parent)
        offset = parent.offset + effect.data_offset
        effect.data = data[offset:offset + effect.data_size]
        return effect

    def to_bytes(self) -> bytes:
        self.name_len = len(self.name) + 1
        self.data_size = len(self.data)
        return super().to_bytes()

    # TODO validation
    def validate(self, max_length: int, field: Field) -> None:
        return


@dataclass
class EffectTable(BaseBinary):
    table_size: int = fieldex('I')
    entry_count: int = fieldex('H2x')
    entries: list[EffectTableEntry] = fieldex(ignore_binary=True) # Handled manually
    offset: int = fieldex(ignore_binary=True)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent: BaseBinary = None) -> 'EffectTable':

        # Parse fields and validate them
        table: EffectTable = super().from_bytes(data, offset, parent)
        table.offset = offset

        # Parse table entries after the table header
        offset += table.size('entry_count')
        for _ in range(table.entry_count):
            entry = EffectTableEntry.from_bytes(data, offset, table)
            table.entries.append(entry)
            offset += entry.size('data_size')

        # Return result
        return table

    # TODO rewrite this method
    """
    def to_bytes(self) -> bytes:

        # Set the table size and entry count
        self.entry_count = len(self.entries)
        for entry in self.entries:
            self.table_size += entry.size('data_size')

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
    """

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
    project_name: str = fieldex(align_pad=4)
    effect_table: EffectTable = fieldex(ignore_json=True)

    def to_bytes(self) -> bytes:

        # Set project header size and name length, then pack everything
        self.project_header_size = self.size('name')
        self.project_name_length = len(self.project_name) + 1
        return super().to_bytes()

    def validate(self, max_length: int, field: Field) -> None:
        match field.name:
            case 'name':
                if self.project_header_size != self.size('name'):
                    raise ValueError('Invalid project header size')
                if self.project_name_length != len(self.project_name) + 1:
                    raise ValueError('Project name length mismatch')
