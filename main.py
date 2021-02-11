import pygame as pg

pg.init()
pg.mixer.init()
size = WIDTH, HEIGHT = 608, 416
screen = pg.display.set_mode(size)
pg.key.set_repeat(10, 20)
pg.display.set_caption("Танчики")
clock = pg.time.Clock()

# сначала нужен pygame.init()
from menus import *
from tanks import *
from level import *
from effects import *


def terminate():
    pg.quit()
    sys.exit()


def default_options():
    options = {"up": pg.K_w,
               "down": pg.K_s,
               "left": pg.K_a,
               "right": pg.K_d,
               "shoot": pg.K_e}
    with open("options.json", 'w') as file:
        json.dump(options, file)


if __name__ == "__main__":
    if not os.path.isfile("options.json"):
        default_options()
    level_number = main_menu()
    with open("options.json", 'r') as options_file:
        options_dict = json.load(options_file)

    player, level_x, level_y, spawn_point = generate_level(load_level('map_' + str(level_number) + '.txt'))
    aggressive_mode_check = collidable_group.copy()
    aggressive_mode_check.add(player)
    pg.time.set_timer(ENEMY_EFFECT_SPAWN, enemy_respawn_time, enemy_count)
    player_lives = 3
    enemies_killed = 0
    game_over_flag = False
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    terminate()

                if event.key == options_dict["up"]:
                    player.update(0, -1, NORTH)
                if event.key == options_dict["right"]:
                    player.update(1, 0, EAST)
                if event.key == options_dict["down"]:
                    player.update(0, 1, SOUTH)
                if event.key == options_dict["left"]:
                    player.update(-1, 0, WEST)

                if event.key == options_dict["shoot"]:
                    player.shoot()
            if event.type == PLAYER_EFFECT_SPAWN:
                if player_lives > 0:
                    eff = SpawningEffect(tuple(map(lambda a: a * tile_width + 1, spawn_point)), 5000)
                    if not(pg.sprite.spritecollideany(eff, enemy_team) or
                           len(pg.sprite.spritecollide(eff, collidable_group, False)) > 1):
                        pg.time.set_timer(PLAYER_RESPAWN, 5000, True)
                    else:
                        eff.kill()
                        pg.time.set_timer(PLAYER_EFFECT_SPAWN, 250, True)
                else:
                    pg.time.set_timer(GAME_OVER, 1000, True)
            if event.type == PLAYER_RESPAWN:
                player.respawn()
            if event.type == PLAYER_KILLED:
                player_lives -= 1
                pg.event.post(player_effect_spawn)

            if event.type == ENEMY_EFFECT_SPAWN:
                if enemies_killed != enemy_count:
                    eff = SpawningEffect(tuple(map(lambda a: a * tile_width + 1,
                                                   enemy_spawn_points[enemy_spawn_iteration %
                                                                      len(enemy_spawn_points)])), 1000)
                    if not(pg.sprite.spritecollideany(eff, enemy_team) or pg.sprite.spritecollideany(eff, player_team) or
                           len(pg.sprite.spritecollide(eff, collidable_group, False)) > 1):
                        pg.time.set_timer(ENEMY_RESPAWN, 1000, True)
                    else:
                        eff.kill()
                else:
                    pg.time.set_timer(GAME_OVER, 1000, True)
            if event.type == ENEMY_RESPAWN:
                pos = enemy_spawn_points[enemy_spawn_iteration % len(enemy_spawn_points)]
                Enemy(pos[0], pos[1], aggressive_mode_check)
                enemy_spawn_iteration += 1
            if event.type == ENEMY_KILLED:
                enemies_killed += 1
                pg.event.post(enemy_effect_spawn)

            if event.type == GAME_OVER:
                game_over_flag = True
                running = False
                break
        screen.fill('black')
        bullet_group.update()
        effects_group.update()
        tiles_group.draw(screen)
        enemy_team.update()
        top_layer_group.draw(screen)
        pg.display.flip()
        clock.tick(FPS)
    if game_over_flag:
        game_over_screen(enemies_killed, player_lives, pg.time.get_ticks(), level_number)
