#!/usr/bin/env python3

# common.py
# Common animation definitions

from common.field import *
from animations.flags import *
from animations.tables import KeyType, KeyFrameBase

# Get the parent emitter
def get_emitter(structure: Structure):
    from effect.effect import Effect
    return structure.get_parent(Effect).emitter

# Get the animation root
def get_anim_header(structure: Structure):
    from animations.header import AnimationHeader
    return structure.get_parent(AnimationHeader)

# Get the sub target count
def get_sub_target_count(structure: Structure):
    return bin(get_anim_header(structure).sub_targets).count('1')

# Get the key type
def get_key_type(structure: Structure) -> KeyType:
    return structure.get_parent(KeyFrameBase).value_type

# Gets the enabled targets
def get_enabled_targets(sub_targets: IntFlag):
    for i, entry in enumerate(sub_targets):
        yield i, entry.name, entry.value

# Checks if the only available target is enabled
def has_single_target(self: Structure, _) -> bool:
    return self.t is not None
