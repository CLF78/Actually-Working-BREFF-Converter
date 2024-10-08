#!/usr/bin/env python3

# header.py
# Binary file header definitions

from dataclasses import dataclass, Field
from common.common import BaseBinary, fieldex
from project import EffectProject

@dataclass
class BinaryBlockHeader(BaseBinary):
    magic: bytes = fieldex('4s', ignore_json=True, default=b'REFF')
    block_size: int = fieldex('I', ignore_json=True)
    project: EffectProject = fieldex(unroll_content=True)

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
    magic: bytes = fieldex('4s', ignore_json=True, default=b'REFF')
    bom: int = fieldex('H', ignore_json=True, default=0xFEFF)
    version: int = fieldex('H')
    file_length: int = fieldex('I', ignore_json=True)
    header_length: int = fieldex('H', ignore_json=True)
    block_count: int = fieldex('H', ignore_json=True)
    blocks: list[BinaryBlockHeader] = fieldex(export_name='projects', default_factory=list)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent: BaseBinary = None) -> 'BinaryFileHeader':

        # Parse header fields and validate them
        header = super().from_bytes(data, offset, parent)

        # Parse block headers after the main file header
        offset = header.size(None, 'block_count')
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
