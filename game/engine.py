import random
from typing import List, Deque
from collections import deque
from game.constants import Color, color_text, ClassType, BIOMES
from game.utils import get_key, clear_screen, show_logo
from game.entities import GameObject, Skill
from game.world import DungeonGenerator

class GameEngine:
    def __init__(self):
        show_logo()
        self.map_width = 60
        self.map_height = 20
        self.ui_width = 35
        self.dungeon_level = 1
        
        self.game_over = False
        self.inventory: List[GameObject] = []
        self.player: GameObject = None
        self.enemies: List[GameObject] = []
        self.items: List[GameObject] = []
        
        # Лог событий (хранит последние 5 сообщений)
        self.log: Deque[str] = deque(maxlen=5)
        self.log.append("Добро пожаловать в Voxelborn!")
        
        self.generator = DungeonGenerator(self.map_width, self.map_height)
        self.init_player()
        self.generate_level()

    def calculate_damage(self, base_dmg: int, defense: int) -> int:
        variation = max(1, int(base_dmg * 0.15))
        roll = random.randint(base_dmg - variation, base_dmg + variation)
        return max(1, roll - defense)

    def add_log(self, message: str):
        self.log.append(message)

    def init_player(self):
        print("Выберите класс:\n1. Воин\n2. Маг\n3. Разбойник")
        while True:
            ch = get_key()
            if ch in ['1', '2', '3']: break
        
        stats_map = {
            '1': {'hp': 45, 'mana': 10, 'damage': 8, 'defense': 5},
            '2': {'hp': 25, 'mana': 45, 'damage': 5, 'defense': 2},
            '3': {'hp': 35, 'mana': 20, 'damage': 10, 'defense': 3},
        }
        stats = stats_map[ch]
        cls = ClassType(int(ch))
        self.player = GameObject(0, 0, '@', Color.GREEN, stats['hp'], stats['mana'], stats['damage'], stats['defense'], class_type=cls)
        
        if cls == ClassType.WARRIOR:
            self.player.skills = [
                Skill("Удар щитом", 7, 2, 3, "Оглушающий удар"),
                Skill("Рывок", 16, 8, 5, "Мощный выпад")
            ]
        elif cls == ClassType.MAGE:
            self.player.skills = [
                Skill("Огненный шар", 22, 12, 4, "Сжигает врага"),
                Skill("Ледяная стрела", 14, 7, 2, "Замораживает")
            ]
        else:
            self.player.skills = [
                Skill("Смертельный удар", 28, 10, 6, "Критический урон"),
                Skill("Двойной удар", 9, 4, 2, "Две атаки")
            ]

    def generate_level(self):
        self.map, self.biome_name, biome_data = self.generator.generate()
        self.floor_char, self.wall_char = biome_data['floor'], biome_data['wall']
        self.wall_color, self.floor_color = biome_data['color'], Color.WHITE
        
        room = random.choice(self.generator.rooms)
        self.exit_x, self.exit_y = random.randint(room[0], room[2]), random.randint(room[1], room[3])
        self.map[self.exit_y][self.exit_x] = '>'
        
        self.enemies.clear()
        self.items.clear()
        self.spawn_entities()
        self.add_log(f"Вы вошли в биом: {self.biome_name}")

    def spawn_entities(self):
        room = random.choice(self.generator.rooms)
        self.player.x, self.player.y = random.randint(room[0], room[2]), random.randint(room[1], room[3])
        
        names = ["Гоблин", "Скелет", "Орк", "Призрак"]
        for _ in range(3 + self.dungeon_level):
            x, y = self.find_free_cell()
            stats = {'hp': 15 + self.dungeon_level * 5, 'damage': 4 + self.dungeon_level, 'defense': 1 + self.dungeon_level // 2}
            enemy = GameObject(x, y, 'G', Color.RED, stats['hp'], 0, stats['damage'], stats['defense'])
            enemy.name = random.choice(names)
            self.enemies.append(enemy)
            
        for _ in range(4):
            x, y = self.find_free_cell()
            t = random.choice(['hp_potion', 'mana_potion'])
            c, col = ('!', Color.RED) if t == 'hp_potion' else ('M', Color.BLUE)
            self.items.append(GameObject(x, y, c, col, 0, 0, 0, 0, item_type=t))

    def find_free_cell(self):
        while True:
            room = random.choice(self.generator.rooms)
            x, y = random.randint(room[0], room[2]), random.randint(room[1], room[3])
            if (x, y) != (self.player.x, self.player.y) and (x, y) != (self.exit_x, self.exit_y):
                return x, y

    def combat(self, e: GameObject):
        clear_screen()
        self.add_log(f"Сражение с {e.name}!")
        while self.player.is_alive() and e.is_alive():
            clear_screen()
            self.draw_ui_and_map()
            print(f"\n--- БОЙ С {e.name.upper()} ---")
            print(f"Враг HP: {color_text(str(e.hp), Color.RED)} | Вы HP: {color_text(str(self.player.hp), Color.GREEN)}")
            print(f"Нажмите цифру навыка или '3' для атаки")
            
            key = get_key()
            if key == 'u': self.use_item('hp_potion')
            elif key == 'm': self.use_item('mana_potion')
            elif key == '3':
                dmg = self.calculate_damage(self.player.damage, e.defense)
                e.hp -= dmg
                self.add_log(f"Вы бьете {e.name} и наносите {dmg} урона.")
            elif key in [str(i+1) for i in range(len(self.player.skills))]:
                idx = int(key) - 1
                sk = self.player.skills[idx]
                if sk.current_cooldown == 0 and self.player.mana >= sk.cost:
                    dmg = self.calculate_damage(sk.damage, e.defense)
                    e.hp -= dmg
                    self.player.mana -= sk.cost
                    sk.current_cooldown = sk.cooldown
                    self.add_log(f"Вы используете {sk.name} и наносите {dmg} урона!")
                else:
                    self.add_log("Навык недоступен!")
                    continue
            else: continue

            if e.is_alive():
                ed = self.calculate_damage(e.damage, self.player.defense)
                self.player.hp -= ed
                self.add_log(f"{e.name} атакует и наносит {ed} урона.")
            
            for sk in self.player.skills:
                if sk.current_cooldown > 0: sk.current_cooldown -= 1
            
            if not self.player.is_alive(): self.game_over = True; return
            if not e.is_alive():
                exp = self.dungeon_level * 20
                self.player.exp += exp
                self.add_log(f"{e.name} повержен! +{exp} опыта.")
                return

    def draw_ui_and_map(self):
        ui = [
            "=" * (self.ui_width - 1),
            f"Уровень: {color_text(str(self.dungeon_level), Color.YELLOW)}  Биом: {self.biome_name}",
            f"HP:   {color_text(str(self.player.hp), Color.RED)}/{self.player.max_hp}",
            f"Mana: {color_text(str(self.player.mana), Color.BLUE)}/{self.player.max_mana}",
            f"Exp:  {self.player.exp}/{self.player.exp_to_level} (Lvl {self.player.level})",
            "-" * (self.ui_width - 1),
            color_text("НАВЫКИ:", Color.BOLD)
        ]
        for i, sk in enumerate(self.player.skills):
            status = f"CD:{sk.current_cooldown}" if sk.current_cooldown > 0 else "Готов"
            ui.append(f"{i+1}. {sk.name} ({sk.cost} MP) [{status}]")
        ui.append("3. Обычная атака")
        ui.append("-" * (self.ui_width - 1))
        ui.append(color_text("ЖУРНАЛ СОБЫТИЙ:", Color.BOLD))
        ui.extend(list(self.log))
        ui.append("=" * (self.ui_width - 1))

        for y in range(self.map_height):
            row = ''
            for x in range(self.map_width):
                if (x, y) == (self.player.x, self.player.y): row += color_text('@', Color.GREEN)
                elif (x, y) == (self.exit_x, self.exit_y): row += color_text('>', Color.YELLOW)
                else:
                    char, col = self.map[y][x], (self.floor_color if self.map[y][x] == self.floor_char else self.wall_color)
                    for e in self.enemies:
                        if (x, y) == (e.x, e.y): char, col = e.char, e.color; break
                    for i in self.items:
                        if (x, y) == (i.x, i.y): char, col = i.char, i.color; break
                    row += color_text(char, col)
            if y < len(ui): row += '  ' + ui[y]
            print(row)

    def handle_input(self):
        key = get_key()
        dx = dy = 0
        if key == 'w': dy = -1
        elif key == 's': dy = 1
        elif key == 'a': dx = -1
        elif key == 'd': dx = 1
        elif key == 'q': self.game_over = True
        elif key == 'u': self.use_item('hp_potion')
        elif key == 'm': self.use_item('mana_potion')
        
        if dx or dy:
            nx, ny = self.player.x + dx, self.player.y + dy
            if 0 <= nx < self.map_width and 0 <= ny < self.map_height:
                if self.map[ny][nx] != self.wall_char:
                    for enemy in self.enemies:
                        if (nx, ny) == (enemy.x, enemy.y):
                            self.combat(enemy)
                            if not enemy.is_alive(): self.enemies.remove(enemy)
                            return
                    self.player.x, self.player.y = nx, ny
                    if (nx, ny) == (self.exit_x, self.exit_y):
                        self.dungeon_level += 1
                        self.generate_level()

    def use_item(self, item_type):
        for it in self.inventory:
            if it.item_type == item_type:
                if item_type == 'hp_potion':
                    self.player.hp = min(self.player.max_hp, self.player.hp + 15)
                    self.add_log("Вы выпили зелье здоровья.")
                else:
                    self.player.mana = min(self.player.max_mana, self.player.mana + 15)
                    self.add_log("Вы выпили зелье маны.")
                self.inventory.remove(it)
                return
        self.add_log("Нет зелий!")

    def update(self):
        for it in list(self.items):
            if (it.x, it.y) == (self.player.x, self.player.y):
                self.inventory.append(it)
                self.items.remove(it)
                self.add_log(f"Подобрано: {it.item_type}")
        
        if self.player.exp >= self.player.exp_to_level:
            self.player.level += 1
            self.player.exp -= self.player.exp_to_level
            self.player.exp_to_level = int(self.player.exp_to_level * 1.5)
            self.player.max_hp += 10; self.player.hp = self.player.max_hp
            self.player.damage += 2
            self.add_log(f"УРОВЕНЬ ПОВЫШЕН! Теперь вы {self.player.level} уровня.")
            
        for enemy in self.enemies:
            if random.random() < 0.2:
                dx = random.choice([-1, 0, 1]); dy = random.choice([-1, 0, 1])
                nx, ny = enemy.x + dx, enemy.y + dy
                if 0 <= nx < self.map_width and 0 <= ny < self.map_height:
                    if self.map[ny][nx] == self.floor_char and not any(e.x == nx and e.y == ny for e in self.enemies):
                        enemy.x, enemy.y = nx, ny

    def run(self):
        while not self.game_over:
            clear_screen()
            self.draw_ui_and_map()
            self.handle_input()
            self.update()
        clear_screen()
        print(color_text("ИГРА ОКОНЧЕНА", Color.RED))
        print(f"Вы достигли {self.dungeon_level} уровня подземелья.")
        input("Нажмите Enter для выхода...")
