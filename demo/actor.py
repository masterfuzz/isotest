from dataclasses import dataclass
from iso.gfx.sprite import Sprite

@dataclass
class Actor:
    name: str

@dataclass
class ActorInstance(Actor):
    sprite: Sprite

