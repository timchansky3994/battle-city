import pygame as pg
import os
import sys
# модуль, содержащий нужные переменные и константы, использующиеся везде


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


size = WIDTH, HEIGHT = 608, 416
NORTH, EAST, SOUTH, WEST = 0, 1, 2, 3
FPS = 60
explosion_sound = pg.mixer.Sound("data/sounds/explosion.mp3")
breaking_sound = pg.mixer.Sound("data/sounds/break.mp3")
shooting_sound = pg.mixer.Sound("data/sounds/shoot.mp3")
bump_sound = pg.mixer.Sound("data/sounds/bump.mp3")

enemy_count = 1
enemy_respawn_time = 3100
enemy_spawn_points = list()
enemy_spawn_iteration = 0
ENEMY_RESPAWN = pg.USEREVENT + 1
enemy_respawn = pg.event.Event(ENEMY_RESPAWN)
ENEMY_EFFECT_SPAWN = pg.USEREVENT + 2
enemy_effect_spawn = pg.event.Event(ENEMY_EFFECT_SPAWN)
PLAYER_EFFECT_SPAWN = pg.USEREVENT + 3
player_effect_spawn = pg.event.Event(PLAYER_EFFECT_SPAWN)
PLAYER_RESPAWN = pg.USEREVENT + 4
player_respawn = pg.event.Event(PLAYER_RESPAWN)
GAME_OVER = pg.USEREVENT + 5
game_over = pg.event.Event(GAME_OVER)
PLAYER_KILLED = pg.USEREVENT + 6
player_killed = pg.event.Event(PLAYER_KILLED)
ENEMY_KILLED = pg.USEREVENT + 7
enemy_killed = pg.event.Event(ENEMY_KILLED)

tile_images = {
    'bricks': load_image('bricks.png'),
    'block': load_image('block.png'),
    'empty': load_image('ground.png')}
player_sheet = load_image('player_tank.png')
enemy_sheet = load_image('enemy_tank.png')
explosion_sheet = load_image('explosion.png')
small_explosion_sheet = load_image('small_explosion.png')
spawning_eff_sheet = load_image('spawning_effect.png')
bullet_image = load_image('bullet.png')
tile_width = tile_height = 32

all_sprites = pg.sprite.Group()
top_layer_group = pg.sprite.Group()
tiles_group = pg.sprite.Group()
collidable_group = pg.sprite.Group()
breakable_group = pg.sprite.Group()
bullet_group = pg.sprite.Group()
effects_group = pg.sprite.Group()
player_team = pg.sprite.Group()
enemy_team = pg.sprite.Group()
