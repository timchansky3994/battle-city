from init import *
from main import screen, clock, terminate
import json
# модуль с меню


def main_menu():
    intro_text = ["BATTLE CITY",
                  "Начать игру",
                  "Управление",
                  "Выйти"]

    background = pg.transform.scale(load_image('background.jpg'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    logo_font = pg.font.Font("data/fonts/docktrin.ttf", 89)
    text_font = pg.font.Font("data/fonts/rockwellnova.ttf", 36)

    logo = logo_font.render(intro_text[0], True, pg.Color('white'))
    logo_rect = logo.get_rect()
    logo_rect.top = 80
    logo_rect.center = WIDTH // 2, logo_rect.center[1]
    screen.blit(logo, logo_rect)

    start_game = text_font.render(intro_text[1], True, pg.Color('white'), (30, 30, 30))
    start_game_rect = start_game.get_rect()
    start_game_rect.top = logo_rect.bottom + 25
    start_game_rect.center = WIDTH // 2, start_game_rect.center[1]
    screen.blit(start_game, start_game_rect)

    options = text_font.render(intro_text[2], True, pg.Color('white'), (30, 30, 30))
    options_rect = options.get_rect()
    options_rect.top = start_game_rect.bottom + 15
    options_rect.center = WIDTH // 2, options_rect.center[1]
    screen.blit(options, options_rect)

    quit_btn = text_font.render(intro_text[3], True, pg.Color('white'), (30, 30, 30))
    quit_rect = quit_btn.get_rect()
    quit_rect.top = options_rect.bottom + 15
    quit_rect.center = WIDTH // 2, quit_rect.center[1]
    screen.blit(quit_btn, quit_rect)

    options_clicked = True
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
                    options_clicked = True
                    break
                if quit_rect.left <= event.pos[0] <= quit_rect.right and \
                        quit_rect.top <= event.pos[1] <= quit_rect.bottom:
                    terminate()
        pg.display.flip()
        clock.tick(FPS)
    if options_clicked:
        options_menu()


def options_menu():
    options = ["Вверх",
               "Вниз",
               "Влево",
               "Вправо",
               "Выстрелить"]
    options_names = ["up",
                     "down",
                     "left",
                     "right",
                     "shoot"]

    background = pg.transform.scale(load_image('background.jpg'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    text_font = pg.font.Font("data/fonts/rockwellnova.ttf", 36)

    title = text_font.render("Управление", True, pg.Color('white'))
    title_rect = title.get_rect()
    title_rect.top = 10
    title_rect.center = WIDTH // 2, title_rect.center[1]
    screen.blit(title, title_rect)

    back_btn = text_font.render("< Назад", True, pg.Color('white'), (30, 30, 30))
    back_btn_rect = title.get_rect()
    back_btn_rect.top, back_btn_rect.left = 10, 10
    screen.blit(back_btn, back_btn_rect)

    save_btn = text_font.render("Сохранить", True, pg.Color('white'), (30, 30, 30))
    save_btn_rect = title.get_rect()
    save_btn_rect.bottom = HEIGHT - 10
    save_btn_rect.center = WIDTH // 2, save_btn_rect.center[1]
    screen.blit(save_btn, save_btn_rect)

    click_areas = list()
    with open("options.json", 'r') as opt_file:
        bindings = json.load(opt_file)
    for i, line in enumerate(options):
        name = text_font.render(line, True, pg.Color('white'))
        name_rect = name.get_rect()
        name_rect.right = WIDTH // 2 - 30
        name_rect.center = name_rect.center[0], (save_btn_rect.top - title_rect.bottom) // \
                           (len(options) + 1) * (i + 1) + title_rect.bottom
        screen.blit(name, name_rect)

        click_areas.append(pg.rect.Rect(WIDTH // 2 + 30, name_rect.top, WIDTH // 2 - 60, name_rect.height))
        screen.fill((30, 30, 30), click_areas[i])
        binding = text_font.render(pg.key.name(bindings[options_names[i]]), True, pg.Color('white'))
        binding_rect = binding.get_rect()
        binding_rect.left, binding_rect.top = click_areas[i].left, click_areas[i].top
        screen.blit(binding, binding_rect)

    back_btn_pressed = False
    set_binding = None
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN:
                if back_btn_rect.left <= event.pos[0] <= back_btn_rect.right and \
                        back_btn_rect.top <= event.pos[1] <= back_btn_rect.bottom:
                    back_btn_pressed = True
                    break
                else:
                    for i, area in enumerate(click_areas):
                        if area.left <= event.pos[0] <= area.right and area.top <= event.pos[1] <= area.bottom:
                            set_binding = i
                if save_btn_rect.left <= event.pos[0] <= save_btn_rect.right and \
                        save_btn_rect.top <= event.pos[1] <= save_btn_rect.bottom:
                    with open("options.json", 'w') as opt_file:
                        json.dump(bindings, opt_file)
            if set_binding is not None and event.type == pg.KEYDOWN:
                bindings[options_names[set_binding]] = event.key
                screen.fill((30, 30, 30), click_areas[set_binding])
                binding = text_font.render(pg.key.name(bindings[options_names[set_binding]]), True, pg.Color('white'))
                binding_rect = binding.get_rect()
                binding_rect.left, binding_rect.top = click_areas[set_binding].left, click_areas[set_binding].top
                screen.blit(binding, binding_rect)
        pg.display.flip()
        clock.tick(FPS)
    if back_btn_pressed:
        main_menu()
