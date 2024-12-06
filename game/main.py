import pygame
import os
from pygame import mixer
import time
import random
import button

pygame.font.init()
pygame.mixer.init()
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Benediction Survival")

shoot_fx = pygame.mixer.Sound('assets/Fireball.mp3')
shoot_fx.set_volume(0.7)

GameOver_fx = pygame.mixer.Sound('assets/GameOver.mp3')
GameOver_fx.set_volume(0.5)

Damaged_fx = pygame.mixer.Sound('assets/Damaged.mp3')
Damaged_fx.set_volume(0.5)

# Load images
WITCH = pygame.image.load(os.path.join("assets", "witch.png"))
BAT = pygame.image.load(os.path.join("assets", "bat.png"))
WITCH1 = pygame.image.load(os.path.join("assets", "witch.png"))
PAUSE_BUTTON = pygame.image.load(os.path.join("assets", "pause.png"))
RESUME_BUTTON = pygame.image.load(os.path.join("assets", "resume.png"))
TITLE = pygame.image.load(os.path.join("assets", "title.png"))

# Player player
WIZARD_PLAYER = pygame.image.load(os.path.join("assets", "player.png"))

# Balls
SKULL = pygame.image.load(os.path.join("assets", "skull.png"))

FIREBALL = pygame.image.load(os.path.join("assets", "fireball.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bg1.png")), (WIDTH, HEIGHT))

# code sa ball
class Ball:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

#code sa wizard
class wizard:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.wizard_img = None
        self.ball_img = None
        self.balls = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.wizard_img, (self.x, self.y))
        for ball in self.balls:
            ball.draw(window)

    def move_balls(self, vel, obj):
        self.cooldown()
        for ball in self.balls:
            ball.move(vel)
            if ball.off_screen(HEIGHT):
                self.balls.remove(ball)
            elif ball.collision(obj):
                obj.health -= 10
                if obj.health == 0:
                    GameOver_fx.play()
                elif obj.health > 0:
                    Damaged_fx.play()
                self.balls.remove(ball)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            shoot_fx.play()
            ball = Ball(self.x, self.y, self.ball_img)
            self.balls.append(ball)
            self.cool_down_counter = 1

    def get_width(self):
        return self.wizard_img.get_width()

    def get_height(self):
        return self.wizard_img.get_height()

#player(wizard)
class Player(wizard):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.wizard_img = WIZARD_PLAYER
        self.ball_img = FIREBALL
        self.mask = pygame.mask.from_surface(self.wizard_img)
        self.max_health = health
        self.score = 0
        self.pause = False

    def move_balls(self, vel, objs):
        self.cooldown()
        for ball in self.balls:
            ball.move(vel)
            if ball.off_screen(HEIGHT):
                self.balls.remove(ball)
            else:
                for obj in objs:
                    if ball.collision(obj):
                        objs.remove(obj)
                        self.score+=10
                        if ball in self.balls:
                            self.balls.remove(ball)
   
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.wizard_img.get_height() + 10, self.wizard_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.wizard_img.get_height() + 10, self.wizard_img.get_width() * (self.health/self.max_health), 10))

#enemy(wizard)
class Enemy(wizard):
    COLOR_MAP = {
                "witch": (WITCH, SKULL),
                "bat": (BAT,SKULL),
                "witch1": (WITCH1, SKULL)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.wizard_img, self.ball_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.wizard_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            ball = Ball(self.x-20, self.y, self.ball_img)
            self.balls.append(ball)
            self.cool_down_counter = 1
            
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None