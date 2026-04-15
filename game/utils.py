import os
import sys
from game.constants import Color, color_text

# Универсальный метод ввода клавиш
def get_key():
    if os.name == 'nt':
        import msvcrt
        # Чтение клавиши на Windows
        char = msvcrt.getch()
        try:
            return char.decode('utf-8').lower()
        except UnicodeDecodeError:
            return str(char).lower()
    else:
        import tty
        import termios
        # Чтение клавиши на Linux/macOS
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return char.lower()

def clear_screen():
    # 'cls' для Windows, 'clear' для POSIX систем (Linux, macOS)
    os.system('cls' if os.name == 'nt' else 'clear')

def show_logo():
    logo = color_text(r"""
  ██╗   ██╗ ██████╗ ██╗  ██╗███████╗██╗      ██████╗ ██████╗  ██████╗ ███╗   ██╗
  ╚██╗ ██╔╝██╔═══██╗╚██╗██╔╝██╔════╝██║     ██╔═══██╗██╔══██╗██╔═══██╗████╗  ██║
   ╚████╔╝ ██║   ██║ ╚███╔╝ █████╗  ██║     ██║   ██║██████╔╝██║   ██║██╔██╗ ██║
    ╚██╔╝  ██║   ██║ ██╔██╗ ██╔══╝  ██║     ██║   ██║██╔══██╗██║   ██║██║╚██╗██║
     ██║   ╚██████╔╝██╔╝ ██╗███████╗███████╗╚██████╔╝██║  ██║╚██████╔╝██║ ╚████║
     ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
""", Color.CYAN)
    clear_screen()
    print(logo)
    print(color_text("\n      [ Нажмите любую клавишу, чтобы начать приключение ]", Color.BOLD))
    get_key()
