from enum import Enum

class Color:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"

def color_text(text, color):
    return f"{color}{text}{Color.RESET}"

class ClassType(Enum):
    WARRIOR = 1
    MAGE = 2
    ROGUE = 3

BIOMES = {
    'Пещера': {'floor': '.', 'wall': '#', 'color': Color.WHITE},
    'Лес': {'floor': ',', 'wall': '^', 'color': Color.GREEN},
    'Лава': {'floor': '~', 'wall': '%', 'color': Color.RED},
    'Пустыня': {'floor': '.', 'wall': '+', 'color': Color.YELLOW},
    'Лёд': {'floor': '"', 'wall': '*', 'color': Color.CYAN},
}
