import pgzrun
import random
import math
from pygame import Rect

WIDTH = 800
HEIGHT = 480
LEVEL_END = 750  # X da bandeira

# --- Assets
MUSIC_FILE = "8bit-music-for-game"
HERO_IDLE = "hero_idle"
HERO_WALK = "hero_walk"
ENEMY_IDLE = "enemy_idle"
ENEMY_WALK = "enemy_walk"
FLAG_IMAGE = "flag"

# --- Estados do jogo
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_WIN = "win"
STATE_EXIT = "exit"

game_state = STATE_MENU
music_on = False  # Música começa como Off

# --- Classes

class AnimatedActor(Actor):
    def __init__(self, idle_image, walk_image, pos):
        super().__init__(idle_image, pos)
        self.idle_image = idle_image
        self.walk_image = walk_image
        self.walking = False
        self.frame = 0

    def animate(self, walking):
        self.walking = walking
        if walking:
            self.image = self.walk_image if (self.frame // 15) % 2 == 0 else self.idle_image
        else:
            self.image = self.idle_image
        self.frame += 1

class Hero(AnimatedActor):
    def __init__(self, pos):
        super().__init__(HERO_IDLE, HERO_WALK, pos)
        self.vy = 0
        self.on_ground = False

    def update(self):
        if not self.on_ground:
            self.vy += 0.6
            self.y += self.vy
            if self.y > HEIGHT - 60:
                self.y = HEIGHT - 60
                self.on_ground = True
                self.vy = 0

        keys = keyboard
        dx = 0
        if keys.left:
            dx -= 4
        if keys.right:
            dx += 4

        self.x += dx
        self.animate(dx != 0)

        if keys.space and self.on_ground:
            self.vy = -16
            self.on_ground = False

        if self.x < 20:
            self.x = 20
        if self.x > WIDTH - 20:
            self.x = WIDTH - 20

class Enemy(AnimatedActor):
    def __init__(self, pos, territory):
        super().__init__(ENEMY_IDLE, ENEMY_WALK, pos)
        self.territory = territory
        self.direction = 1

    def update(self):
        if self.x < self.territory[0]:
            self.direction = 1
        if self.x > self.territory[1]:
            self.direction = -1
        self.x += self.direction * 2
        self.animate(True)

def create_enemies():
    return [
        Enemy((180, HEIGHT - 60), (120, 220)),
        Enemy((310, HEIGHT - 60), (280, 370)),
        Enemy((470, HEIGHT - 60), (450, 530)),
        Enemy((580, HEIGHT - 60), (570, 670)),
        Enemy((700, HEIGHT - 60), (680, 770)),
    ]

hero = Hero((100, HEIGHT - 60))
enemies = create_enemies()
flag = Actor(FLAG_IMAGE, (LEVEL_END, HEIGHT - 96))

menu_buttons = [
    {"text": "Start Game", "rect": Rect(340, 180, 120, 40), "action": lambda: start_game()},
    {"text": "Music: Off", "rect": Rect(340, 240, 120, 40), "action": lambda: toggle_music()},
    {"text": "Exit", "rect": Rect(340, 300, 120, 40), "action": lambda: exit_game()},
]

def draw():
    screen.clear()
    if game_state == STATE_MENU:
        draw_menu()
    elif game_state == STATE_PLAYING:
        draw_game()
    elif game_state == STATE_WIN:
        draw_game()
        draw_win_message()

def draw_menu():
    screen.fill((30, 30, 60))
    screen.draw.text("PLATFORMER GAME", center=(WIDTH // 2, 100), fontsize=56, color="white")
    for btn in menu_buttons:
        screen.draw.filled_rect(btn["rect"], (60, 60, 110))
        screen.draw.text(btn["text"], center=btn["rect"].center, fontsize=32, color="yellow")

def draw_game():
    screen.fill((60, 180, 255))
    screen.draw.filled_rect(Rect(0, HEIGHT - 40, WIDTH, 40), (90, 60, 40))
    hero.draw()
    for enemy in enemies:
        enemy.draw()
    flag.draw()

def draw_win_message():
    box = Rect(WIDTH//2 - 260, 100, 520, 140)
    screen.draw.filled_rect(box, (20, 20, 60))
    screen.draw.rect(box, (200, 200, 255))
    screen.draw.text(
        "Parabéns, você concluiu o jogo!",
        center=(box.centerx, box.centery - 25), color="white", fontsize=42
    )
    screen.draw.text(
        "Pressione a tecla R para reiniciar.",
        center=(box.centerx, box.centery + 30), color="yellow", fontsize=32
    )

def update():
    if game_state == STATE_PLAYING:
        hero.update()
        for enemy in enemies:
            enemy.update()
        check_collisions()
        check_flag()
    elif game_state == STATE_WIN:
        pass

def on_mouse_down(pos):
    if game_state == STATE_MENU:
        for btn in menu_buttons:
            if btn["rect"].collidepoint(pos):
                btn["action"]()
        update_menu_labels()

def on_key_down(key):
    global game_state
    if game_state == STATE_WIN and key == keys.R:
        reset_game()
        game_state = STATE_MENU

def update_menu_labels():
    menu_buttons[1]["text"] = f"Music: {'On' if music_on else 'Off'}"

def start_game():
    global game_state
    game_state = STATE_PLAYING
    if music_on:
        music.play(MUSIC_FILE)
        music.set_volume(0.3)
    else:
        music.stop()
    reset_game_positions()

def toggle_music():
    global music_on
    music_on = not music_on
    if music_on:
        music.play(MUSIC_FILE)
        music.set_volume(0.3)
    else:
        music.stop()
    update_menu_labels()

def exit_game():
    global game_state
    game_state = STATE_EXIT
    quit()

def check_collisions():
    for enemy in enemies:
        enemy_collision_rect = Rect(enemy.x - 10, enemy.y - 10, 20, 20)
        hero_rect = Rect(hero.x - hero.width // 2, hero.y - hero.height // 2, hero.width, hero.height)
        if enemy_collision_rect.colliderect(hero_rect):
            print("GAME OVER")
            reset_game_positions()

def check_flag():
    hero_rect = Rect(hero.x - hero.width // 2, hero.y - hero.height // 2, hero.width, hero.height)
    flag_rect = Rect(flag.x - flag.width // 2, flag.y - flag.height // 2, flag.width, flag.height)
    if hero_rect.colliderect(flag_rect):
        win_game()

def win_game():
    global game_state
    sounds.collect_points.play()   # Toca o efeito sonoro ao encostar na bandeira
    game_state = STATE_WIN
    music.stop()

def reset_game_positions():
    global hero, enemies
    hero.x, hero.y = 100, HEIGHT - 60
    hero.vy = 0
    hero.on_ground = True
    enemies = create_enemies()

def reset_game():
    reset_game_positions()
    global game_state
    game_state = STATE_MENU

pgzrun.go()
