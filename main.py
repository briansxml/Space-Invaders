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
enemy_direction = 1
enemy_speed = 2

player_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Menu:
    def __init__(self):
        self.font = pygame.font.Font(None, 74)
        self.font_small = pygame.font.Font(None, 36)
        self.difficulty = "easy"
        self.difficulties = ["easy", "medium", "hard"]
        self.current_difficulty_index = 0
        self.running = True

    def draw(self):
        screen.fill((0, 0, 0))
        background = load_image("space_background.jpg")
        screen.blit(background, (0, 0))
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
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if start_button_rect.collidepoint(mouse_pos):
                        return self.difficulties[self.current_difficulty_index]  # Начать игру с выбранной сложностью
                    if exit_button_rect.collidepoint(mouse_pos):
                        self.running = False
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
                       + list(player_group)[0].rect.w // 2 - self.rect.w // 2)
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

        global enemy_direction
        self.rect.x += enemy_direction * enemy_speed
        if self.rect.right >= width or self.rect.left <= 0:
            enemy_direction *= -1
            for enemy in enemy_group:
                enemy.rect.y += 10


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

        global enemy_direction
        self.rect.x += enemy_direction * enemy_speed
        if self.rect.right >= width or self.rect.left <= 0:
            enemy_direction *= -1
            for enemy in enemy_group:
                enemy.rect.y += 10


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

        global enemy_direction
        self.rect.x += enemy_direction * enemy_speed
        if self.rect.right >= width or self.rect.left <= 0:
            enemy_direction *= -1
            for enemy in enemy_group:
                enemy.rect.y += 10


def main():
    menu = Menu()
    difficulty = menu.run()

    if difficulty is None:
        pygame.quit()
        return

    player = Player()

    enemy_count = 10

    for i in range(enemy_count):
        x_position = 50 + (i * (width - 100) // enemy_count)
        Enemy_Red(x_position, 50)
        Enemy_Yellow(x_position, 100)
        Enemy_Green(x_position, 150)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        player_group.draw(screen)
        player_group.update()
        bullet_group.draw(screen)
        bullet_group.update()
        enemy_group.draw(screen)
        enemy_group.update()
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    main()