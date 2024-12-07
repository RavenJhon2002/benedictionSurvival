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

shoot_fx = pygame.mixer.Sound('game/assets/Fireball.mp3')
shoot_fx.set_volume(0.7)

GameOver_fx = pygame.mixer.Sound('game/assets/GameOver.mp3')
GameOver_fx.set_volume(0.5)

Damaged_fx = pygame.mixer.Sound('game/assets/Damaged.mp3')
Damaged_fx.set_volume(0.5)

# Load images
WITCH = pygame.image.load(os.path.join("game/assets", "witch.png"))
BAT = pygame.image.load(os.path.join("game/assets", "bat.png"))
WITCH1 = pygame.image.load(os.path.join("game/assets", "witch.png"))
PAUSE_BUTTON = pygame.image.load(os.path.join("game/assets", "pause.png"))
RESUME_BUTTON = pygame.image.load(os.path.join("game/assets", "resume.png"))
TITLE = pygame.image.load(os.path.join("game/assets", "title.png"))

# Player player
WIZARD_PLAYER = pygame.image.load(os.path.join("game/assets", "player.png"))

# Balls
SKULL = pygame.image.load(os.path.join("game/assets", "skull.png"))

FIREBALL = pygame.image.load(os.path.join("game/assets", "fireball.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("game/assets", "bg1.png")), (WIDTH, HEIGHT))

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


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("Times New Roman", 50)
    lost_font = pygame.font.SysFont("Times New Roman", 60)
    pause_font = pygame.font.SysFont("Times New Roman", 120)
    pause_button = button.Button(10, 660, PAUSE_BUTTON, 1)
    resume_button = button.Button(WIDTH // 2 - 30, 400, RESUME_BUTTON, 1)
    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    ball_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    won = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        if player.pause == False:
            lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
            level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
            score_label = main_font.render(f"Score: {player.score}", 1, (255,255,255))
            
            WIN.blit(lives_label, (10, 10))
            WIN.blit(score_label, (10, 50))
            WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

            for enemy in enemies:
                enemy.draw(WIN)

            player.draw(WIN)
            
            if pause_button.draw(WIN):
                player.pause = True
                pygame.mixer.music.set_volume(0)
                
            if lost:
                WIN.blit(BG, (0,0))
                pygame.mixer.music.set_volume(0)
                lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
                WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 300))
                finalscore_label = lost_font.render(f"Your score is: {player.score}", 1, (255,255,255))
                WIN.blit(finalscore_label, (210, 350))
            
            if won:
                WIN.blit(BG, (0,0))
                pygame.mixer.music.set_volume(0)
                lost_label = lost_font.render("You Finished The Game!!", 1, (255,255,255))
                WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 300))
                finalscore_label = lost_font.render(f"Your score is: {player.score}", 1, (255,255,255))
                WIN.blit(finalscore_label, (210, 350))


        if player.pause == True:
            WIN.blit(BG, (0,0))
            pause_label = pause_font.render(f"Game Paused",3,(255,255,255))
            WIN.blit(pause_label,(WIDTH/2 - pause_label.get_width()/2, 300))

            if resume_button.draw(WIN):
                player.pause = False
                pygame.mixer.music.set_volume(0.1)
                
        pygame.display.update()
        
    while run:
        clock.tick(FPS)
        redraw_window()
        if lives <= 0 or player.health <= 0:
            
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            
            if level==2:
                FPS +=10
                lives += 4
                player.health += 40
            
            if level==3:
                FPS += 10
                lives += 4
                player.health += 40
            
            if level==4:
                won = True
            
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["witch", "bat", "witch1"]))
                enemies.append(enemy)

            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
#keypress
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0 and player.pause == False: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH and player.pause == False: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0 and player.pause == False: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT and player.pause == False: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]and player.pause == False:
            player.shoot()


            
        if player.pause == False:
            for enemy in enemies[:]:
                enemy.move(enemy_vel)
                enemy.move_balls(ball_vel, player)

                if random.randrange(0, 2*60) == 1:
                    enemy.shoot()

                if collide(enemy, player):
                    player.health -= 10
                    if player.health == 0:
                        GameOver_fx.play()
                    elif player.health > 0:
                        Damaged_fx.play()
                    enemies.remove(enemy)
                elif enemy.y + enemy.get_height() > HEIGHT:
                    lives -= 1
                    enemies.remove(enemy)

        player.move_balls(-ball_vel, enemies)

#mainmenu
def main_menu():
    title_font = pygame.font.SysFont("Times New Roman", 40)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        WIN.blit(TITLE, (WIDTH/2 - TITLE.get_width()/2,280))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 500))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.mixer.music.load('game/assets/Music1.mp3')
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play(-1, 0.0)
                main()
    pygame.quit()


main_menu()
