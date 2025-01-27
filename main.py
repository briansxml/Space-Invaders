import os
import sys
import random
import pygame

pygame.init()
size = width, height = 600, 400
screen = pygame.display.set_mode(size)
fps = 30  # FPS
speed_move = 180  # Скорость передвижения игрока
speed_bullet = 400  # Скорость пули игрока
clock = pygame.time.Clock()
bullet_status = 0  # 1 - пуля игрока существует и летит, 0 - пули игрока нет
enemy_direction = 1  # Направление передвижения врага (1 - вправо, -1 - влево)
enemy_speed = 1  # Скорост передвижения врага
score = 0  # очки
total_time = 120  # таймер
start_ticks = pygame.time.get_ticks()  # Начальное время для таймера
enemy_speed_bullet = 150  # Скорость пули врага
chance_shot_enemy = 20  # С каким шансом враги будут стрелять
running = True

player_group = pygame.sprite.Group()  # Группа спрайтов с игроком
bullet_group = pygame.sprite.Group()  # Группа спрайтов с пулей игрока
bullet_group_enemy = pygame.sprite.Group()  # Группа спрайтов с пулями врагов
enemy_group = pygame.sprite.Group()  # Группа спрайтов с врагами
explosion_group = pygame.sprite.Group()  # Группа спрайтов с взрывами


def load_image(name, colorkey=None):  # Функция загрузки изображения
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def draw_score_and_timer():
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
        self.font = pygame.font.Font(None, 74)  # Шрифт
        self.font_small = pygame.font.Font(None, 36)  # Шрифт маленький
        self.difficulties = ["easy", "medium", "hard"]  # Список сложностей игры
        self.current_difficulty_index = 0  # Сложность игры

    def draw(self):
        screen.fill((0, 0, 0))
        background = pygame.transform.scale(load_image("space_background.jpg"), (800, 400))  # Фон
        screen.blit(background, (-100, 0))
        title = self.font.render("Space Invaders", True, (255, 255, 255))
        start_button = self.font_small.render("Начать", True, (255, 255, 255))
        exit_button = self.font_small.render("Выход", True, (255, 255, 255))
        difficulty_text = self.font_small.render(f"Сложность: {self.difficulties[self.current_difficulty_index]}", True,
                                                 (255, 255, 255))

        start_button_rect = start_button.get_rect(center=(width // 2, height // 2))
        exit_button_rect = exit_button.get_rect(center=(width // 2, height // 2 + 50))

        screen.blit(title, (width // 2 - title.get_width() // 2, height // 4))
        screen.blit(start_button, start_button_rect)
        screen.blit(exit_button, exit_button_rect)
        screen.blit(difficulty_text, (width // 2 - difficulty_text.get_width() // 2, height // 2 + 100))

        left_arrow = self.font_small.render("<", True, (255, 255, 255))
        right_arrow = self.font_small.render(">", True, (255, 255, 255))
        screen.blit(left_arrow, (width // 2 - difficulty_text.get_width() // 2 - 30, height // 2 + 100))
        screen.blit(right_arrow, (width // 2 + difficulty_text.get_width() // 2 + 10, height // 2 + 100))

        return start_button_rect, exit_button_rect

    def run(self):
        global running
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if start_button_rect.collidepoint(mouse_pos):
                        return self.difficulties[self.current_difficulty_index]  # Начать игру с выбранной сложностью
                    if exit_button_rect.collidepoint(mouse_pos):
                        running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.current_difficulty_index = (self.current_difficulty_index + 1) % len(self.difficulties)
                    elif event.key == pygame.K_DOWN:
                        self.current_difficulty_index = (self.current_difficulty_index - 1) % len(self.difficulties)
                    elif event.key == pygame.K_LEFT:
                        self.current_difficulty_index = (self.current_difficulty_index - 1) % len(self.difficulties)
                    elif event.key == pygame.K_RIGHT:
                        self.current_difficulty_index = (self.current_difficulty_index + 1) % len(self.difficulties)

            start_button_rect, exit_button_rect = self.draw()
            pygame.display.flip()
            clock.tick(fps)


class Player(pygame.sprite.Sprite):
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

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        if self.if_num == 5:
            self.if_num = 0
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.cur_frame], (32, 48))
        self.if_num += 1
        global bullet_status
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            if not bullet_status:
                Bullet()
                bullet_status = 1
        if pygame.key.get_pressed()[pygame.K_LEFT] and self.rect.x > width * 0.03:
            self.rect.x -= speed_move / fps
        if pygame.key.get_pressed()[pygame.K_RIGHT] and self.rect.x + self.rect.w < (width * 0.97):
            self.rect.x += speed_move / fps
        if pygame.sprite.spritecollideany(self, bullet_group_enemy):
            Explosion(self.rect.x, self.rect.y, 52, 64)
            self.kill()
            list(bullet_group_enemy)[0].kill()


class Bullet(pygame.sprite.Sprite):
    image = load_image("laser-bolts.png")

    def __init__(self):
        super().__init__(bullet_group)
        self.image = pygame.transform.scale(Bullet.image, (10, 24))
        self.rect = self.image.get_rect()
        self.rect.x = (list(player_group)[0].rect.x
                       + list(player_group)[0].rect.w // 2 - list(bullet_group)[0].rect.w // 2)
        self.rect.y = list(player_group)[0].rect.y - self.rect.h

    def update(self, *args):
        global bullet_status
        self.rect.y -= speed_bullet / fps
        if self.rect.y + self.rect.h < 0:
            bullet_status = 0
            self.kill()


class Enemy_Bullet(pygame.sprite.Sprite):
    image = load_image("laser-bolts.png")

    def __init__(self, x, y):
        super().__init__(bullet_group_enemy)
        self.image = pygame.transform.rotate(pygame.transform.scale(Enemy_Bullet.image, (10, 24)), 180)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, *args):
        self.rect.y += enemy_speed_bullet / fps


class Enemy_Red(pygame.sprite.Sprite):
    image = load_image("enemy-big.png")

    def __init__(self, x, y):
        super().__init__(enemy_group)
        self.frames = []
        self.cut_sheet(Enemy_Red.image, 2, 1)
        self.cur_frame = 0
        self.if_num = 0
        self.if_num_bullet = 0
        self.image = pygame.transform.scale(self.frames[self.cur_frame], (52, 64))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def is_path_clear(self):
        # Проверяет, есть ли враги на пути выстрела
        for enemy in enemy_group:
            if (
                    abs(enemy.rect.x - self.rect.x) < self.rect.width  # Горизонтальное перекрытие
                    and enemy.rect.y > self.rect.y  # Враг ниже текущего
            ):
                return False
        return True

    def update(self, *args):
        if self.if_num_bullet == 30:
            self.if_num_bullet = 0
            if random.randint(1, 100) <= chance_shot_enemy and self.is_path_clear():
                Enemy_Bullet((self.rect.x
                              + self.rect.w // 2 - 5 // 2), self.rect.y + self.rect.h)
        if self.if_num == 5:
            self.if_num = 0
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.cur_frame], self.image.get_size())
        self.if_num += 1
        self.if_num_bullet += 1
        global bullet_status
        if pygame.sprite.spritecollideany(self, bullet_group):
            Explosion(self.rect.x, self.rect.y, 52, 64)
            self.kill()
            list(bullet_group)[0].kill()
            bullet_status = 0
            global score
            score += 100
        if pygame.sprite.spritecollideany(self, bullet_group):
            Explosion(self.rect.x, self.rect.y, self.rect.w, self.rect.h)
            self.kill()
            list(bullet_group)[0].kill()
            bullet_status = 0


class Enemy_Yellow(pygame.sprite.Sprite):
    image = load_image("enemy-medium.png")

    def __init__(self, x, y):
        super().__init__(enemy_group)
        self.frames = []
        self.cut_sheet(Enemy_Yellow.image, 2, 1)
        self.cur_frame = 0
        self.if_num = 0
        self.if_num_bullet = 0
        self.image = pygame.transform.scale(self.frames[self.cur_frame], (48, 24))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def is_path_clear(self):
        # Проверяет, есть ли враги на пути выстрела
        for enemy in enemy_group:
            if (
                    abs(enemy.rect.x - self.rect.x) < self.rect.width  # Горизонтальное перекрытие
                    and enemy.rect.y > self.rect.y  # Враг ниже текущего
            ):
                return False
        return True

    def update(self, *args):
        if self.if_num_bullet == 30:
            self.if_num_bullet = 0
            if random.randint(1, 100) <= chance_shot_enemy and self.is_path_clear():
                Enemy_Bullet((self.rect.x
                              + self.rect.w // 2 - 5 // 2), self.rect.y + self.rect.h)
        if self.if_num == 5:
            self.if_num = 0
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.cur_frame], self.image.get_size())
        self.if_num += 1
        self.if_num_bullet += 1
        global bullet_status
        if pygame.sprite.spritecollideany(self, bullet_group):
            Explosion(self.rect.x, self.rect.y, 52, 64)
            self.kill()
            list(bullet_group)[0].kill()
            bullet_status = 0
            global score
            score += 100
        if pygame.sprite.spritecollideany(self, bullet_group):
            Explosion(self.rect.x, self.rect.y, self.rect.w, self.rect.h)
            self.kill()
            list(bullet_group)[0].kill()
            bullet_status = 0


class Enemy_Green(pygame.sprite.Sprite):
    image = load_image("enemy-small.png")

    def __init__(self, x, y):
        super().__init__(enemy_group)
        self.frames = []
        self.cut_sheet(Enemy_Green.image, 2, 1)
        self.cur_frame = 0
        self.if_num = 0
        self.if_num_bullet = 0
        self.image = pygame.transform.scale(self.frames[self.cur_frame], (32, 32))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def is_path_clear(self):
        # Проверяет, есть ли враги на пути выстрела
        for enemy in enemy_group:
            if (
                    abs(enemy.rect.x - self.rect.x) < self.rect.width  # Горизонтальное перекрытие
                    and enemy.rect.y > self.rect.y  # Враг ниже текущего
            ):
                return False
        return True

    def update(self, *args):
        if self.if_num_bullet == 30:
            self.if_num_bullet = 0
            if random.randint(1, 100) <= chance_shot_enemy and self.is_path_clear():
                Enemy_Bullet((self.rect.x
                              + self.rect.w // 2 - 5 // 2), self.rect.y + self.rect.h)
        if self.if_num == 5:
            self.if_num = 0
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.cur_frame], self.image.get_size())
        self.if_num += 1
        self.if_num_bullet += 1
        global bullet_status
        if pygame.sprite.spritecollideany(self, bullet_group):
            Explosion(self.rect.x, self.rect.y, 52, 64)
            self.kill()
            list(bullet_group)[0].kill()
            bullet_status = 0
            global score
            score += 100
        if pygame.sprite.spritecollideany(self, bullet_group):
            Explosion(self.rect.x, self.rect.y, self.rect.w, self.rect.h)
            self.kill()
            list(bullet_group)[0].kill()
            bullet_status = 0


class Explosion(pygame.sprite.Sprite):
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

    def update(self, *args):
        global bullet_status
        if self.if_num == 3:
            self.if_num = 0
            self.cur_frame += 1
            if self.cur_frame == 5:
                self.kill()
            else:
                self.image = pygame.transform.scale(self.frames[self.cur_frame], (self.y_size, self.y_size))
        self.if_num += 1


def enemy_move_update():
    global enemy_direction, enemy_speed
    if enemy_group:
        leftmost = min(enemy.rect.x for enemy in enemy_group)
        rightmost = max(enemy.rect.x + enemy.rect.w for enemy in enemy_group)

        # Проверка, достигли ли крайние враги границ
        if rightmost >= width or leftmost <= 0:
            enemy_direction *= -1
            for enemy in enemy_group:
                enemy.rect.y += 10

        # Обновление всех врагов
        for enemy in enemy_group:
            enemy.rect.x += enemy_direction * enemy_speed


menu = Menu()
difficulty = menu.run()

if difficulty is None:
    pygame.quit()

Player()
for i in range(22, width - 50, 56):
    Enemy_Red(i, 40)
for i in range(40, width - 50, 52):
    Enemy_Yellow(i, 115)
for i in range(57, width - 50, 50):
    Enemy_Green(i, 150)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    background = pygame.transform.scale(load_image("space_background_game.jpg"), (800, 400))  # Фон
    screen.blit(background, (-100, 0))
    player_group.draw(screen)
    player_group.update()
    bullet_group.draw(screen)
    bullet_group.update()
    bullet_group_enemy.draw(screen)
    bullet_group_enemy.update()
    enemy_group.draw(screen)
    enemy_group.update()
    enemy_move_update()
    explosion_group.update()
    explosion_group.draw(screen)
    draw_score_and_timer()
    final_score = int(score)
    pygame.display.flip()
    clock.tick(fps)
pygame.quit()
