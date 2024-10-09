#!/usr/bin/env python3

# Options.py
# Emitter option definitions

from enum import auto
from dataclasses import dataclass

from common.common import BaseBinary, CEnum, fieldex

class ParticleType(CEnum):
    Point = auto()
    Line = auto()
    Free = auto()
    Billboard = auto()
    Directional = auto()
    Stripe = auto()
    SmoothStripe = auto()


class Assist(CEnum):
    Normal = auto() # Render single Quad to Face surface
    Cross = auto()  # Add Quads so they are orthogonal to Normals


class BillboardAssist(CEnum):
    Normal = auto()       # Normal
    YAssist = auto()      # Y-axis billboard
    Directional = auto()  # Billboard using the movement direction as its axis
    NormalNoRoll = auto() # Normal (no roll)


class StripeAssist(CEnum):
    Normal = auto()    # Normal
    Cross = auto()     # Add a surface orthogonal to the Normal
    Billboard = auto() # Always faces the screen
    Tube = auto()      # Expression of a tube shape


class Ahead(CEnum):
    Speed = auto()          # Velocity vector direction
    EmitterCenter = auto()  # Relative position from the center of emitter
    EmitterSpecDir = auto() # Emitter specified direction
    Particle = auto()       # Difference in location from the previous particle
    User = auto()           # User specified
    NotSpecified = auto()   # Unspecified
    ParticleBoth = auto()   # Difference in position with both neighboring particles
    WorldYAxis = auto()     # Unspecified (initialized as the world Y-axis)


class BillboardAhead(CEnum):
    Speed = auto()          # Velocity vector direction
    EmitterCenter = auto()  # Relative position from the center of emitter
    EmitterSpecDir = auto() # Emitter specified direction
    Particle = auto()       # Difference in location from the previous particle
    ParticleBoth = auto()   # Difference in position with both neighboring particles


class RotateAxis(CEnum):
    XOnly = auto() # X-axis rotation only
    YOnly = auto() # Y-axis rotation only
    ZOnly = auto() # Z-axis rotation only
    XYZ = auto()   # 3-axis rotation


class Face(CEnum):
    XY = auto()
    XZ = auto()


class StripeConnect(CEnum):
    NoConnect = 0      # Does not connect
    Ring      = 1 << 0 # Both ends connected
    Emitter   = 1 << 1 # Connect between the newest particle and the emitter
    Mask      = 3


class StripeInitialPrevAxis(CEnum):
    EmitterYAxis =   0      # Y-axis of the emitter
    EmitterXAxis =   1 << 3 # X-axis of the emitter
    EmitterZAxis =   2 << 3 # Z-axis of the emitter
    EmitterXYZAxis = 3 << 3 # Direction in emitter coordinates (1, 1, 1)
    Mask           = 3 << 3


class StripeTexmapType(CEnum):
    Stretch = 0      # Stretch the texture along the stripe's entire length
    Repeat  = 1 << 6 # Repeats the texture for each segment
    Mask    = 1 << 6


class DirectionalPivot(CEnum):
    NoPivot = auto()   # No processing
    Billboard = auto() # Convert into a billboard, with the movement direction as its axis


class Options(BaseBinary):
    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0, parent: BaseBinary = None):
        particle_type = parent.particle_type
        if particle_type == ParticleType.Billboard:
            return BillboardOptions.from_bytes(data, offset, parent)
        elif particle_type == ParticleType.Directional:
            return DirectionalOptions.from_bytes(data, offset, parent)
        elif particle_type == ParticleType.Stripe:
            return StripeOptions.from_bytes(data, offset, parent)
        elif particle_type == ParticleType.SmoothStripe:
            return SmoothStripeOptions.from_bytes(data, offset, parent)
        else:
            return PointLineFreeOptions.from_bytes(data, offset, parent)

    @classmethod
    def from_json(cls, data: dict, parent: BaseBinary = None):
        particle_type = data['particleType']
        if particle_type == ParticleType.Billboard:
            return BillboardOptions.from_json(data, parent)
        elif particle_type == ParticleType.Directional:
            return DirectionalOptions.from_json(data, parent)
        elif particle_type == ParticleType.Stripe:
            return StripeOptions.from_json(data, parent)
        elif particle_type == ParticleType.SmoothStripe:
            return SmoothStripeOptions.from_json(data, parent)
        else:
            return PointLineFreeOptions.from_json(data, parent)


@dataclass
class PointLineFreeOptions(BaseBinary):
    expression: Assist = fieldex('B')
    y_direction: Ahead = fieldex('B')
    rotational_axis: RotateAxis = fieldex('B4x')


@dataclass
class BillboardOptions(BaseBinary):
    expression: BillboardAssist = fieldex('B')
    y_direction: BillboardAhead = fieldex('B')
    rotational_axis: RotateAxis = fieldex('B4x')


@dataclass
class DirectionalOptions(BaseBinary):
    expression: Assist = fieldex('B')
    y_direction: Ahead = fieldex('B')
    rotational_axis: RotateAxis = fieldex('B')
    speed_based_vertical: bool = fieldex('B')
    render_surface: Face = fieldex('B')
    directional_pivot: DirectionalPivot = fieldex('Bx')


@dataclass
class StripeOptions(BaseBinary):
    expression: StripeAssist = fieldex('B')
    y_direction: Ahead = fieldex('B')
    rotational_axis: RotateAxis = fieldex('B')
    num_tube_vertices: int = fieldex('Bx')
    type2: int = fieldex('Bx', ignore_json=True)

    connect: StripeConnect = fieldex(ignore_binary=True)
    initial_prev_axis: StripeInitialPrevAxis = fieldex(ignore_binary=True)
    texmap_type: StripeTexmapType = fieldex(ignore_binary=True)

    def to_json(self) -> dict:
        self.connect = StripeConnect(self.type2 & StripeConnect.Mask)
        self.initial_prev_axis = StripeInitialPrevAxis(self.type2 & StripeInitialPrevAxis.Mask)
        self.texmap_type = StripeTexmapType(self.type2 & StripeTexmapType.Mask)
        return super().to_json()

    def to_bytes(self) -> bytes:
        self.type2 = int(self.connect) | int(self.initial_prev_axis) | int(self.texmap_type)
        return super().to_bytes()


@dataclass
class SmoothStripeOptions(BaseBinary):
    expression: StripeAssist = fieldex('B')
    y_direction: Ahead = fieldex('B')
    rotational_axis: RotateAxis = fieldex('B')
    num_tube_vertices: int = fieldex('B')
    num_interpolation_divisions: int = fieldex('B')
    type2: int = fieldex('Bx', ignore_json=True)

    connect: StripeConnect = fieldex(ignore_binary=True)
    initial_prev_axis: StripeInitialPrevAxis = fieldex(ignore_binary=True)
    texmap_type: StripeTexmapType = fieldex(ignore_binary=True)

    def to_json(self) -> dict:
        self.connect = StripeConnect(self.type2 & StripeConnect.Mask)
        self.initial_prev_axis = StripeInitialPrevAxis(self.type2 & StripeInitialPrevAxis.Mask)
        self.texmap_type = StripeTexmapType(self.type2 & StripeTexmapType.Mask)
        return super().to_json()

    def to_bytes(self) -> bytes:
        self.type2 = int(self.connect) | int(self.initial_prev_axis) | int(self.texmap_type)
        return super().to_bytes()
