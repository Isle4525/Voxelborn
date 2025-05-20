import os
import random
import sys
# Cross-platform key input
try:
    import msvcrt
    def get_key(): return msvcrt.getch().decode().lower()
except ImportError:
    import tty, termios
    def get_key():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1).lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

from enum import Enum
from typing import List

# ---------- Цвета и вывод ----------
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

def show_logo():
    logo = color_text(r"""
  ██╗   ██╗ ██████╗ ██╗  ██╗███████╗██╗      ██████╗ ██████╗  ██████╗ ███╗   ██╗
  ╚██╗ ██╔╝██╔═══██╗╚██╗██╔╝██╔════╝██║     ██╔═══██╗██╔══██╗██╔═══██╗████╗  ██║
   ╚████╔╝ ██║   ██║ ╚███╔╝ █████╗  ██║     ██║   ██║██████╔╝██║   ██║██╔██╗ ██║
    ╚██╔╝  ██║   ██║ ██╔██╗ ██╔══╝  ██║     ██║   ██║██╔══██╗██║   ██║██║╚██╗██║
     ██║   ╚██████╔╝██╔╝ ██╗███████╗███████╗╚██████╔╝██║  ██║╚██████╔╝██║ ╚████║
     ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
""", Color.CYAN)
    os.system('cls' if os.name=='nt' else 'clear')
    print(logo)
    input("Нажмите Enter, чтобы начать...")

# ---------- Классы персонажей и навыков ----------
class ClassType(Enum):
    WARRIOR = 1
    MAGE = 2
    ROGUE = 3

class Skill:
    def __init__(self, name, damage, cost, cooldown=0, description=""):
        self.name = name
        self.damage = damage
        self.cost = cost
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.description = description

class GameObject:
    def __init__(self, x, y, char, color, hp, mana, damage, defense, class_type=None, item_type=None):
        self.x = x; self.y = y; self.char = char; self.color = color
        self.max_hp = hp; self.hp = hp
        self.max_mana = mana; self.mana = mana
        self.damage = damage; self.defense = defense
        self.class_type = class_type
        self.skills: List[Skill] = []
        self.level = 1; self.exp = 0; self.exp_to_level = 100
        self.item_type = item_type

class Game:
    def __init__(self):
        show_logo()
        self.map_width = 60
        self.map_height = 20
        self.ui_width = 30
        self.dungeon_level = 1
        self.biomes = {
            'Пещера': {'floor': '.', 'wall': '#', 'color': Color.WHITE},
            'Лес': {'floor': ',', 'wall': '^', 'color': Color.GREEN},
            'Лава': {'floor': '~', 'wall': '%', 'color': Color.RED},
            'Пустыня': {'floor': '.', 'wall': '+', 'color': Color.YELLOW},
            'Лёд': {'floor': '"', 'wall': '*', 'color': Color.CYAN},
        }
        self.biome = None
        self.floor_char = None
        self.wall_char = None
        self.floor_color = None
        self.wall_color = None
        self.exit_x = None
        self.exit_y = None
        self.game_over = False
        self.inventory: List[GameObject] = []
        self.player: GameObject = None
        self.enemies: List[GameObject] = []
        self.items: List[GameObject] = []
        self.rooms: List[tuple] = []

        self.init_player()
        self.generate_level()
        self.run()


    def init_player(self):
        print("Выберите класс:\n1. Воин\n2. Маг\n3. Разбойник")
        while True:
            ch = get_key()
            if ch in ['1','2','3']: break
        stats_map = {
            '1': {'hp':30,'mana':10,'damage':(4,6),'defense':5},
            '2': {'hp':20,'mana':30,'damage':(2,4),'defense':2},
            '3': {'hp':25,'mana':20,'damage':(3,8),'defense':3},
        }
        stats = stats_map[ch]
        cls = ClassType(int(ch))
        self.player = GameObject(0,0,'@',Color.GREEN,stats['hp'],stats['mana'],stats['damage'],stats['defense'],class_type=cls)
        # Назначение навыков
        if cls == ClassType.WARRIOR:
            self.player.skills = [Skill("Удар щитом",(4,6),0,3,"Оглушает"),Skill("Рывок",(8,12),10,5,"" )]
        elif cls == ClassType.MAGE:
            self.player.skills = [Skill("Огненный шар",(10,15),15,4,""),Skill("Ледяная стрела",(6,10),10,3,"")]
        else:
            self.player.skills = [Skill("Смертельный удар",(5,20),10,5,""),Skill("Двойной удар",(3,6),5,2,"")]

    def combat(self, e: GameObject):
        self.clear_screen()
        print(f"=== Подземелье {self.dungeon_level}, Биом: {self.biome} ===")
        while self.player.hp > 0 and e.hp > 0:
            print(f"Враг   HP: {e.hp}/{e.max_hp}")
            print(f"Вы     HP: {self.player.hp}/{self.player.max_hp} Mana: {self.player.mana}/{self.player.max_mana}")
            print("Навыки:")
            for idx, sk in enumerate(self.player.skills, start=1):
                print(f" {idx}. {sk.name} (DMG {sk.damage}, Cost {sk.cost}, CD {sk.current_cooldown}/{sk.cooldown}) - {sk.description}")
            print("3. Атака | u: Зелье HP | m: Зелье Mana")
            c = get_key()
            if c == 'u':
                self.use_item('hp_potion')
            elif c == 'm':
                self.use_item('mana_potion')
            else:
                if c in ['1', '2']:
                    sk = self.player.skills[int(c)-1]
                    if sk.current_cooldown == 0 and self.player.mana >= sk.cost:
                        dmg = random.randint(*sk.damage)
                        self.player.mana -= sk.cost
                        sk.current_cooldown = sk.cooldown
                    else:
                        dmg = random.randint(*self.player.damage)
                else:
                    dmg = random.randint(*self.player.damage)
                actual = max(0, dmg - e.defense)
                e.hp -= actual
                print(color_text(f"Вы наносите {actual} урона", Color.YELLOW))
            if e.hp > 0:
                ed = max(0, random.randint(*e.damage) - self.player.defense)
                self.player.hp -= ed
                print(color_text(f"Враг наносит {ed} урона", Color.RED))
            for sk in self.player.skills:
                if sk.current_cooldown > 0:
                    sk.current_cooldown -= 1
            if self.player.hp <= 0:
                self.game_over = True
                return
            if e.hp <= 0:
                self.player.exp += self.dungeon_level * 10
                return
            print("Нажмите любую клавишу...")
            get_key()
            self.clear_screen()

    def draw_ui(self):
        ui_lines = ["="*(self.ui_width-1),
                    f"Уровень: {color_text(str(self.dungeon_level), Color.YELLOW)}",
                    f"Биом: {color_text(self.biome, self.wall_color)}", "", 
                    f"HP: {color_text(str(self.player.hp), Color.RED)}/{self.player.max_hp}",
                    f"Мана: {color_text(str(self.player.mana), Color.BLUE)}/{self.player.max_mana}",
                    f"Уровень: {self.player.level}",
                    f"Опыт: {self.player.exp}/{self.player.exp_to_level}", "", 
                    color_text("Навыки:", Color.BOLD)]
        for skill in self.player.skills:
            cd = f" (CD: {skill.current_cooldown}/{skill.cooldown})" if skill.cooldown>0 else ""
            ui_lines.append(f"- {skill.name}: {skill.damage[0]}-{skill.damage[1]} урон, {skill.cost} мана{cd}")
        ui_lines += ["", color_text("Инвентарь:", Color.BOLD)]
        for item in self.inventory:
            ui_lines.append(f"- {item.item_type}")
        ui_lines += ["", color_text("Управление:", Color.BOLD),"WASD - движение","1-2 - навыки","U - зелье здоровья","M - зелье маны","Q - выход", "="*(self.ui_width-1)]

        for y in range(self.map_height):
            row = ''
            for x in range(self.map_width):
                if (x,y)==(self.player.x,self.player.y): row+=color_text('@',Color.GREEN)
                elif (x,y)==(self.exit_x,self.exit_y): row+=color_text('>',Color.YELLOW)
                else:
                    char=self.map[y][x]
                    col=self.floor_color if char==self.floor_char else self.wall_color
                    for e in self.enemies:
                        if (x,y)==(e.x,e.y): char, col = e.char, e.color; break
                    for i in self.items:
                        if (x,y)==(i.x,i.y): char, col = i.char, i.color; break
                    row+=color_text(char,col)
            if y<len(ui_lines): row+= ' '+ui_lines[y]
            print(row)

    def clear_screen(self):
        os.system('cls' if os.name=='nt' else 'clear')

    def choose_biome(self):
        self.biome=random.choice(list(self.biomes.keys()))
        bd=self.biomes[self.biome]
        self.floor_char, self.wall_char=bd['floor'], bd['wall']
        self.floor_color, self.wall_color=Color.WHITE, bd['color']

    def generate_level(self):
        self.choose_biome()
        self.map=[[self.wall_char]*self.map_width for _ in range(self.map_height)]
        self.rooms.clear()
        self.split_room(0,0,self.map_width-1,self.map_height-1)
        for r in range(1,len(self.rooms)): self.connect_rooms(self.rooms[r-1],self.rooms[r])
        room=random.choice(self.rooms)
        self.exit_x, self.exit_y = random.randint(room[0],room[2]), random.randint(room[1],room[3])
        self.map[self.exit_y][self.exit_x]='>'
        self.enemies.clear();self.items.clear()
        self.spawn_enemies();self.spawn_items();self.spawn_player()
        # Place exit
        room = random.choice(self.rooms)
        self.exit_x = random.randint(room[0], room[2])
        self.exit_y = random.randint(room[1], room[3])
        self.map[self.exit_y][self.exit_x] = '>'
        

    def split_room(self,x1,y1,x2,y2,depth=0):
        if depth>=3:
            if x2-x1>=8 and y2-y1>=8:
                room=(x1+random.randint(1,3),y1+random.randint(1,3),x2-random.randint(1,3),y2-random.randint(1,3))
                self.create_room(room);self.rooms.append(room)
            return
        horiz=random.choice([True,False])
        if horiz:
            if y2-y1<12: self.split_room(x1,y1,x2,y2,depth+1);return
            s=random.randint(y1+6,y2-6)
            self.split_room(x1,y1,x2,s,depth+1);self.split_room(x1,s,x2,y2,depth+1)
        else:
            if x2-x1<12: self.split_room(x1,y1,x2,y2,depth+1);return
            s=random.randint(x1+6,x2-6)
            self.split_room(x1,y1,s,y2,depth+1);self.split_room(s,y1,x2,y2,depth+1)

    def create_room(self,room):
        x1,y1,x2,y2=room
        for y in range(y1,y2+1):
            for x in range(x1,x2+1): self.map[y][x]=self.floor_char

    def connect_rooms(self,r1,r2):
        x1,y1=(r1[0]+r1[2])//2,(r1[1]+r1[3])//2
        x2,y2=(r2[0]+r2[2])//2,(r2[1]+r2[3])//2
        while(x1,y1)!=(x2,y2):
            if x1< x2: x1+=1
            elif x1> x2: x1-=1
            elif y1< y2: y1+=1
            elif y1> y2: y1-=1
            if self.map[y1][x1]==self.wall_char: self.map[y1][x1]=self.floor_char

    def spawn_player(self):
        while True:
            x,y=random.randint(1,self.map_width-2),random.randint(1,self.map_height-2)
            if self.map[y][x]==self.floor_char and (x,y)!=(self.exit_x,self.exit_y):
                self.player.x,self.player.y=x,y;break

    def spawn_enemies(self):
        for _ in range(3+self.dungeon_level):
            x,y=self.find_free_cell()
            stats={'hp':10+self.dungeon_level*2,'damage':(2+self.dungeon_level,4+self.dungeon_level),'defense':2+self.dungeon_level//2}
            self.enemies.append(GameObject(x,y,'G',Color.RED,stats['hp'],0,stats['damage'],stats['defense']))

    def spawn_items(self):
        for _ in range(4):
            x,y=self.find_free_cell()
            t=random.choice(['hp_potion','mana_potion'])
            c='!' if t=='hp_potion' else 'M';col=Color.RED if t=='hp_potion' else Color.BLUE
            self.items.append(GameObject(x,y,c,col,0,0,0,0,item_type=t))

    def find_free_cell(self):
        while True:
            x,y=random.randint(1,self.map_width-2),random.randint(1,self.map_height-2)
            if self.map[y][x]==self.floor_char and not any(e.x==x and e.y==y for e in self.enemies) and not any(i.x==x and i.y==y for i in self.items):
                return x,y

    def handle_input(self):
        key=get_key();dx=dy=0
        if key=='w': dy=-1
        elif key=='s': dy=1
        elif key=='a': dx=-1
        elif key=='d': dx=1
        elif key=='q': self.game_over=True;return
        elif key=='u': self.use_item('hp_potion');return
        elif key=='m': self.use_item('mana_potion');return
        elif key in ['1','2']: self.use_skill(int(key)-1);return
        if dx or dy:
            nx,ny=self.player.x+dx,self.player.y+dy
            for enemy in self.enemies:
                if(nx,ny)==(enemy.x,enemy.y):
                    self.combat(enemy)
                    if enemy.hp<=0: self.enemies.remove(enemy)
                    return
            self.player.x,self.player.y=nx,ny

    def use_item(self,item_type):
        for it in self.inventory:
            if it.item_type==item_type:
                if item_type=='hp_potion': self.player.hp=min(self.player.max_hp,self.player.hp+10);print(color_text("Вы использовали зелье здоровья!",Color.GREEN))
                else: self.player.mana=min(self.player.max_mana,self.player.mana+10);print(color_text("Вы использовали зелье маны!",Color.BLUE))
                self.inventory.remove(it);get_key();return
        print(color_text(f"У вас нет {item_type}!",Color.RED));get_key()

    def use_skill(self,idx):
        if idx<0 or idx>=len(self.player.skills):return
        sk=self.player.skills[idx]
        if sk.current_cooldown>0:print(color_text(f"{sk.name} на перезарядке!",Color.RED));get_key();return
        if self.player.mana<sk.cost:print(color_text("Недостаточно маны!",Color.RED));get_key();return
        # ближайшая цель
        tgt,min_d=None,float('inf')
        for e in self.enemies:
            d=abs(e.x-self.player.x)+abs(e.y-self.player.y)
            if d<min_d:tgt, min_d=e,d
        if not tgt:print(color_text("Нет врагов рядом!",Color.RED));get_key();return
        self.player.mana-=sk.cost;sk.current_cooldown=sk.cooldown
        dmg=random.randint(*sk.damage);actual=max(0,dmg-tgt.defense);tgt.hp-=actual
        print(color_text(f"Вы используете {sk.name} и наносите {actual} урона!",Color.YELLOW))
        if tgt.hp<=0: self.enemies.remove(tgt);exp=self.dungeon_level*10;self.player.exp+=exp;print(color_text(f"Враг побежден! Получено {exp} опыта.",Color.GREEN))
        else:
            ed=max(0,random.randint(*tgt.damage)-self.player.defense);self.player.hp-=ed;print(color_text(f"Враг контратакует и наносит {ed} урона!",Color.RED))
            if self.player.hp<=0:self.game_over=True;print(color_text("Вы погибли!",Color.RED))
        get_key()

    def move_enemies(self):
        for enemy in list(self.enemies):
            dx,dy=self.player.x-enemy.x,self.player.y-enemy.y
            sx=1 if dx>0 else -1 if dx<0 else 0
            sy=1 if dy>0 else -1 if dy<0 else 0
            if random.random()<0.6:
                if abs(dx)>abs(dy) and self.map[enemy.y][enemy.x+sx]==self.floor_char:enemy.x+=sx
                elif self.map[enemy.y+sy][enemy.x]==self.floor_char:enemy.y+=sy

    def update(self):
        for it in list(self.items):
            if(it.x,it.y)==(self.player.x,self.player.y):self.inventory.append(it);self.items.remove(it);print(color_text(f"Вы подобрали {it.item_type}!",Color.GREEN));get_key()
        if self.player.exp>=self.player.exp_to_level:
            self.player.level+=1;self.player.exp-=self.player.exp_to_level;self.player.exp_to_level=int(self.player.exp_to_level*1.5)
            self.player.max_hp+=5;self.player.hp=self.player.max_hp;self.player.max_mana+=5;self.player.mana=self.player.max_mana
            print(color_text(f"Поздравляем! Вы достигли {self.player.level} уровня!",Color.YELLOW));get_key()
        for sk in self.player.skills:
            if sk.current_cooldown>0:sk.current_cooldown-=1
        self.move_enemies()
        for enemy in list(self.enemies):
            if(enemy.x,enemy.y)==(self.player.x,self.player.y):
                dmg=random.randint(*enemy.damage);act=max(0,dmg-self.player.defense);self.player.hp-=act;print(color_text(f"Враг атаковал вас и нанес {act} урона!",Color.RED));get_key()
                if self.player.hp<=0:self.game_over=True;break
                if enemy.hp<=0:self.enemies.remove(enemy);exp=self.dungeon_level*10;self.player.exp+=exp;print(color_text(f"Враг побежден! Получено {exp} опыта.",Color.GREEN));get_key()
        if not self.enemies:
            self.dungeon_level+=1;self.generate_level();print(color_text(f"Вы перешли на уровень {self.dungeon_level}!",Color.YELLOW));get_key()

    def run(self):
        while not self.game_over:
            self.clear_screen();self.draw_ui();self.handle_input();self.update()
        self.clear_screen();print(color_text("Игра окончена!",Color.RED));print(f"Вы достигли {self.dungeon_level} уровня подземелья");print(f"Ваш уровень: {self.player.level}");input("Нажмите Enter для выхода...")

if __name__=="__main__":
    Game()
