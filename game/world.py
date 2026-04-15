import random
from typing import List, Tuple
from game.constants import BIOMES, Color

class DungeonGenerator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.rooms: List[Tuple[int, int, int, int]] = []
        
    def generate(self):
        biome_name = random.choice(list(BIOMES.keys()))
        biome_data = BIOMES[biome_name]
        
        floor_char = biome_data['floor']
        wall_char = biome_data['wall']
        
        dungeon_map = [[wall_char] * self.width for _ in range(self.height)]
        self.rooms = []
        
        self._split_room(0, 0, self.width - 1, self.height - 1)
        
        for r in range(1, len(self.rooms)):
            self._connect_rooms(dungeon_map, self.rooms[r-1], self.rooms[r], floor_char)
            
        for room in self.rooms:
            self._create_room(dungeon_map, room, floor_char)
            
        return dungeon_map, biome_name, biome_data

    def _split_room(self, x1, y1, x2, y2, depth=0):
        if depth >= 3:
            if x2 - x1 >= 8 and y2 - y1 >= 8:
                room = (x1 + random.randint(1, 3), y1 + random.randint(1, 3), 
                        x2 - random.randint(1, 3), y2 - random.randint(1, 3))
                self.rooms.append(room)
            return
            
        horiz = random.choice([True, False])
        if horiz:
            if y2 - y1 < 12: 
                self._split_room(x1, y1, x2, y2, depth + 1)
                return
            s = random.randint(y1 + 6, y2 - 6)
            self._split_room(x1, y1, x2, s, depth + 1)
            self._split_room(x1, s, x2, y2, depth + 1)
        else:
            if x2 - x1 < 12: 
                self._split_room(x1, y1, x2, y2, depth + 1)
                return
            s = random.randint(x1 + 6, x2 - 6)
            self._split_room(x1, y1, s, y2, depth + 1)
            self._split_room(s, y1, x2, y2, depth + 1)

    def _create_room(self, dungeon_map, room, floor_char):
        x1, y1, x2, y2 = room
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                dungeon_map[y][x] = floor_char

    def _connect_rooms(self, dungeon_map, r1, r2, floor_char):
        x1, y1 = (r1[0] + r1[2]) // 2, (r1[1] + r1[3]) // 2
        x2, y2 = (r2[0] + r2[2]) // 2, (r2[1] + r2[3]) // 2
        while (x1, y1) != (x2, y2):
            if x1 < x2: x1 += 1
            elif x1 > x2: x1 -= 1
            elif y1 < y2: y1 += 1
            elif y1 > y2: y1 -= 1
            dungeon_map[y1][x1] = floor_char
