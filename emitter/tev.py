#!/usr/bin/env python3

# tev.py
# TEV stage definitions

from common.field import *
from common.gx import *

class TEVStageColor(Structure):
    color_selection_a = EnumField(GXTevColorArg)
    color_selection_b = EnumField(GXTevColorArg)
    color_selection_c = EnumField(GXTevColorArg)
    color_selection_d = EnumField(GXTevColorArg)


class TEVStageColorOp(Structure):
    color_operation = EnumField(GXTevOp)
    color_bias = EnumField(GXTevBias)
    color_scale = EnumField(GXTevScale)
    color_clamp = boolean()
    color_register = EnumField(GXTevRegID)


class TEVStageAlphaOp(Structure):
    alpha_operation = EnumField(GXTevOpAlpha)
    alpha_bias = EnumField(GXTevBias)
    alpha_scale = EnumField(GXTevScale)
    alpha_clamp = boolean()
    alpha_register = EnumField(GXTevRegIDAlpha)


class TEVStageAlpha(Structure):
    alpha_selection_a = EnumField(GXTevAlphaArg)
    alpha_selection_b = EnumField(GXTevAlphaArg)
    alpha_selection_c = EnumField(GXTevAlphaArg)
    alpha_selection_d = EnumField(GXTevAlphaArg)


class TEVStage(Structure):
    texture = u32()
    colors = StructField(TEVStageColor, True)
    colorop = StructField(TEVStageColorOp, True)
    alphas = StructField(TEVStageAlpha, True)
    alphaop = StructField(TEVStageAlphaOp, True)
    constant_color_selection = EnumField(GXTevKColorSel)
    constant_alpha_selection = EnumField(GXTevKAlphaSel)


class TEVStages(Structure):

    # Number of TEV stages
    num_tev_stages = u8(skip_json=True)

    # Obsolete flag
    flag_clamp = boolean()

    # Number of indirect TEV stages
    indirect_target_stages = u8()

    # TEV Texture value (unsure of purpose)
    texture1 = u8(skip_json=True)
    texture2 = u8(skip_json=True)
    texture3 = u8(skip_json=True)
    texture4 = u8(skip_json=True)

    # TEV stage colors
    colors1 = StructField(TEVStageColor, skip_json=True)
    colors2 = StructField(TEVStageColor, skip_json=True)
    colors3 = StructField(TEVStageColor, skip_json=True)
    colors4 = StructField(TEVStageColor, skip_json=True)

    # TEV color operations
    colorop1 = StructField(TEVStageColorOp, skip_json=True)
    colorop2 = StructField(TEVStageColorOp, skip_json=True)
    colorop3 = StructField(TEVStageColorOp, skip_json=True)
    colorop4 = StructField(TEVStageColorOp, skip_json=True)

    # TEV stage alphas
    alphas1 = StructField(TEVStageAlpha, skip_json=True)
    alphas2 = StructField(TEVStageAlpha, skip_json=True)
    alphas3 = StructField(TEVStageAlpha, skip_json=True)
    alphas4 = StructField(TEVStageAlpha, skip_json=True)

    # TEV alpha operations
    alphaop1 = StructField(TEVStageAlphaOp, skip_json=True)
    alphaop2 = StructField(TEVStageAlphaOp, skip_json=True)
    alphaop3 = StructField(TEVStageAlphaOp, skip_json=True)
    alphaop4 = StructField(TEVStageAlphaOp, skip_json=True)

    # TEV constant colors
    kcolor1 = EnumField(GXTevKColorSel, skip_json=True)
    kcolor2 = EnumField(GXTevKColorSel, skip_json=True)
    kcolor3 = EnumField(GXTevKColorSel, skip_json=True)
    kcolor4 = EnumField(GXTevKColorSel, skip_json=True)

    # TEV constant alphas
    kalpha1 = EnumField(GXTevKAlphaSel, skip_json=True)
    kalpha2 = EnumField(GXTevKAlphaSel, skip_json=True)
    kalpha3 = EnumField(GXTevKAlphaSel, skip_json=True)
    kalpha4 = EnumField(GXTevKAlphaSel, skip_json=True)

    # Parsed TEV stages
    tev_stages = ListField(StructField(TEVStage), skip_binary=True) # Handled manually

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
            self.tev_stages.append((type(stage), stage))

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
