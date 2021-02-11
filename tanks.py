from init import *
import random
from math import sin, cos, radians
from base_sprites import AnimatedSprite
from effects import Explosion, SmallExplosion
# модуль с классами танков и всего с ними связанного


def convert_dir_to_x_y(direction):
    return int(sin(radians(direction * 90))), -int(cos(radians(direction * 90)))


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
                shooting_sound.play()

    def kill(self):
        super().kill()
        explosion_sound.play()
        Explosion(self.rect.center)


class Player(BaseTank):
    def __init__(self, pos_x, pos_y, spawn_point):
        super().__init__(pos_x, pos_y, player_sheet, 11, 1, 10, player_team)
        self.spawn_point = spawn_point

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
            pg.event.post(player_effect_spawn)
        else:
            pg.time.set_timer(GAME_OVER, 1000, True)

    def respawn(self):
        self.rect.x, self.rect.y = map(lambda a: a * tile_width + 1, self.spawn_point)
        self.direction = NORTH
        self.add(all_sprites, top_layer_group, player_team)


class Enemy(BaseTank):
    def __init__(self, pos_x, pos_y, aggressive_mode_check, velocity=1):
        super().__init__(pos_x, pos_y, enemy_sheet, 11, 1, 10, enemy_team)
        self.velocity = velocity
        self.dir_lock_start = -3000
        self.shoot_chance = 0.5
        self.aggr_mode_check = aggressive_mode_check

    def update(self):
        super().update()
        if self.rect.x % tile_width == 0 or self.rect.y % tile_height == 0:
            # ищем игрока; смотрит по всем сторонам когда по центру тайла; поле зрения - 5 тайлов
            for i in range(0, 4):
                ray = Ray(self.rect.center, self.rect.width, 5 * tile_width, (self.direction + i) % 4)
                if pg.sprite.spritecollideany(ray, self.aggr_mode_check):
                    first_sprite = pg.sprite.spritecollide(ray, self.aggr_mode_check, False)[0]
                    if first_sprite.__class__ == Player and first_sprite.alive():
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


class Bullet(pg.sprite.Sprite):
    def __init__(self, center_x, center_y, owner_name, direction, velocity=3):
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
        elif pg.sprite.spritecollideany(self, collidable_group):
            self.kill()
            bump_sound.play()
            SmallExplosion(self.rect.center)
