from init import *
from base_sprites import Tile
from tanks import Player
# модуль для загрузки уровней


def load_level(filename):
    filename = "data/maps/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y, spawn_point = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('bricks', x, y)
            elif level[y][x] == 'X':
                Tile('block', x, y)
            elif level[y][x] == 'E':
                Tile('empty', x, y)
                enemy_spawn_points.append((x, y))
            elif level[y][x] == '@':
                Tile('empty', x, y)
                spawn_point = (x, y)
                new_player = Player(x, y, spawn_point)
    return new_player, x, y, spawn_point
