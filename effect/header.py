#!/usr/bin/env python3

# header.py
# Binary file header definitions

from dataclasses import dataclass, Field
from common.common import BaseBinary, fieldex
from effect.project import EffectProject

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
                if self.block_size > max_length - self.parent.header_length:
                    raise ValueError(f'Invalid block size')


@dataclass
class BinaryFileHeader(BaseBinary):
    magic: bytes = fieldex('4s', ignore_json=True, default=b'REFF')
    bom: int = fieldex('H', ignore_json=True, default=0xFEFF)
    version: int = fieldex('H')
    file_length: int = fieldex('I', ignore_json=True)
    header_length: int = fieldex('H', ignore_json=True, default=16)
    block_count: int = fieldex('H', ignore_json=True, default=1)
    block: BinaryBlockHeader = fieldex(unroll_content=True)

    def to_bytes(self) -> bytes:

        # Calculate the file length and encode everything
        self.file_length = self.size()
        return super().to_bytes()

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
                if self.header_length != field.default:
                    raise ValueError('Declared file header size does not match the expected file header size')

            case 'block_count':
                if self.block_count != field.default:
                    raise ValueError('Invalid block count')
