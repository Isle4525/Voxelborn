import random
from typing import List
from game.constants import Color, color_text, ClassType, BIOMES
from game.utils import get_key, clear_screen, show_logo
from game.entities import GameObject, Skill
from game.world import DungeonGenerator

class GameEngine:
    def __init__(self):
        show_logo()
        self.map_width = 60
        self.map_height = 20
        self.ui_width = 30
        self.dungeon_level = 1
        
        self.game_over = False
        self.inventory: List[GameObject] = []
        self.player: GameObject = None
        self.enemies: List[GameObject] = []
        self.items: List[GameObject] = []
        
        self.generator = DungeonGenerator(self.map_width, self.map_height)
        self.init_player()
        self.generate_level()

    def init_player(self):
        print("Выберите класс:\n1. Воин\n2. Маг\n3. Разбойник")
        while True:
            ch = get_key()
            if ch in ['1', '2', '3']: break
        
        stats_map = {
            '1': {'hp': 30, 'mana': 10, 'damage': (4, 6), 'defense': 5},
            '2': {'hp': 20, 'mana': 30, 'damage': (2, 4), 'defense': 2},
            '3': {'hp': 25, 'mana': 20, 'damage': (3, 8), 'defense': 3},
        }
        stats = stats_map[ch]
        cls = ClassType(int(ch))
        self.player = GameObject(0, 0, '@', Color.GREEN, stats['hp'], stats['mana'], stats['damage'], stats['defense'], class_type=cls)
        
        if cls == ClassType.WARRIOR:
            self.player.skills = [Skill("Удар щитом", (4, 6), 0, 3, "Огнушает"), Skill("Рывок", (8, 12), 10, 5, "")]
        elif cls == ClassType.MAGE:
            self.player.skills = [Skill("Огненный шар", (10, 15), 15, 4, ""), Skill("Ледяная стрела", (6, 10), 10, 3, "")]
        else:
            self.player.skills = [Skill("Смертельный удар", (5, 20), 10, 5, ""), Skill("Двойной удар", (3, 6), 5, 2, "")]

    def generate_level(self):
        self.map, self.biome_name, biome_data = self.generator.generate()
        self.floor_char = biome_data['floor']
        self.wall_char = biome_data['wall']
        self.wall_color = biome_data['color']
        self.floor_color = Color.WHITE
        
        room = random.choice(self.generator.rooms)
        self.exit_x, self.exit_y = random.randint(room[0], room[2]), random.randint(room[1], room[3])
        self.map[self.exit_y][self.exit_x] = '>'
        
        self.enemies.clear()
        self.items.clear()
        self.spawn_entities()

    def spawn_entities(self):
        # Player
        room = random.choice(self.generator.rooms)
        self.player.x, self.player.y = random.randint(room[0], room[2]), random.randint(room[1], room[3])
        
        # Enemies
        for _ in range(3 + self.dungeon_level):
            x, y = self.find_free_cell()
            stats = {'hp': 10 + self.dungeon_level * 2, 'damage': (2 + self.dungeon_level, 4 + self.dungeon_level), 'defense': 2 + self.dungeon_level // 2}
            self.enemies.append(GameObject(x, y, 'G', Color.RED, stats['hp'], 0, stats['damage'], stats['defense']))
            
        # Items
        for _ in range(4):
            x, y = self.find_free_cell()
            t = random.choice(['hp_potion', 'mana_potion'])
            c = '!' if t == 'hp_potion' else 'M'
            col = Color.RED if t == 'hp_potion' else Color.BLUE
            self.items.append(GameObject(x, y, c, col, 0, 0, 0, 0, item_type=t))

    def find_free_cell(self):
        while True:
            room = random.choice(self.generator.rooms)
            x, y = random.randint(room[0], room[2]), random.randint(room[1], room[3])
            if (x, y) != (self.player.x, self.player.y) and (x, y) != (self.exit_x, self.exit_y):
                return x, y

    def combat(self, e: GameObject):
        clear_screen()
        print(f"=== Подземелье {self.dungeon_level}, Биом: {self.biome_name} ===")
        while self.player.is_alive() and e.is_alive():
            print(f"Враг   HP: {e.hp}/{e.max_hp}")
            print(f"Вы     HP: {self.player.hp}/{self.player.max_hp} Mana: {self.player.mana}/{self.player.max_mana}")
            print("Навыки:")
            for idx, sk in enumerate(self.player.skills, start=1):
                print(f" {idx}. {sk.name} (DMG {sk.damage}, Cost {sk.cost}, CD {sk.current_cooldown}/{sk.cooldown})")
            print("3. Атака | u: Зелье HP | m: Зелье Mana")
            
            c = get_key()
            if c == 'u': self.use_item('hp_potion')
            elif c == 'm': self.use_item('mana_potion')
            else:
                dmg = random.randint(*self.player.damage)
                if c in ['1', '2']:
                    sk = self.player.skills[int(c)-1]
                    if sk.current_cooldown == 0 and self.player.mana >= sk.cost:
                        dmg = random.randint(*sk.damage)
                        self.player.mana -= sk.cost
                        sk.current_cooldown = sk.cooldown
                
                actual = max(0, dmg - e.defense)
                e.hp -= actual
                print(color_text(f"Вы наносите {actual} урона", Color.YELLOW))
            
            if e.is_alive():
                ed = max(0, random.randint(*e.damage) - self.player.defense)
                self.player.hp -= ed
                print(color_text(f"Враг наносит {ed} урона", Color.RED))
                
            for sk in self.player.skills:
                if sk.current_cooldown > 0: sk.current_cooldown -= 1
            
            if not self.player.is_alive():
                self.game_over = True
                return
            if not e.is_alive():
                self.player.exp += self.dungeon_level * 10
                return
            print("Нажмите любую клавишу...")
            get_key()
            clear_screen()

    def draw(self):
        ui_lines = [
            "=" * (self.ui_width - 1),
            f"Уровень: {color_text(str(self.dungeon_level), Color.YELLOW)}",
            f"Биом: {color_text(self.biome_name, self.wall_color)}", "",
            f"HP: {color_text(str(self.player.hp), Color.RED)}/{self.player.max_hp}",
            f"Мана: {color_text(str(self.player.mana), Color.BLUE)}/{self.player.max_mana}",
            f"Уровень: {self.player.level}",
            f"Опыт: {self.player.exp}/{self.player.exp_to_level}", "",
            color_text("Управление:", Color.BOLD), "WASD - движение", "1-2 - навыки", "U/M - зелья", "Q - выход",
            "=" * (self.ui_width - 1)
        ]

        for y in range(self.map_height):
            row = ''
            for x in range(self.map_width):
                if (x, y) == (self.player.x, self.player.y): row += color_text('@', Color.GREEN)
                elif (x, y) == (self.exit_x, self.exit_y): row += color_text('>', Color.YELLOW)
                else:
                    char = self.map[y][x]
                    col = self.floor_color if char == self.floor_char else self.wall_color
                    for e in self.enemies:
                        if (x, y) == (e.x, e.y): char, col = e.char, e.color; break
                    for i in self.items:
                        if (x, y) == (i.x, i.y): char, col = i.char, i.color; break
                    row += color_text(char, col)
            if y < len(ui_lines): row += ' ' + ui_lines[y]
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
                if item_type == 'hp_potion': self.player.hp = min(self.player.max_hp, self.player.hp + 10)
                else: self.player.mana = min(self.player.max_mana, self.player.mana + 10)
                self.inventory.remove(it)
                return

    def update(self):
        # Pick up items
        for it in list(self.items):
            if (it.x, it.y) == (self.player.x, self.player.y):
                self.inventory.append(it)
                self.items.remove(it)
        
        # Level up
        if self.player.exp >= self.player.exp_to_level:
            self.player.level += 1
            self.player.exp -= self.player.exp_to_level
            self.player.exp_to_level = int(self.player.exp_to_level * 1.5)
            self.player.max_hp += 5; self.player.hp = self.player.max_hp
            
        # Move enemies
        for enemy in self.enemies:
            if random.random() < 0.3:
                dx = 1 if self.player.x > enemy.x else -1 if self.player.x < enemy.x else 0
                dy = 1 if self.player.y > enemy.y else -1 if self.player.y < enemy.y else 0
                nx, ny = enemy.x + dx, enemy.y + dy
                if self.map[ny][nx] == self.floor_char:
                    enemy.x, enemy.y = nx, ny

    def run(self):
        while not self.game_over:
            clear_screen()
            self.draw()
            self.handle_input()
            self.update()
        print(color_text("Игра окончена!", Color.RED))
