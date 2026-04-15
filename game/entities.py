from typing import List, Tuple
from game.constants import ClassType

class Skill:
    def __init__(self, name: str, damage: Tuple[int, int], cost: int, cooldown: int = 0, description: str = ""):
        self.name = name
        self.damage = damage
        self.cost = cost
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.description = description

class GameObject:
    def __init__(self, x, y, char, color, hp, mana, damage, defense, class_type=None, item_type=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.max_hp = hp
        self.hp = hp
        self.max_mana = mana
        self.mana = mana
        self.damage = damage
        self.defense = defense
        self.class_type = class_type
        self.skills: List[Skill] = []
        self.level = 1
        self.exp = 0
        self.exp_to_level = 100
        self.item_type = item_type

    def is_alive(self):
        return self.hp > 0
