#!/usr/bin/env python3

# tev.py
# TEV Stage definitions

from dataclasses import dataclass, field
from common import BaseBinary, STRUCT, IGNORE_JSON, UNROLL_CONTENT, IGNORE_BINARY
from emitter.gx import *

@dataclass
class TEVStageColor(BaseBinary):
    color_selection_a: GXTevColorArg = field(default=0, metadata=STRUCT('B'))
    color_selection_b: GXTevColorArg = field(default=0, metadata=STRUCT('B'))
    color_selection_c: GXTevColorArg = field(default=0, metadata=STRUCT('B'))
    color_selection_d: GXTevColorArg = field(default=0, metadata=STRUCT('B'))


@dataclass
class TEVStageColorOp(BaseBinary):
    color_operation: GXTevOp = field(default=0, metadata=STRUCT('B'))
    color_bias: GXTevBias = field(default=0, metadata=STRUCT('B'))
    color_scale: GXTevScale = field(default=0, metadata=STRUCT('B'))
    color_clamp: bool = field(default=False, metadata=STRUCT('B'))
    color_register: GXTevRegID = field(default=0, metadata=STRUCT('B'))


@dataclass
class TEVStageAlphaOp(BaseBinary):
    alpha_operation: GXTevOpAlpha = field(default=0, metadata=STRUCT('B'))
    alpha_bias: GXTevBias = field(default=0, metadata=STRUCT('B'))
    alpha_scale: GXTevScale = field(default=0, metadata=STRUCT('B'))
    alpha_clamp: bool = field(default=False, metadata=STRUCT('B'))
    alpha_register: GXTevRegIDAlpha = field(default=0, metadata=STRUCT('B'))


@dataclass
class TEVStageAlpha(BaseBinary):
    alpha_selection_a: GXTevAlphaArg = field(default=0, metadata=STRUCT('B'))
    alpha_selection_b: GXTevAlphaArg = field(default=0, metadata=STRUCT('B'))
    alpha_selection_c: GXTevAlphaArg = field(default=0, metadata=STRUCT('B'))
    alpha_selection_d: GXTevAlphaArg = field(default=0, metadata=STRUCT('B'))


@dataclass
class TEVStage(BaseBinary):
    texture: int = 0
    colors: TEVStageColor = field(default=None, metadata=UNROLL_CONTENT)
    colorop: TEVStageColorOp = field(default=None, metadata=UNROLL_CONTENT)
    alphas: TEVStageAlpha = field(default=None, metadata=UNROLL_CONTENT)
    alphaop: TEVStageAlphaOp = field(default=None, metadata=UNROLL_CONTENT)
    constant_color_selection: GXTevKColorSel = 0
    constant_alpha_selection: GXTevKAlphaSel = 0


@dataclass
class TEVStages(BaseBinary):

    # Number of TEV stages
    num_tev_stages: int = field(default=0, metadata=STRUCT('Bx') | IGNORE_JSON)

    # Number of indirect TEV stages
    indirect_target_stages: int = field(default=0, metadata=STRUCT('B'))

    # TEV Texture value (unsure of purpose)
    texture1: int = field(default=0, metadata=STRUCT('B') | IGNORE_JSON)
    texture2: int = field(default=0, metadata=STRUCT('B') | IGNORE_JSON)
    texture3: int = field(default=0, metadata=STRUCT('B') | IGNORE_JSON)
    texture4: int = field(default=0, metadata=STRUCT('B') | IGNORE_JSON)

    # TEV stage colors
    colors1: TEVStageColor = field(default=None, metadata=IGNORE_JSON)
    colors2: TEVStageColor = field(default=None, metadata=IGNORE_JSON)
    colors3: TEVStageColor = field(default=None, metadata=IGNORE_JSON)
    colors4: TEVStageColor = field(default=None, metadata=IGNORE_JSON)

    # TEV color operations
    colorop1: TEVStageColorOp = field(default=None, metadata=IGNORE_JSON)
    colorop2: TEVStageColorOp = field(default=None, metadata=IGNORE_JSON)
    colorop3: TEVStageColorOp = field(default=None, metadata=IGNORE_JSON)
    colorop4: TEVStageColorOp = field(default=None, metadata=IGNORE_JSON)

    # TEV stage alphas
    alphas1: TEVStageAlpha = field(default=None, metadata=IGNORE_JSON)
    alphas2: TEVStageAlpha = field(default=None, metadata=IGNORE_JSON)
    alphas3: TEVStageAlpha = field(default=None, metadata=IGNORE_JSON)
    alphas4: TEVStageAlpha = field(default=None, metadata=IGNORE_JSON)

    # TEV alpha operations
    alphaop1: TEVStageAlphaOp = field(default=None, metadata=IGNORE_JSON)
    alphaop2: TEVStageAlphaOp = field(default=None, metadata=IGNORE_JSON)
    alphaop3: TEVStageAlphaOp = field(default=None, metadata=IGNORE_JSON)
    alphaop4: TEVStageAlphaOp = field(default=None, metadata=IGNORE_JSON)

    # TEV constant colors
    kcolor1: GXTevKColorSel = field(default=0, metadata=STRUCT('B') | IGNORE_JSON)
    kcolor2: GXTevKColorSel = field(default=0, metadata=STRUCT('B') | IGNORE_JSON)
    kcolor3: GXTevKColorSel = field(default=0, metadata=STRUCT('B') | IGNORE_JSON)
    kcolor4: GXTevKColorSel = field(default=0, metadata=STRUCT('B') | IGNORE_JSON)

    # TEV constant alphas
    kalpha1: GXTevKAlphaSel = field(default=0, metadata=STRUCT('B') | IGNORE_JSON)
    kalpha2: GXTevKAlphaSel = field(default=0, metadata=STRUCT('B') | IGNORE_JSON)
    kalpha3: GXTevKAlphaSel = field(default=0, metadata=STRUCT('B') | IGNORE_JSON)
    kalpha4: GXTevKAlphaSel = field(default=0, metadata=STRUCT('B') | IGNORE_JSON)

    # Parsed TEV stages
    tev_stages: list[TEVStage] = field(default_factory=list, metadata=IGNORE_BINARY)

    def to_json(self) -> dict:

        # Parse each stage
        self.tev_stages.clear()
        for i in range(1, self.num_tev_stages + 1):
            stage = TEVStage()
            stage.texture = getattr(self, f'texture{i}')
            stage.colors = getattr(self, f'colors{i}')
            stage.colorop = getattr(self, f'colorop{i}')
            stage.alphas = getattr(self, f'alphas{i}')
            stage.alphaop = getattr(self, f'alphaop{i}')
            stage.constant_color_selection = getattr(self, f'kcolor{i}')
            stage.constant_alpha_selection = getattr(self, f'kalpha{i}')
            self.tev_stages.append(stage)

        # Return result
        return super().to_json()

    def to_bytes(self) -> bytes:

        # Set value
        self.num_tev_stages = len(self.tev_stages)

        # Unpack each stage into the fields
        for i, data in enumerate(self.tev_stages, 1):
            setattr(self, f'texture{i}', data.texture)
            setattr(self, f'colors{i}', data.colors)
            setattr(self, f'colorop{i}', data.colorop)
            setattr(self, f'alphas{i}', data.alphas)
            setattr(self, f'alphaop{i}', data.alphaop)
            setattr(self, f'kcolor{i}', data.constant_color_selection)
            setattr(self, f'kalpha{i}', data.constant_alpha_selection)

        return super().to_bytes()
