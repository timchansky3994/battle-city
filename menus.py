from init import *
from main import screen, clock, terminate
import json
# модуль с меню

level_number = None


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
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN:
                if start_game_rect.left <= event.pos[0] <= start_game_rect.right and \
                        start_game_rect.top <= event.pos[1] <= start_game_rect.bottom:
                    global level_number
                    level_number = level_select()
                    return
                if options_rect.left <= event.pos[0] <= options_rect.right and \
                        options_rect.top <= event.pos[1] <= options_rect.bottom:
                    options_clicked = True
                    running = False
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
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN:
                if back_btn_rect.left <= event.pos[0] <= back_btn_rect.right and \
                        back_btn_rect.top <= event.pos[1] <= back_btn_rect.bottom:
                    back_btn_pressed = True
                    running = False
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


def game_over_screen(amount_killed, lives_left, time, level_number):
    background = pg.transform.scale(load_image('background.jpg'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    title_font = pg.font.Font("data/fonts/docktrin.ttf", 56)
    text_font = pg.font.Font("data/fonts/rockwellnova.ttf", 24)
    
    title = title_font.render("Game Over", True, pg.Color('white'))
    title_rect = title.get_rect()
    title_rect.top = 10
    title_rect.center = WIDTH // 2, title_rect.center[1]
    screen.blit(title, title_rect)

    back_btn = text_font.render("В меню", True, pg.Color('white'), (30, 30, 30))
    back_btn_rect = title.get_rect()
    back_btn_rect.top, back_btn_rect.left = 10, 10
    screen.blit(back_btn, back_btn_rect)

    if not os.path.isfile("highscores.json"):
        highscores = [0, 0]
    else:
        with open("highscores.json", 'r') as file:
            highscores = json.load(file)
    highscore = highscores[level_number]
    kills_score, lives_score, time_score = amount_killed * 100, lives_left * 500, int((5 * 60000 - time) * 0.01)
    if time_score < 0 or lives_left <= 0:
        time_score = 0
    lines = [f"Прошлый рекорд: {highscore}",
             f"Очки за убийства: {kills_score}",
             f"Очки за ост. жизни: {lives_score}",
             f"Очки за время: {time_score}",
             f"Всего: {kills_score + lives_score + time_score}"]
    new_highscore = kills_score + lives_score + time_score
    if new_highscore > highscore:
        lines.append("Новый рекорд!")
        highscores[level_number] = new_highscore
        with open("highscores.json", 'w') as file:
            json.dump(highscores, file)

    for i, line in enumerate(lines):
        name = text_font.render(line, True, pg.Color('white'))
        name_rect = name.get_rect()
        name_rect.center = WIDTH // 2, (HEIGHT - title_rect.bottom) // \
            (len(lines) + 1) * (i + 1) + title_rect.bottom
        screen.blit(name, name_rect)
    back_btn_pressed = False
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN:
                if back_btn_rect.left <= event.pos[0] <= back_btn_rect.right and \
                        back_btn_rect.top <= event.pos[1] <= back_btn_rect.bottom:
                    back_btn_pressed = True
                    running = False
                    break
        pg.display.flip()
        clock.tick(FPS)
    if back_btn_pressed:
        main_menu()


def level_select():
    background = pg.transform.scale(load_image('background.jpg'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    title_font = pg.font.Font("data/fonts/docktrin.ttf", 48)
    text_font = pg.font.Font("data/fonts/rockwellnova.ttf", 36)
    
    title = title_font.render("level select", True, pg.Color('white'))
    title_rect = title.get_rect()
    title_rect.top = 10
    title_rect.center = WIDTH // 2, title_rect.center[1]
    screen.blit(title, title_rect)
    
    back_btn = text_font.render("< Назад", True, pg.Color('white'), (30, 30, 30))
    back_btn_rect = title.get_rect()
    back_btn_rect.top, back_btn_rect.left = 10, 10
    screen.blit(back_btn, back_btn_rect)
    
    btn1 = pg.Rect(75, title_rect.bottom + 15, 100, 100)
    screen.fill((30, 30, 30), btn1)
    btn1_text = text_font.render("1", True, pg.Color('white'))
    btn1_rect = btn1_text.get_rect()
    btn1_rect.center = btn1.center
    screen.blit(btn1_text, btn1_rect)
    btn2 = pg.Rect(75, title_rect.bottom + 15, 100, 100)
    btn2.right = WIDTH - 75
    screen.fill((30, 30, 30), btn2)
    btn2_text = text_font.render("2", True, pg.Color('white'))
    btn2_rect = btn2_text.get_rect()
    btn2_rect.center = btn2.center
    screen.blit(btn2_text, btn2_rect)
    
    back_btn_pressed = False
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN:
                if back_btn_rect.left <= event.pos[0] <= back_btn_rect.right and \
                        back_btn_rect.top <= event.pos[1] <= back_btn_rect.bottom:
                    back_btn_pressed = True
                    running = False
                    break
                if btn1.left <= event.pos[0] <= btn1.right and \
                        btn1.top <= event.pos[1] <= btn1.bottom:
                    return 0
                if btn2.left <= event.pos[0] <= btn2.right and \
                        btn2.top <= event.pos[1] <= btn2.bottom:
                    return 1
        pg.display.flip()
        clock.tick(FPS)
    if back_btn_pressed:
        main_menu()
