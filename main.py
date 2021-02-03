import sys
import os
import pygame
from math import sin, cos, radians

NORTH, EAST, SOUTH, WEST = 0, 1, 2, 3
FPS = 60
pygame.init()
size = WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode(size)
pygame.key.set_repeat(10, 20)


def terminate():
    pygame.quit()
    sys.exit()

    # while True:
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             terminate()
    #         elif event.type == pygame.KEYDOWN or \
    #                 event.type == pygame.MOUSEBUTTONDOWN:
    #             return
    #     pygame.display.flip()
    #     clock.tick(FPS)


def convert_dir_to_x_y(direction):
    return int(sin(radians(direction * 90))), -int(cos(radians(direction * 90)))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        if tile_type != 'empty':
            collidable_group.add(self)
        if tile_type == 'bricks':
            breakable_group.add(self)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, center_x, center_y, owner_name, direction, velocity=5):
        super().__init__(top_layer_group, bullet_group,  all_sprites)
        self.velocity = velocity
        self.direction = direction
        self.image = pygame.transform.rotate(bullet_image, -90 * self.direction)
        self.rect = self.image.get_rect()
        self.rect.center = center_x, center_y
        if owner_name == 'Player':
            self.enemies = enemy_team
        else:
            self.enemies = player_team

    def update(self):
        dir_x, dir_y = convert_dir_to_x_y(self.direction)
        self.rect = self.rect.move(self.velocity * dir_x, self.velocity * dir_y)
        if pygame.sprite.spritecollideany(self, self.enemies):
            pass
        elif pygame.sprite.spritecollideany(self, breakable_group):
            killed = pygame.sprite.spritecollide(self, breakable_group, False)[0]
            killed.kill()
            self.kill()
            Tile('empty', killed.rect.x // tile_width, killed.rect.y // tile_height)
        elif pygame.sprite.spritecollideany(self, collidable_group):
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_team, top_layer_group, all_sprites)
        self.image = player_image
        self.direction = NORTH
        self.rect = self.image.get_rect().move(tile_width * pos_x + 4, tile_height * pos_y + 2)
        self.cooldown_duration = 750
        self.cooldown_start = -self.cooldown_duration

    def update(self, dx, dy, direction):
        self.rect = self.rect.move(dx, dy)
        prev_direction = self.direction
        self.direction = direction
        self.image = pygame.transform.rotate(player_image, -90 * self.direction)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        if pygame.sprite.spritecollideany(self, collidable_group):
            self.rect = self.rect.move(-dx, -dy)
            self.direction = prev_direction
            self.image = pygame.transform.rotate(player_image, -90 * self.direction)
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def shoot(self):
        if pygame.time.get_ticks() - self.cooldown_start >= self.cooldown_duration:
            dir_x, dir_y = convert_dir_to_x_y(self.direction)
            bullet_radius = max(bullet_image.get_width(), bullet_image.get_height()) // 2
            Bullet(self.rect.x + self.rect.width // 2 * (1 + dir_x) + bullet_radius * dir_x,
                   self.rect.y + self.rect.height // 2 * (1 + dir_y) + bullet_radius * dir_y,
                   self.__class__.__name__, self.direction)
            self.cooldown_start = pygame.time.get_ticks()

    def set_cooldown(self, cooldown):
        self.cooldown_duration = cooldown


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
    return new_player, x, y


tile_images = {
    'bricks': load_image('bricks.png'),
    'block': load_image('block.png'),
    'empty': load_image('ground.png')}
player_image = load_image('player_tank.png')
bullet_image = load_image('bullet.png')
tile_width = tile_height = 32
all_sprites = pygame.sprite.Group()
top_layer_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
collidable_group = pygame.sprite.Group()
breakable_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
player_team = pygame.sprite.Group()
enemy_team = pygame.sprite.Group()
player, level_x, level_y = generate_level(load_level('map1.txt'))
pygame.display.set_caption("Танчики")
# camera = Camera((level_x, level_y))
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                terminate()

            if event.key == pygame.K_UP:
                player.update(0, -1, NORTH)
            if event.key == pygame.K_RIGHT:
                player.update(1, 0, EAST)
            if event.key == pygame.K_DOWN:
                player.update(0, 1, SOUTH)
            if event.key == pygame.K_LEFT:
                player.update(-1, 0, WEST)

            if event.key == pygame.K_e:
                player.shoot()
    screen.fill('black')
    # camera.update(player)
    # for sprite in all_sprites:
    #     camera.apply(sprite)
    bullet_group.update()
    tiles_group.draw(screen)
    top_layer_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
