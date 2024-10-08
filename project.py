#!/usr/bin/env python3

# project.py
# Effect project definitions

from dataclasses import dataclass, field, Field

from common import BaseBinary, ALIGN_PAD, IGNORE_JSON, IGNORE_BINARY, OVERRIDE_NAME, STRUCT, UNROLL_CONTENT, align
from effect import Effect

@dataclass
class EffectTable(BaseBinary):
    table_size: int = field(default=0, metadata=IGNORE_JSON | STRUCT('I'))
    entry_count: int = field(default=0, metadata=IGNORE_JSON | STRUCT('H2x'))
    entries: list[Effect] = field(default_factory=list)
    offset: int = field(default=0, metadata=IGNORE_JSON | IGNORE_BINARY)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent: BaseBinary = None) -> 'EffectTable':

        # Parse fields and validate them
        table: EffectTable = super().from_bytes(data, offset, parent)
        table.offset = offset

        # Parse table entries after the table header
        offset += table.size()
        for _ in range(table.entry_count):
            effect = Effect.from_bytes(data, offset, table)
            table.entries.append(effect)
            offset += effect.size()

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
    project_header_size: int = field(default=0, metadata=IGNORE_JSON | STRUCT('I8x'))
    project_name_length: int = field(default=0, metadata=IGNORE_JSON | STRUCT('H2x'))
    project_name: str = field(default='', metadata=ALIGN_PAD(4) | OVERRIDE_NAME('name'))
    effect_table: EffectTable = field(kw_only=True, default=None, metadata=UNROLL_CONTENT)

    def to_bytes(self) -> bytes:

        # Set project header size and name length, then pack everything
        self.project_header_size = self.size()
        self.project_name_length = len(self.project_name) + 1
        return super().to_bytes()

    def validate(self, max_length: int, field: Field) -> None:
        match field.name:
            case 'project_name':
                if self.project_header_size != align(self.size(), 4):
                    raise ValueError('Invalid project header size')
                if self.project_name_length != len(self.project_name) + 1:
                    raise ValueError('Project name length mismatch')
