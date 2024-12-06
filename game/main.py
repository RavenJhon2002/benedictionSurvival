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
shoot_fx.set_volume(0.6)

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
