import os
import sys
import random
import pygame
import sqlite3

con = sqlite3.connect("data/si_db.sql")

cur = con.cursor()

pygame.init()
pygame.mixer.init()
size = width, height = 600, 400
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Space Invaders')
fps = 30  # FPS
speed_move = 180  # Скорость передвижения игрока
speed_bullet = 400  # Скорость пули игрока
clock = pygame.time.Clock()
bullet_status = 0  # 1 - пуля игрока существует и летит, 0 - пули игрока нет
enemy_direction = 1  # Направление передвижения врага (1 - вправо, -1 - влево)
enemy_speed = 0.50  # Скорость передвижения врага
start_enemy_speed = 0.50  # Скорость передвижения врага согласно сложности игры
max_enemy_speed = 1  # Максимальная скорость передвижения врага
max_give_enemy_speed = 0.02  # Максимальное значение которое выдается к скорости передвижения врага
score = 0  # Очки
total_time = 120  # Таймер
delta_time = 0  # Переменная для хранения времени между кадрами (в секундах)
start_ticks = pygame.time.get_ticks()  # Начальное время для таймера
enemy_speed_bullet = 150  # Скорость пули врага
chance_shot_enemy = 30  # С каким шансом враги будут стрелять
chance_powerup = 10  # С каким шансом будет выпадать повер-ап из противников
shield_status = 0  # Определяет, есть ли у игрока щит
god_status = 0  # Определяет, есть ли у игрока неуязвимость
god_status_again = 1  # Определяет, есть ли у игрока повторная неуязвимость
frame_shot = 30  # Сколько кадров должно пройти, чтобы была произведена попытка выстрела
level = cur.execute("""SELECT level FROM settings""").fetchall()[0][0]  # Уровень по-умолчанию
god_status_one_time = 0
power_up_sound = pygame.mixer.Sound('data/pu_sound_1.mp3')
bullet_sound_player = pygame.mixer.Sound('data/shot_sound_2.mp3')
explosion_sound = pygame.mixer.Sound('data/explosion_2.mp3')  # звук взрыва
running = True

player_group = pygame.sprite.Group()  # Группа спрайтов с игроком
bullet_group = pygame.sprite.Group()  # Группа спрайтов с пулей игрока
bullet_group_enemy = pygame.sprite.Group()  # Группа спрайтов с пулями врагов
enemy_group = pygame.sprite.Group()  # Группа спрайтов с врагами
explosion_group = pygame.sprite.Group()  # Группа спрайтов с взрывами
powerup_group = pygame.sprite.Group()  # Группа спрайтов с повер-ап'ами


def load_image(name, colorkey=None):  # Функция загрузки изображения
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


# space_background_game


def draw_score_and_timer():  # Отображение очков и таймера
    global score
    elapsed_time = (pygame.time.get_ticks() - start_ticks) // 1000  # Время в секундах
    remaining_time = total_time - elapsed_time
    if remaining_time < 0:
        remaining_time = 0
    minutes = remaining_time // 60
    seconds = remaining_time % 60
    timer_text = f"Время: {minutes:02}:{seconds:02}"
    score_text = f"Очки: {score}"
    font = pygame.font.Font(None, 36)
    timer_surface = font.render(timer_text, True, (255, 255, 255))
    score_surface = font.render(score_text, True, (255, 255, 255))
    screen.blit(timer_surface, (10, 10))  # Позиция таймера
    screen.blit(score_surface, (10, 40))  # Позиция счета


class Menu:  # Меню
    def __init__(self):
        pygame.mixer.music.load('data/menu_sound.mp3')  # Музыка для главного меню
        pygame.mixer.music.set_volume(0.5)  # Установка громкости (от 0.0 до 1.0)
        pygame.mixer.music.play(-1)  # Воспроизведение музыки в цикле# Музыка для главного меню
        self.font = pygame.font.Font(None, 74)  # Шрифт
        self.font_small = pygame.font.Font(None, 36)  # Шрифт маленький
        self.difficulties = ["easy", "medium", "hard"]  # Список сложностей игры
        self.current_difficulty_index = cur.execute("""SELECT difficulty FROM settings""").fetchall()[0][
            0]  # Сложность игры
        self.sound_volume = cur.execute("""SELECT volume FROM settings""").fetchall()[0][0]  # Громкость звука

    def draw(self):
        global enemy_speed_bullet, enemy_speed, chance_shot_enemy, max_give_enemy_speed, max_enemy_speed, sound_volume, start_enemy_speed
        screen.fill((0, 0, 0))
        background = pygame.transform.scale(load_image("space_background.jpg"), (800, 400))  # Фон
        screen.blit(background, (-100, 0))
        title = self.font.render("Space Invaders", True, (255, 255, 255))
        start_button = self.font_small.render("Новая игра", True, (255, 255, 255))
        continue_button = self.font_small.render("Продолжить", True, (255, 255, 255))
        exit_button = self.font_small.render("Выход", True, (255, 255, 255))
        score_text = self.font_small.render(
            f"Всего очков: {cur.execute('SELECT score_all FROM settings').fetchall()[0][0]}", True, (255, 255, 255))
        if level != 4:
            level_text = self.font_small.render(
                f"Текущий уровень: {cur.execute('SELECT level FROM settings').fetchall()[0][0]}", True, (255, 255, 255))
        else:
            level_text = self.font_small.render(
                f"Текущий уровень: {cur.execute('SELECT level FROM settings').fetchall()[0][0] - 1}", True,
                (255, 255, 255))
        difficulty_text = self.font_small.render(f"Сложность: {self.difficulties[self.current_difficulty_index]}",
                                                 True,
                                                 (255, 255, 255))
        sound_on_button = load_image("sound-on.png")
        sound_off_button = load_image("sound-off.png")
        if self.sound_volume:
            sound_button = pygame.transform.scale(sound_on_button, (30, 30))
        else:
            sound_button = pygame.transform.scale(sound_off_button, (30, 30))
        screen.blit(sound_button, (width - 40, height - 40))
        sound_button_rect = sound_button.get_rect(x=width - 40, y=height - 40)
        if self.difficulties[self.current_difficulty_index] == 'medium':
            enemy_speed_bullet = 200
            chance_shot_enemy = 50
            enemy_speed = 0.80
            start_enemy_speed = 0.80
            max_give_enemy_speed = 0.04
            max_enemy_speed = 1.3
        elif self.difficulties[self.current_difficulty_index] == 'hard':
            enemy_speed_bullet = 250
            chance_shot_enemy = 70
            enemy_speed = 1.10
            start_enemy_speed = 1.10
            max_give_enemy_speed = 0.06
            max_enemy_speed = 1.6
        else:
            enemy_speed_bullet = 150
            chance_shot_enemy = 30
            enemy_speed = 0.50
            start_enemy_speed = 0.50
            max_give_enemy_speed = 0.02
            max_enemy_speed = 1
        if self.sound_volume:
            explosion_sound.set_volume(1.0)
            bullet_sound_player.set_volume(1.0)
            power_up_sound.set_volume(1.0)
            pygame.mixer.music.set_volume(0.5)
        else:
            explosion_sound.set_volume(0.0)
            bullet_sound_player.set_volume(0.0)
            power_up_sound.set_volume(0.0)
            pygame.mixer.music.set_volume(0.0)
        cur.execute(f"""UPDATE settings SET difficulty = {self.current_difficulty_index}""")
        cur.execute(f"""UPDATE settings SET volume = {self.sound_volume}""")
        con.commit()
        if level != 1 and level < 4:
            continue_button_rect = continue_button.get_rect(center=(width // 2, height // 2))
            start_button_rect = start_button.get_rect(center=(width // 2, height // 2 + 50))
            exit_button_rect = exit_button.get_rect(center=(width // 2, height // 2 + 100))
            difficulty_text_rect = difficulty_text.get_rect(x=width // 2 - difficulty_text.get_width() // 2,
                                                            y=height // 2 + 150)
        else:
            continue_button_rect = continue_button.get_rect(center=(-100, -100))
            start_button_rect = start_button.get_rect(center=(width // 2, height // 2))
            exit_button_rect = exit_button.get_rect(center=(width // 2, height // 2 + 50))
            difficulty_text_rect = difficulty_text.get_rect(x=width // 2 - difficulty_text.get_width() // 2,
                                                            y=height // 2 + 100)

        screen.blit(title, (width // 2 - title.get_width() // 2, height // 4))
        screen.blit(score_text, (width // 2 - score_text.get_width() // 2, height // 9))
        screen.blit(start_button, start_button_rect)
        screen.blit(continue_button, continue_button_rect)
        screen.blit(exit_button, exit_button_rect)
        screen.blit(difficulty_text, difficulty_text_rect)
        screen.blit(level_text, (width // 2 - level_text.get_width() // 2, height // 3 + 20))

        left_arrow = self.font_small.render("<", True, (255, 255, 255))
        right_arrow = self.font_small.render(">", True, (255, 255, 255))
        left_arrow_rect = left_arrow.get_rect(x=150, y=difficulty_text_rect.y)
        right_arrow_rect = right_arrow.get_rect(x=430, y=difficulty_text_rect.y)
        screen.blit(left_arrow, left_arrow_rect)
        screen.blit(right_arrow, right_arrow_rect)

        return start_button_rect, exit_button_rect, left_arrow_rect, right_arrow_rect, sound_button_rect, continue_button_rect

    def run(self):
        global running, level
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if start_button_rect.collidepoint(mouse_pos):
                        level = 1
                        cur.execute("""UPDATE settings SET score_all = 0""")
                        cur.execute(f"""UPDATE settings SET level = {level}""")
                        con.commit()
                        return
                    if continue_button_rect.collidepoint(mouse_pos):
                        return
                    if exit_button_rect.collidepoint(mouse_pos):
                        running = False
                    if left_arrow_rect.collidepoint(mouse_pos):
                        self.current_difficulty_index = (self.current_difficulty_index - 1) % len(self.difficulties)
                    if right_arrow_rect.collidepoint(mouse_pos):
                        self.current_difficulty_index = (self.current_difficulty_index + 1) % len(self.difficulties)
                    if sound_button_rect.collidepoint(mouse_pos):
                        if not self.sound_volume:
                            self.sound_volume = 1
                        else:
                            self.sound_volume = 0

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.current_difficulty_index = (self.current_difficulty_index + 1) % len(self.difficulties)
                    elif event.key == pygame.K_DOWN:
                        self.current_difficulty_index = (self.current_difficulty_index - 1) % len(self.difficulties)
                    elif event.key == pygame.K_LEFT:
                        self.current_difficulty_index = (self.current_difficulty_index - 1) % len(self.difficulties)
                    elif event.key == pygame.K_RIGHT:
                        self.current_difficulty_index = (self.current_difficulty_index + 1) % len(self.difficulties)

            start_button_rect, exit_button_rect, left_arrow_rect, right_arrow_rect, sound_button_rect, continue_button_rect = self.draw()
            pygame.display.flip()
            clock.tick(fps)


def show_end_screen(final_score):  # Окно по завершению уровня
    global level  # Добавляем уровень в глобальные переменные
    screen_fade = pygame.Surface((600, 400))
    screen_fade.fill((0, 0, 0))
    screen_fade.set_alpha(160)
    screen.blit(screen_fade, (0, 0))
    # screen.fill((0, 0, 0))  # Заполняем экран черным цветом (или можно использовать фон)

    font = pygame.font.Font(None, 74)
    text = font.render("Уровень завершен!", True, (255, 255, 255))
    score_text = font.render(f"Ваши очки: {final_score}", True, (255, 255, 255))
    continue_button = font.render("Продолжить", True, (255, 255, 255))
    main_menu_button = font.render("Главное меню", True, (255, 255, 255))

    level += 1  # Увеличиваем уровень
    cur.execute(f"""UPDATE settings SET level = {level}""")
    con.commit()

    if level != 4:
        screen.blit(score_text, (width // 2 - score_text.get_width() // 2, height // 2 - 25))
        # Изменяем позицию кнопки "Продолжить"
        continue_button_rect = continue_button.get_rect(center=(width // 2, height // 2 + 85))
        main_menu_button_rect = main_menu_button.get_rect(center=(width // 2, height // 2 + 150))
    else:
        text = font.render("Вы прошли все уровни!", True, (255, 255, 255))
        screen.blit(score_text, (width // 2 - score_text.get_width() // 2, height // 2))
        # Изменяем позицию кнопки "Продолжить"
        continue_button_rect = continue_button.get_rect(center=(-100, -100))
        main_menu_button_rect = main_menu_button.get_rect(center=(width // 2, height // 2 + 100))
    screen.blit(text, (width // 2 - text.get_width() // 2, height // 4))
    screen.blit(main_menu_button, main_menu_button_rect)
    screen.blit(continue_button, continue_button_rect)

    pygame.display.flip()  # Обновляем экран
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if continue_button_rect.collidepoint(mouse_pos):
                    initialize_next_level()  # Вызов функции для инициализации следующего уровня
                    return  # Возвращаемся, чтобы выйти из функции и очистить экран
                if main_menu_button_rect.collidepoint(mouse_pos):
                    initialize_next_level()
                    Menu().run()  # Вызов функции для перехода в главное меню
                    return  # Возвращаемся, чтобы выйти из функции


def show_death_screen():  # Окно после смерти игрока
    screen_fade = pygame.Surface((600, 400))
    screen_fade.fill((0, 0, 0))
    screen_fade.set_alpha(160)
    screen.blit(screen_fade, (0, 0))
    # screen.fill((0, 0, 0))  # Заполняем экран черным цветом (или можно использовать фон)

    font = pygame.font.Font(None, 74)
    text = font.render("Вы умерли!", True, (255, 255, 255))
    start_again_button = font.render("Начать заново", True, (255, 255, 255))
    main_menu_button = font.render("Главное меню", True, (255, 255, 255))

    screen.blit(text, (width // 2 - text.get_width() // 2, height // 4))
    start_again_button_rect = start_again_button.get_rect(center=(width // 2, height // 2 + 85))
    main_menu_button_rect = main_menu_button.get_rect(center=(width // 2, height // 2 + 150))
    screen.blit(main_menu_button, main_menu_button_rect)
    screen.blit(start_again_button, start_again_button_rect)

    pygame.display.flip()  # Обновляем экран
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_again_button_rect.collidepoint(mouse_pos):
                    initialize_next_level()  # Вызов функции для инициализации следующего уровня
                    Player()
                    if level == 1:  # Первый уровень
                        level_one()
                    elif level == 2:  # второй уровень
                        level_two()
                    elif level == 3:  # второй уровень
                        level_three()
                    return  # Возвращаемся, чтобы выйти из функции и очистить экран
                if main_menu_button_rect.collidepoint(mouse_pos):
                    initialize_next_level()
                    Menu().run()  # Вызов функции для перехода в главное меню
                    return  # Возвращаемся, чтобы выйти из функции


class Player(pygame.sprite.Sprite):  # Игрок
    image = load_image("ship.png")

    def __init__(self):
        super().__init__(player_group)
        self.frames = []
        self.cut_sheet(Player.image, 5, 2)
        self.if_num = 0
        self.cur_frame = 0
        self.image = pygame.transform.scale(self.frames[self.cur_frame], (32, 48))
        self.rect = self.image.get_rect()
        self.rect.x = width // 2 - self.rect.w // 2
        self.rect.y = 0.9 * height - self.rect.h // 2
        self.total_time = 5

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if self.if_num == 5:
            self.if_num = 0
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.cur_frame], (32, 48))
        self.if_num += 1
        global bullet_status, god_status, god_status_again, screen, god_status_one_time
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            if not bullet_status:
                Bullet()
                bullet_status = 1
        if pygame.key.get_pressed()[pygame.K_LEFT] and self.rect.x > width * 0.03:
            self.rect.x -= speed_move / fps
        if pygame.key.get_pressed()[pygame.K_RIGHT] and self.rect.x + self.rect.w < (width * 0.97):
            self.rect.x += speed_move / fps
        if pygame.sprite.spritecollideany(self, bullet_group_enemy):
            if not god_status:
                Explosion(self.rect.x, self.rect.y, self.rect.w, self.rect.h)
                for bullet_enemy in bullet_group_enemy:
                    if pygame.sprite.collide_rect(bullet_enemy, list(player_group)[0]):
                        explosion_sound.play()  # Воспроизведение звука взрыва
                        bullet_enemy.kill()
                self.kill()
                show_death_screen()
            else:
                for bullet_enemy in bullet_group_enemy:
                    if pygame.sprite.collide_rect(bullet_enemy, list(player_group)[0]):
                        explosion_sound.play()  # Воспроизведение звука взрыва
                        bullet_enemy.kill()

        if god_status:
            if god_status_again:
                power_up_sound.play()
                self.start_ticks = pygame.time.get_ticks()
                god_status_again = 0
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) // 1000  # Время в секундах
            self.remaining_time = self.total_time - self.elapsed_time
            if self.remaining_time < 0:
                self.remaining_time = 0
                god_status = 0
            self.timer_text = f"Неуязвимость: 00:0{self.remaining_time}"
            self.font = pygame.font.Font(None, 36)
            self.timer_surface = self.font.render(self.timer_text, True, (255, 255, 255))
            self.timer_surface_rect = self.timer_surface.get_rect()
            screen.blit(self.timer_surface, (width - 10 - self.timer_surface_rect.w, 10))  # Позиция таймера


class Shield(pygame.sprite.Sprite):
    image = load_image("shield.png")

    def __init__(self):
        super().__init__(player_group)
        self.image = pygame.transform.scale(Shield.image, (70, 70))
        self.rect = self.image.get_rect()
        self.rect.center = list(player_group)[0].rect.center
        power_up_sound.play()  # Воспроизведение звука взрыва

    def update(self):
        global shield_status
        shield_status = 1
        self.rect.center = list(player_group)[0].rect.center
        if pygame.sprite.spritecollideany(self, bullet_group_enemy):
            shield_status = 0
            for bullet_enemy in bullet_group_enemy:
                if pygame.sprite.collide_rect(bullet_enemy, list(player_group)[1]):
                    bullet_enemy.kill()
            self.kill()


class Bullet(pygame.sprite.Sprite):  # Пуля игрока
    image = load_image("laser-bolts.png")

    def __init__(self):
        super().__init__(bullet_group)
        self.image = pygame.transform.scale(Bullet.image, (10, 24))
        self.rect = self.image.get_rect()
        self.rect.x = (list(player_group)[0].rect.x
                       + list(player_group)[0].rect.w // 2 - list(bullet_group)[0].rect.w // 2)
        self.rect.y = list(player_group)[0].rect.y - self.rect.h
        bullet_sound_player.play()  # Воспроизведение звука пули

    def update(self):
        global bullet_status
        self.rect.y -= speed_bullet / fps
        if self.rect.y + self.rect.h < 0:
            explosion_sound.play()  # Воспроизведение звука взрыва
            bullet_status = 0
            self.kill()


class Enemy_Bullet(pygame.sprite.Sprite):  # Пуля врага
    image = load_image("laser-bolts.png")

    def __init__(self, x, y):
        super().__init__(bullet_group_enemy)
        self.image = pygame.transform.rotate(pygame.transform.scale(Enemy_Bullet.image, (10, 24)), 180)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.voice = pygame.mixer.Channel(2)
        self.voice.play(bullet_sound_player)

    def update(self):
        global bullet_status
        self.rect.y += enemy_speed_bullet / fps
        if self.rect.y > height:
            self.kill()
        if pygame.sprite.spritecollideany(self, bullet_group):
            Explosion(list(bullet_group)[0].rect.x, list(bullet_group)[0].rect.y, list(bullet_group)[0].rect.w,
                      list(bullet_group)[0].rect.h)
            self.kill()
            bullet_status = 0
            list(bullet_group)[0].kill()


class Enemy(pygame.sprite.Sprite):  # Враг (шаблон)
    def __init__(self, x, y, image, width, height, score_values):
        super().__init__(enemy_group)
        self.frames = []
        self.cut_sheet(image, 2, 1)
        self.cur_frame = 0
        self.if_num = 0
        self.if_num_bullet = 0
        self.image = pygame.transform.scale(self.frames[self.cur_frame], (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.score_values = score_values

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def is_path_clear(self):
        for enemy in enemy_group:
            if abs(enemy.rect.x - self.rect.x) < self.rect.width and enemy.rect.y > self.rect.y:
                return False
        return True

    def update(self):
        global frame_shot, bullet_status, score, enemy_speed
        if self.if_num_bullet == frame_shot:
            self.if_num_bullet = 0
            if random.randint(1, 100) <= chance_shot_enemy and self.is_path_clear():
                Enemy_Bullet(self.rect.x + self.rect.w // 2 - 5 // 2, self.rect.y + self.rect.h)
        if self.if_num == 5:
            self.if_num = 0
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.cur_frame], self.image.get_size())
        self.if_num += 1
        self.if_num_bullet += 1
        if pygame.sprite.spritecollideany(self, bullet_group):
            explosion_sound.play()  # Воспроизведение звука взрыва
            if random.randint(1, 100) <= chance_powerup:
                PowerUp(self.rect.x + self.rect.w // 2 - 16 // 2, self.rect.y + self.rect.h // 2 - 16 // 2)
            Explosion(self.rect.x, self.rect.y, self.rect.w, self.rect.h)
            self.kill()
            list(bullet_group)[0].kill()
            bullet_status = 0
            for threshold, points in self.score_values:
                if self.rect.y <= threshold:
                    score += points
                    break
            if enemy_speed < max_enemy_speed:
                enemy_speed += max_give_enemy_speed
        if pygame.sprite.spritecollideany(self, player_group):
            list(player_group)[0].kill()
            show_death_screen()


class Enemy_Red(Enemy):  # Враг Большой
    image = load_image("enemy-big.png")

    def __init__(self, x, y):
        super().__init__(x, y, Enemy_Red.image, 52, 64, [(60, 200), (float('inf'), 100)])


class Enemy_Yellow(Enemy):  # Враг Средний
    image = load_image("enemy-medium.png")

    def __init__(self, x, y):
        super().__init__(x, y, Enemy_Yellow.image, 48, 24, [(60, 200), (100, 100), (200, 70)])


class Enemy_Green(Enemy):  # Враг Маленький
    image = load_image("enemy-small.png")

    def __init__(self, x, y):
        super().__init__(x, y, Enemy_Green.image, 32, 32, [(60, 200), (100, 100), (200, 70)])


class Explosion(pygame.sprite.Sprite):  # Взрыв
    image = load_image("explosion.png")

    def __init__(self, x, y, x_size, y_size):
        super().__init__(explosion_group)
        self.frames = []
        self.cut_sheet(Explosion.image, 5, 1)
        self.cur_frame = 0
        self.if_num = 0
        self.y_size = y_size
        self.image = pygame.transform.scale(self.frames[self.cur_frame], (self.y_size, self.y_size))
        self.rect = self.image.get_rect()
        self.rect.x = x - y_size // 2 + x_size // 2
        self.rect.y = y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if self.if_num == 3:
            self.if_num = 0
            self.cur_frame += 1
            if self.cur_frame == 5:
                self.kill()
            else:
                self.image = pygame.transform.scale(self.frames[self.cur_frame], (self.y_size, self.y_size))
        self.if_num += 1


class PowerUp(pygame.sprite.Sprite):
    image = load_image("power-up.png")

    def __init__(self, x, y):
        super().__init__(powerup_group)
        self.type_powerup = random.randint(1, 2)
        self.frames = []
        self.cut_sheet(PowerUp.image, 2, self.type_powerup)
        self.cur_frame = 0
        self.if_num = 0
        self.image = pygame.transform.scale(self.frames[self.cur_frame], (16, 16))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // 2)
        for i in range(columns):
            frame_location = (self.rect.w * i, self.rect.h * (rows - 1))
            self.frames.append(sheet.subsurface(pygame.Rect(
                frame_location, self.rect.size)))

    def update(self):
        global shield_status, god_status, god_status_again
        if self.rect.y > height:
            self.kill()
        if self.if_num == 5:
            self.if_num = 0
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.cur_frame], self.image.get_size())
        self.if_num += 1
        self.rect.y += int(1 * delta_time * 100)
        if pygame.sprite.spritecollideany(self, player_group):
            if self.type_powerup == 1 and not shield_status:
                Shield()
            elif self.type_powerup == 2 and not god_status:
                god_status_again = 1
                god_status = 1
            elif self.type_powerup == 2 and god_status:
                god_status_again = 1
            self.kill()


def enemy_move_update():  # Передвижение врагов
    global enemy_direction, enemy_speed, delta_time

    if enemy_group:
        leftmost = min(enemy.rect.x for enemy in enemy_group)
        rightmost = max(enemy.rect.x + enemy.rect.w for enemy in enemy_group)

        # Проверка на границы
        if rightmost >= width:
            if enemy_direction == 1:
                enemy_direction *= -1
                for enemy in enemy_group:
                    enemy.rect.y += 10
        elif leftmost <= 0:
            if enemy_direction == -1:
                enemy_direction *= -1
                for enemy in enemy_group:
                    enemy.rect.y += 10

        # Обновление всех врагов
        for enemy in enemy_group:
            enemy.rect.x += int(enemy_direction * enemy_speed * delta_time * 100)
            # print(enemy_speed)


def initialize_next_level():
    global enemy_group, score, start_ticks, enemy_speed, shield_status, god_status, bullet_group_enemy, bullet_status  # Обнуляем группу врагов и счет
    if shield_status == 1:
        shield_status = 0
        list(player_group)[1].kill()
    bullet_group.empty()
    bullet_status = 0
    powerup_group.empty()
    god_status = 0
    enemy_group.empty()  # Очищаем группу врагов
    bullet_group_enemy.empty()
    explosion_group.empty()
    score = 0  # Обнуляем счет
    enemy_speed = start_enemy_speed
    start_ticks = pygame.time.get_ticks()  # Сбрасываем таймер


Menu().run()
Player()

def level_one():
    pygame.mixer.music.load('data/level_1_sound.mp3')  # Музыка для первого уровня
    pygame.mixer.music.play(-1)  # Воспроизведение музыки в цикле
    for i in range(57, width - 50, 50):
        Enemy_Green(i, 40)
    for i in range(57, width - 50, 50):
        Enemy_Green(i, -40)
    for i in range(57, width - 50, 50):
        Enemy_Green(i, -95)
    for i in range(40, width - 50, 52):
        Enemy_Yellow(i, -150)

def level_two():
    pygame.mixer.music.load('data/level_2_sound.mp3')  # Музыка для второго уровня
    pygame.mixer.music.play(-1)  # Воспроизведение музыки в цикле
    for i in range(57, width - 50, 50):
        Enemy_Green(i, 40)
    for i in range(57, width - 50, 50):
        Enemy_Green(i, -40)
    for i in range(57, width - 50, 50):
        Enemy_Yellow(i, -95)
    for i in range(40, width - 50, 52):
        Enemy_Yellow(i, -150)
    for i in range(22, width - 50, 56):
        Enemy_Red(i, -230)

def level_three():
    pygame.mixer.music.load('data/level_3_sound.mp3')  # Музыка для второго уровня
    pygame.mixer.music.play(-1)  # Воспроизведение музыки в цикле
    for i in range(57, width - 50, 50):
        Enemy_Green(i, 30)
    for i in range(57, width - 50, 50):
        Enemy_Yellow(i, -50)
    for i in range(57, width - 50, 50):
        Enemy_Yellow(i, -130)
    for i in range(22, width - 50, 56):
        Enemy_Red(i, -200)
    for i in range(22, width - 50, 56):
        Enemy_Red(i, -270)

if level == 1:  # Первый уровень
    level_one()
elif level == 2:  # второй уровень
    level_two()
elif level == 3:  # второй уровень
    level_three()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    background = pygame.transform.scale(load_image("space_background_game.jpg"), (800, 400))  # Фон
    screen.blit(background, (-100, 0))
    delta_time = clock.get_time() / 1000  # get_time() возвращает время с последнего тика в мс
    bullet_group.draw(screen)
    bullet_group.update()
    bullet_group_enemy.draw(screen)
    bullet_group_enemy.update()
    enemy_group.draw(screen)
    enemy_group.update()
    enemy_move_update()
    explosion_group.update()
    explosion_group.draw(screen)
    powerup_group.update()
    powerup_group.draw(screen)
    draw_score_and_timer()
    player_group.draw(screen)
    player_group.update()

    if len(enemy_group) == 0:
        if list(player_group):
            remaining_time = total_time - (pygame.time.get_ticks() - start_ticks) // 1000
            multiplier = 1 + (remaining_time / 60) * 0.6
            final_score = int(score * multiplier)
            all_score = cur.execute(f"""SELECT score_all FROM settings""").fetchall()[0][0]
            cur.execute(f"""UPDATE settings SET score_all = {all_score + final_score}""")
            con.commit()
            show_end_screen(final_score)
        else:
            Player()
        if level == 1:  # Первый уровень
            level_one()
        elif level == 2:  # второй уровень
            level_two()
        elif level == 3:  # второй уровень
            level_three()
        # Показываем экран завершения
        # running = False

    final_score = int(score)
    pygame.display.flip()
    clock.tick(fps)
pygame.quit()
