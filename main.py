import os
import sys

import pygame

pygame.init()
size = width, height = 600, 400
screen = pygame.display.set_mode(size)
fps = 30
speed_move = 180
speed_bullet = 400
clock = pygame.time.Clock()
bullet_status = 0

player_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


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


class Bullet(pygame.sprite.Sprite):
    image = load_image("laser-bolts.png")

    def __init__(self):
        super().__init__(bullet_group)
        self.frames = []
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


class Enemy_Red(pygame.sprite.Sprite):
    image = load_image("enemy-big.png")

    def __init__(self, x, y):
        super().__init__(enemy_group)
        self.frames = []
        self.cut_sheet(Enemy_Red.image, 2, 1)
        self.cur_frame = 0
        self.if_num = 0
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

    def update(self, *args):
        if self.if_num == 5:
            self.if_num = 0
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.cur_frame], (52, 64))
        self.if_num += 1
        global bullet_status
        if pygame.sprite.spritecollideany(self, bullet_group):
            Explosion(self.rect.x, self.rect.y, 52, 64)
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

    def update(self, *args):
        if self.if_num == 5:
            self.if_num = 0
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.cur_frame], (48, 24))
        self.if_num += 1
        global bullet_status
        if pygame.sprite.spritecollideany(self, bullet_group):
            Explosion(self.rect.x, self.rect.y, 48, 24)
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

    def update(self, *args):
        if self.if_num == 5:
            self.if_num = 0
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.cur_frame], (32, 32))
        self.if_num += 1
        global bullet_status
        if pygame.sprite.spritecollideany(self, bullet_group):
            Explosion(self.rect.x, self.rect.y, 32, 32)
            self.kill()
            list(bullet_group)[0].kill()
            bullet_status = 0

class Explosion(pygame.sprite.Sprite):
    image = load_image("explosion.png")

    def __init__(self, x, y, x_size, y_size):
        super().__init__(enemy_group)
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


Player()
for i in range(22, width - 50, 56):
    Enemy_Red(i, 40)
for i in range(40, width - 50, 52):
    Enemy_Yellow(i, 115)
for i in range(57, width - 50, 50):
    Enemy_Green(i, 150)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))
    player_group.draw(screen)
    player_group.update(event)
    bullet_group.draw(screen)
    bullet_group.update(event)
    enemy_group.draw(screen)
    enemy_group.update(event)
    pygame.display.flip()
    clock.tick(fps)
pygame.quit()
