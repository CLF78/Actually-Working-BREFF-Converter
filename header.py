#!/usr/bin/env python3

# header.py
# Binary file header definitions

from dataclasses import dataclass, field, Field
from common import BaseBinary, IGNORE_JSON, STRUCT, UNROLL_CONTENT, OVERRIDE_NAME
from project import EffectProject

@dataclass
class BinaryBlockHeader(BaseBinary):
    magic: bytes = field(default=b'REFF', metadata=IGNORE_JSON | STRUCT('4s'))
    block_size: int = field(default=0, metadata=IGNORE_JSON | STRUCT('I'))
    project: EffectProject = field(kw_only=True, default=None, metadata=UNROLL_CONTENT)

    def to_bytes(self) -> bytes:

        # Calculate the block size and encode the result
        self.block_size = self.project.size()
        return super().to_bytes()

    def validate(self, max_length: int, field: Field) -> None:

        match field.name:
            case 'magic':
                if self.magic != field.default:
                    raise ValueError('Invalid magic')

            case 'block_size':
                parent: BinaryFileHeader = self.parent
                block_offset = parent.size() + 8
                for block in parent.blocks:
                    block_offset += block.size()

                if self.block_size > max_length - block_offset:
                    raise ValueError(f'Invalid block size')


@dataclass
class BinaryFileHeader(BaseBinary):
    magic: bytes = field(default=b'REFF', metadata=IGNORE_JSON | STRUCT('4s'))
    bom: int = field(default=0xFEFF, metadata=IGNORE_JSON | STRUCT('H'))
    version: int = field(default=9, metadata=STRUCT('H'))
    file_length: int = field(default=0, metadata=IGNORE_JSON | STRUCT('I'))
    header_length: int = field(default=16, metadata=IGNORE_JSON | STRUCT('H'))
    block_count: int = field(default=0, metadata=IGNORE_JSON | STRUCT('H'))
    blocks: list[BinaryBlockHeader] = field(kw_only=True, default_factory=list, metadata=OVERRIDE_NAME('projects'))

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent: BaseBinary = None) -> 'BinaryFileHeader':

        # Parse header fields and validate them
        header = super().from_bytes(data, offset, parent)

        # Parse block headers after the main file header
        offset = header.size()
        for _ in range(header.block_count):
            block = BinaryBlockHeader.from_bytes(data, offset, header)
            header.blocks.append(block)
            offset += block.size()

        # Return result
        return header

    def to_bytes(self) -> bytes:

        # Calculate the block count, header length and file length
        self.block_count = len(self.blocks)
        self.header_length = self.size()
        self.file_length = self.header_length
        for block in self.blocks:
            self.file_length += block.size()

        # Encode everything
        data = super().to_bytes()
        for block in self.blocks:
            data += block.to_bytes()

        # Return it
        return data

    def validate(self, max_length: int, field: Field) -> None:

        match field.name:
            case 'magic':
                if self.magic != field.default:
                    raise ValueError('Invalid magic')

            case 'bom':
                if self.bom != field.default:
                    raise ValueError('Invalid BOM')

            case 'file_length':
                if self.file_length != max_length:
                    raise ValueError('Declared file size does not match the actual file size')

            case 'header_length':
                if self.header_length != self.size():
                    raise ValueError('Declared file header size does not match the expected file header size')

            case 'block_count':
                if self.block_count < 1:
                    raise ValueError('Invalid block count')
