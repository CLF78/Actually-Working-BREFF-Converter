#!/usr/bin/env python3

# tev.py
# TEV stage definitions

from dataclasses import dataclass
from common.common import BaseBinary, fieldex
from common.gx import *

@dataclass
class TEVStageColor(BaseBinary):
    color_selection_a: GXTevColorArg = fieldex('B')
    color_selection_b: GXTevColorArg = fieldex('B')
    color_selection_c: GXTevColorArg = fieldex('B')
    color_selection_d: GXTevColorArg = fieldex('B')


@dataclass
class TEVStageColorOp(BaseBinary):
    color_operation: GXTevOp = fieldex('B')
    color_bias: GXTevBias = fieldex('B')
    color_scale: GXTevScale = fieldex('B')
    color_clamp: bool = fieldex('B')
    color_register: GXTevRegID = fieldex('B')


@dataclass
class TEVStageAlphaOp(BaseBinary):
    alpha_operation: GXTevOpAlpha = fieldex('B')
    alpha_bias: GXTevBias = fieldex('B')
    alpha_scale: GXTevScale = fieldex('B')
    alpha_clamp: bool = fieldex('B')
    alpha_register: GXTevRegIDAlpha = fieldex('B')


@dataclass
class TEVStageAlpha(BaseBinary):
    alpha_selection_a: GXTevAlphaArg = fieldex('B')
    alpha_selection_b: GXTevAlphaArg = fieldex('B')
    alpha_selection_c: GXTevAlphaArg = fieldex('B')
    alpha_selection_d: GXTevAlphaArg = fieldex('B')


@dataclass
class TEVStage(BaseBinary):
    texture: int = fieldex()
    colors: TEVStageColor = fieldex(unroll_content=True)
    colorop: TEVStageColorOp = fieldex(unroll_content=True)
    alphas: TEVStageAlpha = fieldex(unroll_content=True)
    alphaop: TEVStageAlphaOp = fieldex(unroll_content=True)
    constant_color_selection: GXTevKColorSel = fieldex()
    constant_alpha_selection: GXTevKAlphaSel = fieldex()


@dataclass
class TEVStages(BaseBinary):

    # Number of TEV stages
    num_tev_stages: int = fieldex('B', ignore_json=True)

    # Obsolete flag
    flag_clamp: bool = fieldex('B')

    # Number of indirect TEV stages
    indirect_target_stages: int = fieldex('B')

    # TEV Texture value (unsure of purpose)
    texture1: int = fieldex('B', ignore_json=True)
    texture2: int = fieldex('B', ignore_json=True)
    texture3: int = fieldex('B', ignore_json=True)
    texture4: int = fieldex('B', ignore_json=True)

    # TEV stage colors
    colors1: TEVStageColor = fieldex(ignore_json=True)
    colors2: TEVStageColor = fieldex(ignore_json=True)
    colors3: TEVStageColor = fieldex(ignore_json=True)
    colors4: TEVStageColor = fieldex(ignore_json=True)

    # TEV color operations
    colorop1: TEVStageColorOp = fieldex(ignore_json=True)
    colorop2: TEVStageColorOp = fieldex(ignore_json=True)
    colorop3: TEVStageColorOp = fieldex(ignore_json=True)
    colorop4: TEVStageColorOp = fieldex(ignore_json=True)

    # TEV stage alphas
    alphas1: TEVStageAlpha = fieldex(ignore_json=True)
    alphas2: TEVStageAlpha = fieldex(ignore_json=True)
    alphas3: TEVStageAlpha = fieldex(ignore_json=True)
    alphas4: TEVStageAlpha = fieldex(ignore_json=True)

    # TEV alpha operations
    alphaop1: TEVStageAlphaOp = fieldex(ignore_json=True)
    alphaop2: TEVStageAlphaOp = fieldex(ignore_json=True)
    alphaop3: TEVStageAlphaOp = fieldex(ignore_json=True)
    alphaop4: TEVStageAlphaOp = fieldex(ignore_json=True)

    # TEV constant colors
    kcolor1: GXTevKColorSel = fieldex('B', ignore_json=True)
    kcolor2: GXTevKColorSel = fieldex('B', ignore_json=True)
    kcolor3: GXTevKColorSel = fieldex('B', ignore_json=True)
    kcolor4: GXTevKColorSel = fieldex('B', ignore_json=True)

    # TEV constant alphas
    kalpha1: GXTevKAlphaSel = fieldex('B', ignore_json=True)
    kalpha2: GXTevKAlphaSel = fieldex('B', ignore_json=True)
    kalpha3: GXTevKAlphaSel = fieldex('B', ignore_json=True)
    kalpha4: GXTevKAlphaSel = fieldex('B', ignore_json=True)

    # Parsed TEV stages
    tev_stages: list[TEVStage] = fieldex(ignore_binary=True)

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
