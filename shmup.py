# Shmup game
import pygame, sys
import random
from os import path
import time

# PRESETS
WIDTH = 1400
HEIGHT = 900
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHTBLUE = (91, 132, 215)
CYAN = (128, 255, 255)



# initilisation 
pygame.init()
pygame.mixer.init()
pygame.font.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("shmup!")
clock = pygame.time.Clock()
#important folders
img_dir = path.join(path.dirname(__file__), 'image')
snd_dir = path.join(path.dirname(__file__), 'sound')

# Load all game graphics
background = pygame.image.load("star_background.png").convert()
menu_background = pygame.image.load(path.join(img_dir, "starfield.png")).convert()
menu_background.set_colorkey(BLACK)
player_img = pygame.image.load(path.join(img_dir, "player.png")).convert()
core_img = pygame.image.load(path.join(img_dir, "power_point.png")).convert()
core_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_dir, "bullet.png"))
tech_board = pygame.image.load(path.join(img_dir, "tech_board.png")).convert()
tech_board.set_colorkey(BLACK)
tech_underline = pygame.image.load(path.join(img_dir, "h_underline.png")).convert()
tech_underline.set_colorkey(BLACK)
button_board = pygame.image.load(path.join(img_dir, "button_board.png"))
meteor_images = []
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_big2.png', 'meteorBrown_med1.png',
                'meteorBrown_med3.png', 'meteorBrown_small1.png', 'meteorBrown_small2.png',
                'meteorBrown_tiny1.png']

for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = f"regularExplosion0{i}.png"
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (100, 100))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (75, 75))
    explosion_anim['sm'].append(img_sm)
    filename = f"sonicExplosion0{i}.png"
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

powerup = {}
powerup['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png'))
powerup['recover'] = pygame.image.load(path.join(img_dir, 'recovery.png'))

# Loading audio
bg_music = pygame.mixer.Sound("Towel Defence Ingame.mp3")
bg_music.set_volume(0.7)
mbg_music = pygame.mixer.Sound("Tittle Screen.mp3")
mbg_music.set_volume(0.5)
mbg_music.play(-1)
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, "pew.wav"))
expl_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
snd_explosionpl = pygame.mixer.Sound(path.join(snd_dir, "Explosion.wav"))

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font('TranscendsGames.otf', size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.x = x
    text_rect.y = y
    surf.blit(text_surface, text_rect)

def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 300
    BAR_HEIGHT = 17
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, CYAN, fill_rect)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 70*i
        img_rect.y = y
        surf.blit(img, img_rect)

def button_animation(button, pos, color_a, color_b):
    if button.isOver(pos):
        button.color = color_a
    else:
        button.color = color_b

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -20

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < -100:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 50
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT - 40
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 300
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.recover = False
        self.recovery_timer = 100
        self.last_recovery = pygame.time.get_ticks()

    def update(self):
        #unhide is hidden
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT - 40

        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -10
        if keystate[pygame.K_RIGHT]:
            self.speedx = 10
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top+50)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_sound.play()
    
    def hide(self):
        # hide the player temporarily
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT+300)

    def recover_health(self):
        now = pygame.time.get_ticks()
        if self.recover and now - self.last_recovery < 100:
            print(pygame.time.get_ticks() - self.recovery_timer)
            self.last_recovery = now
            self.shield += 5

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width*.85 / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-200, -100)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.rot = (self.rot + self.rot_speed) % 360
            self.last_update = now
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 40

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class Button:
    def __init__(self, color, x,y,width,height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self,win,font_size,outline=None,font_data=None):
        #Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
        
        if self.text != '':
            if font_data:
                font = pygame.font.Font(font_data, font_size)
            else:
                font = pygame.font.SysFont('comicsans', font_size)
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False

class Pow(pygame.sprite.Sprite):
    def __init__(self, effect, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = effect
        self.image = powerup[self.type]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 5

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < -100:
            self.kill()


all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

startButton = Button((0, 110, 255), 40, 550, 170, 80, 'START GAME')
quitButton = Button((255, 128, 0), 250, 550, 170, 80, 'QUIT')

# Main Game loop
class Game():
    def __init__(self, win, game_width, game_height, FPS):
        self.score = 0
        self.WIDTH = game_width
        self.HEIGHT = game_height
        self.WIN = win
        self.FPS = FPS
        self.level = 0
        self.spawn_number = 8
        self.max_spawn_number = 20
        self.state = 'main_menu'
        self.pause = False

        for i in range(self.spawn_number):
            newmob()

    # Window initilisation
    def redraw_window(self):
        win.blit(background, (0, 0))
        
    def main(self):
        # keep loop running at the right speed
        clock.tick(self.FPS)
        # Processing input(events)
        for event in pygame.event.get():
            # Checking for close window
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.pause = True
                    self.state = 'game_paused'
        
        if len(mobs) == 0:
            self.spawn_number += 1
            if self.spawn_number > self.max_spawn_number:
                player.shoot_delay = 200
                self.spawn_number = self.max_spawn_number
            for i in range(self.spawn_number):
                newmob()

        hits = pygame.sprite.groupcollide(mobs, bullets, True, False)
        for hit in hits:
            self.score += 50 - hit.radius
            if self.score < 0:
                self.score = 0
            expl_lg = Explosion(hit.rect.center, 'lg')
            all_sprites.add(expl_lg)
            random.choice(expl_sounds).play()
            powerup_chance = random.random()
            if powerup_chance > 0.9:
                powerup = Pow('shield', hit.rect.center)
                all_sprites.add(powerup)
                powerups.add(powerup)

            if powerup_chance > 0.99:
                powerup = Pow('recover', hit.rect.center)
                all_sprites.add(powerup)
                powerups.add(powerup)

        mistakes = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
        for mistake in mistakes:
            player.shield -= mistake.radius
            death_explosion = Explosion(mistake.rect.center, 'sm')
            all_sprites.add(death_explosion)
            if player.shield <= 0:
                if player.lives == 0 and not death_explosion.alive():
                    running = False

                death_explosion = Explosion(player.rect.center, 'player')
                all_sprites.add(death_explosion)
                snd_explosionpl.play()
                player.hide()
                player.lives -= 1
                player.shield = 100
        
        pickups = pygame.sprite.spritecollide(player, powerups, True)
        for pickup in pickups:
            if pickup.type == 'shield':
                player.shield += 20
            elif pickup.type == 'recover':
                player.recover = True

        player.recover_health()
        if player.shield > 100:
            player.shield = 100

        # Drawing stuff and update
        self.redraw_window()
        all_sprites.update()
        all_sprites.draw(self.WIN)
        self.WIN.blit(tech_board, (self.WIDTH-tech_board.get_width(), 10))
        draw_text(self.WIN, str(self.score), 64, self.WIDTH-330, 33)
        draw_shield_bar(self.WIN, 16, 83, player.shield)
        self.WIN.blit(tech_underline, (-5, 65))
        draw_lives(self.WIN, 0, 10, player.lives, core_img)

        # *after drawing everything, flip the display
        pygame.display.flip()
    
    def menu_redraw(self):
        self.WIN.blit(menu_background, (0, 0))
        if self.pause == False:
            self.menu_message = "ASTERIOD SHOOTER"
            draw_text(self.WIN, self.menu_message, 70, self.WIDTH/2-580, self.HEIGHT/2-100)
            # win.blit(button_board, (self.WIDTH/2-580, self.HEIGHT/2))
            # win.blit(button_board, (self.WIDTH/2-250, self.HEIGHT/2))
            # startButton.draw(win, 30, (0, 0, 128))
            # quitButton.draw(win, 30, (170, 255, 128))
        elif self.pause == True and self.state == 'game_paused':
            self.menu_message = "GAME PAUSED"
            self.reminder = "(press mouse button for returning back to the game)"
            draw_text(self.WIN, self.menu_message, 70, self.WIDTH/2-580, self.HEIGHT/2-50)
            draw_text(self.WIN, self.reminder, 30, self.WIDTH/2-580, self.HEIGHT/2+20)

    def main_menu(self):
        # keep loop running at the right speed
        clock.tick(self.FPS)
        self.menu_redraw()
        # Processing input(events)
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            # Checking for close window
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.pause = False
                if self.state == 'main_menu':
                    mbg_music.stop()
                    bg_music.play(-1)
                self.state = 'main'
                
        pygame.display.flip()
        
    def state_manager(self):
        if self.state == 'main':
            self.main()
        if self.state == 'main_menu':
            self.main_menu()
        if self.state == 'game_paused':
            self.main_menu()
        
GAME = Game(win, WIDTH, HEIGHT, FPS)
while True:
    GAME.state_manager()

