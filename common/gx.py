#!/usr/bin/env python3

# gx.py
# Common GX definitions

from enum import auto
from common.common import CEnum
from common.field import *

class GXCompare(CEnum):
	Never = auto()
	Less = auto()
	LessOrEqual = auto()
	Equal = auto()
	NotEqual = auto()
	GreaterOrEqual = auto()
	Greater = auto()
	Always = auto()


class GXAlphaOp(CEnum):
    And = auto()
    Or = auto()
    ExclusiveOr = auto()
    InverseExclusiveOr = auto()


class GXTevColorArg(CEnum):
	OutputColor = auto()
	OutputAlpha = auto()
	Color0 = auto()
	Alpha0 = auto()
	Color1 = auto()
	Alpha1 = auto()
	Color2 = auto()
	Alpha2 = auto()
	TextureColor = auto()
	TextureAlpha = auto()
	RasterColor = auto()
	RasterAlpha = auto()
	One = auto()
	OneHalf = auto()
	ConstantColorSelection = auto()
	Zero = auto()
	TextureColorRed = auto()
	TextureColorGreen = auto()
	TextureColorBlue = auto()


class GXTevAlphaArg(CEnum):
	OutputAlpha = auto()
	Alpha0 = auto()
	Alpha1 = auto()
	Alpha2 = auto()
	TextureAlpha = auto()
	RasterAlpha = auto()
	ConstantAlphaSelection = auto()
	Zero = auto()


class GXTevOp(CEnum):
	Add = auto()
	Subtract = auto()
	CompR8Greater = auto()
	CompR8Equal = auto()
	CompGR16Greater = auto()
	CompGR16Equal = auto()
	CompBGR24Greater = auto()
	CompBGR24Equal = auto()
	CompRGB8Greater = auto()
	CompRGB8Equal = auto()


class GXTevOpAlpha(CEnum):
	Add = auto()
	Subtract = auto()
	CompR8Greater = auto()
	CompR8Equal = auto()
	CompGR16Greater = auto()
	CompGR16Equal = auto()
	CompBGR24Greater = auto()
	CompBGR24Equal = auto()
	CompA8Greater = auto()
	CompA8Equal = auto()


class GXTevBias(CEnum):
	Zero = auto()
	AddHalf = auto()
	SubHalf = auto()


class GXTevScale(CEnum):
	MultiplyBy1 = auto()
	MultiplyBy2 = auto()
	MultiplyBy4 = auto()
	DivideBy2 = auto()


class GXTevRegID(CEnum):
	OutputColor = auto()
	Color0 = auto()
	Color1 = auto()
	Color2 = auto()


class GXTevRegIDAlpha(CEnum):
	OutputAlpha = auto()
	Alpha0 = auto()
	Alpha1 = auto()
	Alpha2 = auto()


class GXTevKColorSel(CEnum):
	Constant1_1 = auto()
	Constant7_8 = auto()
	Constant3_4 = auto()
	Constant5_8 = auto()
	Constant1_2 = auto()
	Constant3_8 = auto()
	Constant1_4 = auto()
	Constant1_8 = auto()
	ConstantColor0RGB = 0x0C
	ConstantColor1RGB = auto()
	ConstantColor2RGB = auto()
	ConstantColor3RGB = auto()
	ConstantColor0RRR = auto()
	ConstantColor1RRR = auto()
	ConstantColor2RRR = auto()
	ConstantColor3RRR = auto()
	ConstantColor0GGG = auto()
	ConstantColor1GGG = auto()
	ConstantColor2GGG = auto()
	ConstantColor3GGG = auto()
	ConstantColor0BBB = auto()
	ConstantColor1BBB = auto()
	ConstantColor2BBB = auto()
	ConstantColor3BBB = auto()
	ConstantColor0AAA = auto()
	ConstantColor1AAA = auto()
	ConstantColor2AAA = auto()
	ConstantColor3AAA = auto()


class GXTevKAlphaSel(CEnum):
	Constant1_1 = auto()
	Constant7_8 = auto()
	Constant3_4 = auto()
	Constant5_8 = auto()
	Constant1_2 = auto()
	Constant3_8 = auto()
	Constant1_4 = auto()
	Constant1_8 = auto()
	ConstantColor0_Red = 0x10
	ConstantColor1_Red = auto()
	ConstantColor2_Red = auto()
	ConstantColor3_Red = auto()
	ConstantColor0_Green = auto()
	ConstantColor1_Green = auto()
	ConstantColor2_Green = auto()
	ConstantColor3_Green = auto()
	ConstantColor0_Blue = auto()
	ConstantColor1_Blue = auto()
	ConstantColor2_Blue = auto()
	ConstantColor3_Blue = auto()
	ConstantColor0_Alpha = auto()
	ConstantColor1_Alpha = auto()
	ConstantColor2_Alpha = auto()
	ConstantColor3_Alpha = auto()


class GXBlendMode(CEnum):
	NoBlend = auto()
	Blend = auto()
	Logic = auto()
	Subtract = auto()


class GXBlendFactor(CEnum):
	Zero = auto()
	One = auto()
	SourceColor = auto()
	InverseSourceColor = auto()
	SourceAlpha = auto()
	InverseSourceAlpha = auto()
	DestinationAlpha = auto()
	InverseDestinationAlpha = auto()


class GXLogicOp(CEnum):
	Clear = auto()
	Set = auto()
	Copy = auto()
	InverseCopy = auto()
	NoOperation = auto()
	Inverse = auto()
	And = auto()
	NotAnd = auto()
	Or = auto()
	NotOr = auto()
	ExclusiveOr = auto()
	Equivalent = auto()
	ReverseAnd = auto()
	InverseAnd = auto()
	ReverseOr = auto()
	InverseOr = auto()


class GXTexWrapMode(CEnum):
	Clamp = auto()
	Repeat = auto()
	Mirror = auto()


class GXColor(Structure):
	r = u8()
	g = u8()
	b = u8()
	a = u8()
