from game.engine import GameEngine

def main():
    try:
        engine = GameEngine()
        engine.run()
    except KeyboardInterrupt:
        print("\nИгра прервана. До встречи!")

if __name__ == "__main__":
    main()
