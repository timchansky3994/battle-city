import sys
import os
import random
import pygame as pg
from math import sin, cos, radians

NORTH, EAST, SOUTH, WEST = 0, 1, 2, 3
FPS = 60
pg.init()
size = WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode(size)
pg.key.set_repeat(10, 20)


def terminate():
    pg.quit()
    sys.exit()


def convert_dir_to_x_y(direction):
    return int(sin(radians(direction * 90))), -int(cos(radians(direction * 90)))


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


class Tile(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        if tile_type != 'empty':
            collidable_group.add(self)
        if tile_type == 'bricks':
            breakable_group.add(self)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Bullet(pg.sprite.Sprite):
    def __init__(self, center_x, center_y, owner_name, direction, velocity=5):
        super().__init__(top_layer_group, bullet_group,  all_sprites)
        self.velocity = velocity
        self.direction = direction
        self.image = pg.transform.rotate(bullet_image, -90 * self.direction)
        self.rect = self.image.get_rect()
        self.rect.center = center_x, center_y
        if owner_name == 'Player':
            self.enemies = enemy_team
        else:
            self.enemies = player_team

    def update(self):
        dir_x, dir_y = convert_dir_to_x_y(self.direction)
        self.rect = self.rect.move(self.velocity * dir_x, self.velocity * dir_y)
        if pg.sprite.spritecollideany(self, self.enemies):
            pg.sprite.spritecollide(self, self.enemies, True)
            self.kill()
        elif pg.sprite.spritecollideany(self, breakable_group):
            killed = pg.sprite.spritecollide(self, breakable_group, False)[0]
            killed.kill()
            self.kill()
            Tile('empty', killed.rect.x // tile_width, killed.rect.y // tile_height)
        elif pg.sprite.spritecollideany(self, collidable_group):
            self.kill()


class BaseTank(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image, *aux_groups):
        super().__init__(top_layer_group, all_sprites, *aux_groups)
        self.image = image
        self.direction = NORTH
        self.rect = self.image.get_rect().move(tile_width * pos_x + 1, tile_height * pos_y + 1)
        self.cooldown_duration = 750
        self.cooldown_start = -self.cooldown_duration

    def shoot(self):
        if pg.time.get_ticks() - self.cooldown_start >= self.cooldown_duration:
            dir_x, dir_y = convert_dir_to_x_y(self.direction)
            bullet_radius = max(bullet_image.get_width(), bullet_image.get_height()) // 2
            Bullet(self.rect.x + self.rect.width // 2 * (1 + dir_x) + bullet_radius * dir_x,
                   self.rect.y + self.rect.height // 2 * (1 + dir_y) + bullet_radius * dir_y,
                   self.__class__.__name__, self.direction)
            self.cooldown_start = pg.time.get_ticks()

    def set_cooldown(self, cooldown):
        self.cooldown_duration = cooldown


class Player(BaseTank):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, player_image, player_team)

    def update(self, dx, dy, direction):
        self.rect = self.rect.move(dx, dy)
        if direction != self.direction:
            self.direction = direction
            self.image = pg.transform.rotate(player_image, -90 * self.direction)
        if pg.sprite.spritecollideany(self, collidable_group) or pg.sprite.spritecollideany(self, enemy_team):
            self.rect = self.rect.move(-dx, -dy)


class Enemy(BaseTank):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, enemy_image, enemy_team)

    def update(self):
        # при столкновении со стеной поворачивается в случайную сторону
        if random.random() < 1 / 3 / FPS:  # с шансом 15% каждую секунду поворачивает
            self.direction = random.choice(list({0, 1, 2, 3} - {self.direction}))
            self.image = pg.transform.rotate(enemy_image, -90 * self.direction)
        dir_x, dir_y = convert_dir_to_x_y(self.direction)
        self.rect = self.rect.move(dir_x, dir_y)
        if pg.sprite.spritecollideany(self, collidable_group) or pg.sprite.spritecollideany(self, player_team):
            self.rect = self.rect.move(-dir_x, -dir_y)
            self.direction = random.randrange(0, 4)
            self.image = pg.transform.rotate(enemy_image, -90 * self.direction)
            # self.rect = self.rect.move(dir_x, dir_y)
        if random.random() < 0.5 / FPS:  # с шансом 40% каждую секунду стреляет
            self.shoot()


# class Camera:
#     def __init__(self, field_size):
#         self.dx = 0
#         self.dy = 0
#         self.field_size = field_size
#
#     def apply(self, obj):
#         obj.rect.x += self.dx
#         obj.rect.y += self.dy
#         if obj.rect.x >= self.field_size[0] * obj.rect.width:
#             obj.rect.x += -obj.rect.width * (1 + self.field_size[0])
#         if obj.rect.y >= self.field_size[1] * obj.rect.width:
#             obj.rect.y += -obj.rect.width * (1 + self.field_size[0])
#         if obj.rect.x <= -obj.rect.width:
#             obj.rect.x += obj.rect.width * (1 + self.field_size[0])
#         if obj.rect.y <= -obj.rect.width:
#             obj.rect.y += obj.rect.width * (1 + self.field_size[0])
#
#     def update(self, target):
#         self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
#         self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('bricks', x, y)
            elif level[y][x] == 'X':
                Tile('block', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == 'E':
                Tile('empty', x, y)
                new_player = Enemy(x, y)
    return new_player, x, y


tile_images = {
    'bricks': load_image('bricks.png'),
    'block': load_image('block.png'),
    'empty': load_image('ground.png')}
player_image = load_image('player_tank.png')
enemy_image = load_image('enemy_tank.png')
bullet_image = load_image('bullet.png')
tile_width = tile_height = 32
all_sprites = pg.sprite.Group()
top_layer_group = pg.sprite.Group()
tiles_group = pg.sprite.Group()
collidable_group = pg.sprite.Group()
breakable_group = pg.sprite.Group()
bullet_group = pg.sprite.Group()
player_team = pg.sprite.Group()
enemy_team = pg.sprite.Group()
player, level_x, level_y = generate_level(load_level('map0.txt'))
pg.display.set_caption("Танчики")
# camera = Camera((level_x, level_y))
clock = pg.time.Clock()
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                terminate()

            if event.key == pg.K_w:
                player.update(0, -1, NORTH)
            if event.key == pg.K_d:
                player.update(1, 0, EAST)
            if event.key == pg.K_s:
                player.update(0, 1, SOUTH)
            if event.key == pg.K_a:
                player.update(-1, 0, WEST)

            if event.key == pg.K_e:
                player.shoot()
    screen.fill('black')
    # camera.update(player)
    # for sprite in all_sprites:
    #     camera.apply(sprite)
    bullet_group.update()
    enemy_team.update()
    tiles_group.draw(screen)
    top_layer_group.draw(screen)
    pg.display.flip()
    clock.tick(FPS)
