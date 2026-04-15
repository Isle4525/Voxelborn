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
        
        # Начинаем генерацию
        self._split_room(0, 0, self.width - 1, self.height - 1)
        
        # Если комнаты не сгенерировались (слишком маленькая карта), создаем одну принудительно
        if not self.rooms:
            self.rooms.append((2, 2, self.width - 3, self.height - 3))
        
        for r in range(1, len(self.rooms)):
            self._connect_rooms(dungeon_map, self.rooms[r-1], self.rooms[r], floor_char)
            
        for room in self.rooms:
            self._create_room(dungeon_map, room, floor_char)
            
        return dungeon_map, biome_name, biome_data

    def _split_room(self, x1, y1, x2, y2, depth=0):
        width = x2 - x1
        height = y2 - y1
        
        # Если достигли глубины или сектор стал слишком мал для деления
        if depth >= 3 or (width < 10 and height < 10):
            if width >= 4 and height >= 4:
                # Создаем комнату внутри сектора с отступами
                rx1 = x1 + random.randint(1, max(1, width // 4))
                ry1 = y1 + random.randint(1, max(1, height // 4))
                rx2 = x2 - random.randint(1, max(1, width // 4))
                ry2 = y2 - random.randint(1, max(1, height // 4))
                if rx2 > rx1 and ry2 > ry1:
                    self.rooms.append((rx1, ry1, rx2, ry2))
            return
            
        # Решаем, как делить: горизонтально или вертикально
        # Если ширина сильно больше высоты — делим вертикально, и наоборот
        if width > height * 1.5:
            split_horizontally = False
        elif height > width * 1.5:
            split_horizontally = True
        else:
            split_horizontally = random.choice([True, False])

        if split_horizontally:
            if height < 8: # Слишком узко для деления
                self._split_room(x1, y1, x2, y2, 3) # Завершаем здесь
                return
            s = random.randint(y1 + 3, y2 - 3)
            self._split_room(x1, y1, x2, s, depth + 1)
            self._split_room(x1, s + 1, x2, y2, depth + 1)
        else:
            if width < 8: # Слишком узко
                self._split_room(x1, y1, x2, y2, 3)
                return
            s = random.randint(x1 + 3, x2 - 3)
            self._split_room(x1, y1, s, y2, depth + 1)
            self._split_room(s + 1, y1, x2, y2, depth + 1)

    def _create_room(self, dungeon_map, room, floor_char):
        x1, y1, x2, y2 = room
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                if 0 <= y < self.height and 0 <= x < self.width:
                    dungeon_map[y][x] = floor_char

    def _connect_rooms(self, dungeon_map, r1, r2, floor_char):
        x1, y1 = (r1[0] + r1[2]) // 2, (r1[1] + r1[3]) // 2
        x2, y2 = (r2[0] + r2[2]) // 2, (r2[1] + r2[3]) // 2
        
        curr_x, curr_y = x1, y1
        while (curr_x, curr_y) != (x2, y2):
            if curr_x != x2:
                curr_x += 1 if x2 > curr_x else -1
            elif curr_y != y2:
                curr_y += 1 if y2 > curr_y else -1
            
            if 0 <= curr_y < self.height and 0 <= curr_x < self.width:
                dungeon_map[curr_y][curr_x] = floor_char
