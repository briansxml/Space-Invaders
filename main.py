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
    image = load_image("player.png")

    def __init__(self):
        super().__init__(player_group)
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.rect.x = width // 2 - self.rect.w // 2
        self.rect.y = 0.9 * height - self.rect.h // 2

    def update(self, *args):
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
    def __init__(self):
        super().__init__(bullet_group)
        self.image = pygame.Surface((5, 15))
        self.image.fill("WHITE")
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
    image = load_image("red.png")

    def __init__(self, x, y):
        super().__init__(enemy_group)
        self.image = Enemy_Red.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, *args):
        global bullet_status
        if pygame.sprite.spritecollideany(self, bullet_group):
            self.kill()
            list(bullet_group)[0].kill()
            bullet_status = 0


class Enemy_Yellow(pygame.sprite.Sprite):
    image = load_image("yellow.png")

    def __init__(self, x, y):
        super().__init__(enemy_group)
        self.image = Enemy_Yellow.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, *args):
        global bullet_status
        if pygame.sprite.spritecollideany(self, bullet_group):
            self.kill()
            list(bullet_group)[0].kill()
            bullet_status = 0


class Enemy_Green(pygame.sprite.Sprite):
    image = load_image("green.png")

    def __init__(self, x, y):
        super().__init__(enemy_group)
        self.image = Enemy_Green.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, *args):
        global bullet_status
        if pygame.sprite.spritecollideany(self, bullet_group):
            self.kill()
            list(bullet_group)[0].kill()
            bullet_status = 0


Player()
for i in range(50, width - 50, 50):
    Enemy_Red(i, 50)
    Enemy_Yellow(i, 100)
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
