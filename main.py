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
pg.display.set_caption("Танчики")
clock = pg.time.Clock()


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


def main_menu():
    intro_text = ["BATTLE CITY",
                  "Начать игру",
                  "Управление",
                  "Выйти"]

    print(pg.font.get_fonts())
    logo_font = pg.font.Font("data/docktrin.ttf", 89)
    text_font = pg.font.Font("data/rockwellnova.ttf", 36)

    logo = logo_font.render(intro_text[0], True, pg.Color('white'))
    logo_rect = logo.get_rect()
    logo_rect.top = 80
    logo_rect.center = WIDTH // 2, logo_rect.center[1]
    screen.blit(logo, logo_rect)

    start_game = text_font.render(intro_text[1], True, pg.Color('white'))
    start_game_rect = start_game.get_rect()
    start_game_rect.top = logo_rect.bottom + 25
    start_game_rect.center = WIDTH // 2, start_game_rect.center[1]
    screen.blit(start_game, start_game_rect)

    options = text_font.render(intro_text[2], True, pg.Color('white'))
    options_rect = options.get_rect()
    options_rect.top = start_game_rect.bottom + 15
    options_rect.center = WIDTH // 2, options_rect.center[1]
    screen.blit(options, options_rect)

    quit_btn = text_font.render(intro_text[3], True, pg.Color('white'))
    quit_rect = quit_btn.get_rect()
    quit_rect.top = options_rect.bottom + 15
    quit_rect.center = WIDTH // 2, quit_rect.center[1]
    screen.blit(quit_btn, quit_rect)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN:
                if start_game_rect.left <= event.pos[0] <= start_game_rect.right and \
                        start_game_rect.top <= event.pos[1] <= start_game_rect.bottom:
                    return
                if options_rect.left <= event.pos[0] <= options_rect.right and \
                        options_rect.top <= event.pos[1] <= options_rect.bottom:
                    pass
                if quit_rect.left <= event.pos[0] <= quit_rect.right and \
                        quit_rect.top <= event.pos[1] <= quit_rect.bottom:
                    terminate()
        pg.display.flip()
        clock.tick(FPS)


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
            SmallExplosion(self.rect.center)


class AnimatedSprite(pg.sprite.Sprite):
    def __init__(self, x, y, sheet, columns, rows, framerate, *aux_groups):
        super().__init__(all_sprites, *aux_groups)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.framerate = framerate
        self.iteration = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pg.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pg.Rect(frame_location, self.rect.size)))

    def update(self):
        self.iteration += 1
        if self.iteration % (FPS // self.framerate) == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]


class BaseTank(AnimatedSprite):
    def __init__(self, pos_x, pos_y, sheet, columns, rows, framerate, *aux_groups):
        super().__init__(tile_width * pos_x + 1, tile_height * pos_y + 1,
                         sheet, columns, rows, framerate, top_layer_group, *aux_groups)
        self.direction = NORTH
        self.cooldown_duration = 500
        self.cooldown_start = -self.cooldown_duration

    def shoot(self):
        if self.alive():
            if pg.time.get_ticks() - self.cooldown_start >= self.cooldown_duration:
                dir_x, dir_y = convert_dir_to_x_y(self.direction)
                bullet_radius = max(bullet_image.get_width(), bullet_image.get_height()) // 2
                Bullet(self.rect.x + self.rect.width // 2 * (1 + dir_x) + bullet_radius * dir_x,
                       self.rect.y + self.rect.height // 2 * (1 + dir_y) + bullet_radius * dir_y,
                       self.__class__.__name__, self.direction)
                self.cooldown_start = pg.time.get_ticks()

    def set_cooldown(self, cooldown):
        self.cooldown_duration = cooldown

    def kill(self):
        super().kill()
        Explosion(self.rect.center)


class Player(BaseTank):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, player_sheet, 11, 1, 10, player_team)
        self.spawning_effect = None

    def update(self, dx, dy, direction):
        super().update()
        self.rect = self.rect.move(dx, dy)
        self.direction = direction
        self.image = pg.transform.rotate(self.frames[self.cur_frame], -90 * self.direction)
        if pg.sprite.spritecollideany(self, collidable_group) or pg.sprite.spritecollideany(self, enemy_team):
            self.rect = self.rect.move(-dx, -dy)

    def kill(self):
        super().kill()
        global player_lives
        player_lives -= 1
        if player_lives > 0:
            self.spawning_effect = SpawningEffect(tuple(map(lambda a: a * tile_width + 1, spawn_point)), 5000)
            pg.time.set_timer(PLAYER_RESPAWN, 5000, True)
        else:
            pg.event.post(game_over)

    def respawn(self):
        self.rect.x, self.rect.y = map(lambda a: a * tile_width + 1, spawn_point)
        self.direction = NORTH
        self.spawning_effect.kill()
        self.add(all_sprites, top_layer_group, player_team)


class Enemy(BaseTank):
    def __init__(self, pos_x, pos_y, velocity=1):
        super().__init__(pos_x, pos_y, enemy_sheet, 11, 1, 10, enemy_team)
        self.velocity = velocity
        self.dir_lock_start = -3000
        self.shoot_chance = 0.5

    def update(self):
        super().update()
        if self.rect.x % tile_width == 0 or self.rect.y % tile_height == 0:
            # ищем игрока; смотрит по всем сторонам когда по центру тайла; поле зрения - 5 тайлов
            for i in range(0, 4):
                ray = Ray(self.rect.center, self.rect.width, 5 * tile_width, (self.direction + i) % 4)
                if pg.sprite.spritecollideany(ray, aggressive_mode_check):
                    if pg.sprite.spritecollide(ray, aggressive_mode_check, False)[0] == player:
                        if random.random() < 0.75 / FPS:  # если нашли то с шансом 75% в сек движемся к игроку 3 секунды
                            self.direction = (self.direction + i) % 4
                            self.dir_lock_start = pg.time.get_ticks()
                            self.shoot_chance += 0.25
                            break

        dir_x, dir_y = convert_dir_to_x_y(self.direction)
        self.rect = self.rect.move(dir_x * self.velocity, dir_y * self.velocity)
        self.image = pg.transform.rotate(self.frames[self.cur_frame], -90 * self.direction)

        if self.dir_lock_start + 3000 < pg.time.get_ticks():
            if random.random() < 0.2 / FPS:  # с шансом 20% каждую секунду поворачивает
                self.direction = random.choice(list({0, 1, 2, 3} - {self.direction}))

        # при столкновении со стеной поворачивается в случайную сторону
        if pg.sprite.spritecollideany(self, collidable_group) or pg.sprite.spritecollideany(self, player_team) or \
                len(pg.sprite.spritecollide(self, enemy_team, False)) > 1:
            self.rect = self.rect.move(-dir_x * self.velocity, -dir_y * self.velocity)
            if self.dir_lock_start + 3000 < pg.time.get_ticks():
                self.direction = random.randrange(0, 4)
                self.image = pg.transform.rotate(self.frames[self.cur_frame], -90 * self.direction)
        if random.random() < self.shoot_chance / FPS:  # с шансом 50% каждую секунду стреляет
            self.shoot()


class Ray(pg.sprite.Sprite):
    def __init__(self, center, width, length, direction):
        super().__init__()
        self.direction = direction
        dir_x, dir_y = convert_dir_to_x_y(direction)
        if dir_y == 0:
            width, length = length, width
        self.rect = pg.Rect(0, 0, width, length)
        self.rect.center = center[0] + width / 2 * dir_x, center[1] + length / 2 * dir_y


class Explosion(AnimatedSprite):
    def __init__(self, center):
        super().__init__(0, 0, explosion_sheet, 11, 1, 20, top_layer_group, effects_group)
        self.rect.center = center

    def update(self):
        super().update()
        if self.iteration == len(self.frames) * (FPS // self.framerate):
            self.kill()  # при конце анимации умирает


class SmallExplosion(AnimatedSprite):
    def __init__(self, center):
        super().__init__(0, 0, small_explosion_sheet, 8, 1, 20, top_layer_group, effects_group)
        self.rect.center = center

    def update(self):
        super().update()
        if self.iteration == len(self.frames) * (FPS // self.framerate):
            self.kill()  # при конце анимации умирает


class SpawningEffect(AnimatedSprite):
    def __init__(self, coords, duration):
        super().__init__(coords[0], coords[1], spawning_eff_sheet, 2, 1, 4,
                         top_layer_group, effects_group, collidable_group)
        self.duration = duration

    def update(self):
        super().update()
        if self.iteration == int(self.duration / 1000 * FPS):
            self.kill()


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
            elif level[y][x] == 'E':
                Tile('empty', x, y)
                enemy_spawn_points.append((x, y))
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                spawn_point = (x, y)
    return new_player, x, y, spawn_point


if __name__ == "__main__":
    main_menu()

    enemy_count = 20
    enemy_respawn_time = 3100
    enemy_spawn_points = list()
    enemy_spawn_iteration = 0
    ENEMY_RESPAWN = pg.USEREVENT + 1
    enemy_respawn = pg.event.Event(ENEMY_RESPAWN)
    ENEMY_EFFECT_SPAWN = pg.USEREVENT + 2
    enemy_effect_spawn = pg.event.Event(ENEMY_EFFECT_SPAWN)
    PLAYER_RESPAWN = pg.USEREVENT + 3
    player_respawn = pg.event.Event(PLAYER_RESPAWN)
    GAME_OVER = pg.USEREVENT + 4
    game_over = pg.event.Event(GAME_OVER)
    player_lives = 3
    enemies_killed = 0

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
    player, level_x, level_y, spawn_point = generate_level(load_level('map0.txt'))

    aggressive_mode_check = collidable_group.copy()
    aggressive_mode_check.add(player)
    # camera = Camera((level_x, level_y))
    pg.time.set_timer(ENEMY_EFFECT_SPAWN, enemy_respawn_time, enemy_count)
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
            if event.type == PLAYER_RESPAWN:
                player.respawn()
            if event.type == ENEMY_EFFECT_SPAWN:
                SpawningEffect(tuple(map(lambda a: a * tile_width + 1, enemy_spawn_points[enemy_spawn_iteration %
                                                                                          len(enemy_spawn_points)])), 1000)
                pg.time.set_timer(ENEMY_RESPAWN, 1000, True)
            if event.type == ENEMY_RESPAWN:
                pos = enemy_spawn_points[enemy_spawn_iteration % len(enemy_spawn_points)]
                Enemy(pos[0], pos[1])
                enemy_spawn_iteration += 1
        screen.fill('black')
        # camera.update(player)
        # for sprite in all_sprites:
        #     camera.apply(sprite)
        bullet_group.update()
        effects_group.update()
        tiles_group.draw(screen)
        enemy_team.update()
        top_layer_group.draw(screen)
        pg.display.flip()
        clock.tick(FPS)
