import pygame
import sys
import random
import time
import math

# Initialize pygame
pygame.init()
pygame.mixer.init()
projectile_sound = pygame.mixer.Sound("Pew.wav.mp3")
enemyhit_sound = pygame.mixer.Sound('Enemy hit.mp3')
game_over = False
start_menu_running = True

sfx_volume = 0.1
music_volume = 0.1

# Constraints
WIDTH, HEIGHT = 1280, 720
FPS = 60

WHITE = (255, 255, 255)
DARK_GREY = (50, 50, 50)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
DARK_RED_BLUE = (0, 0, 139)
TRANS = (1, 0, 0)

clock = pygame.time.Clock()
current_time = time.time()
game_time = 120

background_color = (0, 0, 0)
font = pygame.font.Font(None, 36)

score = 0
high_score = 0
current_session_high_score = 0

ENEMY_SPEED = 2.0   
PLAYER_SPEED = 5
player_health = 3

COLLISION_COOLDOWN = 1 
last_collision_time = 1

enemies = []
enemies_to_remove = []

projectiles = []
projectiles_to_remove =[]


BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_X = WIDTH // 2 - BUTTON_WIDTH // 2
BUTTON_Y_START = HEIGHT // 2 - BUTTON_HEIGHT // 2
BUTTON_Y_SPACE = 60  
HEALTH_BAR_WIDTH = 100
HEALTH_BAR_HEIGHT = 15
HEALTH_BAR_PADDING = 10


# Image/asset Loading
image = pygame.image.load("ScubaSteve.png")
spear = pygame.image.load("Spear_Black2.png")
background_image = pygame.image.load("Oceanfloor.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
startmenu_image = pygame.image.load("startmenu.png")
startmenu_image = pygame.transform.scale(startmenu_image, (WIDTH, HEIGHT))
ENEMY_IMAGES = [
    pygame.image.load("FIsh1.png"), 
    pygame.image.load("fish2.png"),
    pygame.image.load("fish3.png"),
    pygame.image.load("fish4.png"),
]

retry_button = pygame.Rect(BUTTON_X, BUTTON_Y_START, BUTTON_WIDTH, BUTTON_HEIGHT)
quit_button_game_over = pygame.Rect(BUTTON_X, BUTTON_Y_START + BUTTON_Y_SPACE, BUTTON_WIDTH, BUTTON_HEIGHT)
options_button = pygame.Rect(BUTTON_X, BUTTON_Y_START + BUTTON_Y_SPACE, BUTTON_WIDTH, BUTTON_HEIGHT)


# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Damn Few")


# Asset image loading
player_image = pygame.image.load("ScubaSteve.png").convert()
player_image = pygame.transform.scale(image, (100, 95))  #player size
player_image.set_colorkey((TRANS))  

enemy_image = pygame.Surface((40, 40))
enemy_image.fill((102, 205, 170))

projectile_image = pygame.image.load("Spear_Black2.png").convert()
projectile_image = pygame.transform.scale(spear, (40, 60))  
projectile_image.set_colorkey((TRANS))  


class Enemy:
    def __init__(self):
        self.image = random.choice(ENEMY_IMAGES)
        self.rect = self.image.get_rect()
        
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(0, HEIGHT // 2)
        self.vx = max(1, random.uniform(-ENEMY_SPEED, ENEMY_SPEED))
        self.vy = max(1, random.uniform(-ENEMY_SPEED, ENEMY_SPEED))

        self.image_flipped = False
        while self.rect.colliderect(player):
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(0, HEIGHT // 2)

    def update(self):
        # Update position of enemy
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Check for direction chage
        if self.vx > 0 and not self.image_flipped:
            self.image = pygame.transform.flip(self.image, True, False)  # flip horizontally
            self.image_flipped = True
        elif self.vx < 0 and self.image_flipped:
            self.image = pygame.transform.flip(self.image, True, False)  # flip back to original
            self.image_flipped = False

        # Handle boundary checks
        if self.rect.left < 0:
            self.vx = -self.vx
            self.rect.left = 0

        if self.rect.right > WIDTH:
            self.vx = -self.vx
            self.rect.right = WIDTH

        if self.rect.top < 0:
            self.vy = -self.vy
            self.rect.top = 0

        if self.rect.bottom > HEIGHT:
            self.vy = -self.vy
            self.rect.bottom = HEIGHT


class Projectile:
    def __init__(self, x, y, vx, vy, direction):
        self.image = projectile_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vx = vx
        self.vy = vy
        self.direction = direction 

class Player:
    def __init__(self, image, x, y):
        self.original_image = image
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = PLAYER_SPEED
        self.health = 3
        self.direction = "left"

    def move(self, dx, dy):
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy

        if 0 <= new_x <= WIDTH - self.rect.width:
            self.rect.x = new_x
        if 0 <= new_y <= HEIGHT - self.rect.height:
            self.rect.y = new_y

        # Flip the player's image horizontally based on movement direction
        if dx < 0:
            self.image = pygame.transform.flip(self.original_image, True, False)
            self.direction ="left"
        elif dx > 0:
            self.image = self.original_image
            self.direction = "right"

    def shoot(self, target_x, target_y):
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        angle = math.atan2(dy, dx)
        vx = math.cos(angle) * 5
        vy = math.sin(angle) * 5
        projectiles.append(Projectile(self.rect.centerx, self.rect.centery, vx * 1.5, vy * 1.5, self.direction))
        projectile_sound.play()

# Create the player instance
player = Player(player_image, WIDTH // 2, HEIGHT // 2)

# Start menu loop
start_game_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 11 + 50, 200, 50)
quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 6 + 50, 200, 50)
options_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 4 + 50, 200, 50)

sfx_slider_rect = pygame.Rect(WIDTH // 4, HEIGHT // 2 - 25, 200, 10)
music_slider_rect = pygame.Rect(WIDTH // 4, HEIGHT // 2 + 25, 200, 10)
slider_color = BLACK
slider_handle_radius = 10
slider_handle_color = BLUE

while start_menu_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if start_game_button.collidepoint(event.pos):
                start_menu_running = False
            elif quit_button.collidepoint(event.pos):
                pygame.quit()
                sys.exit()
            elif options_button.collidepoint(event.pos):
                options_menu_running = True  
                while options_menu_running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            options_menu_running = False  #
                      

                    
                    screen.fill(BLUE)

                    
                    pygame.draw.rect(screen, BLACK, sfx_slider_rect)
                    pygame.draw.rect(screen, slider_color, sfx_slider_rect)
                    sfx_slider_handle_x = sfx_slider_rect.left + int(sfx_volume * sfx_slider_rect.width)
                    pygame.draw.circle(screen, slider_handle_color,
                                       (sfx_slider_handle_x, sfx_slider_rect.centery), slider_handle_radius)
                    pygame.draw.rect(screen, BLACK, music_slider_rect)
                    pygame.draw.rect(screen, slider_color, music_slider_rect)
                    music_slider_handle_x = music_slider_rect.left + int(music_volume * music_slider_rect.width)
                    pygame.draw.circle(screen, slider_handle_color,
                                       (music_slider_handle_x, music_slider_rect.centery), slider_handle_radius)
                    sfx_title_text = font.render("SFX Volume", True, BLACK)
                    music_title_text = font.render("Music Volume", True, BLACK)
                    screen.blit(sfx_title_text, (sfx_slider_rect.left, sfx_slider_rect.top - 20))
                    screen.blit(music_title_text, (music_slider_rect.left, music_slider_rect.top - 20))

                    pygame.display.flip()

            elif sfx_slider_rect.collidepoint(event.pos):
                pass
            elif music_slider_rect.collidepoint(event.pos):
                pass

    screen.blit(startmenu_image, (0, 0))
    startmenu_color = (1, 0, 0)
    font = pygame.font.Font(None, 36)

    # Game Name
    title_font = pygame.font.Font(None, 100)
    title_text = title_font.render("Scuba Steve", True, BLACK)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 16))

    start_game_text = font.render("Start Game", True, BLUE)
    quit_text = font.render("Quit", True, BLUE)
    options_text = font.render("Options", True, BLUE)
    pygame.draw.rect(screen, BLACK, start_game_button)
    pygame.draw.rect(screen, BLACK, quit_button)
    pygame.draw.rect(screen, BLACK, options_button)

    # Blit tittle text
    screen.blit(title_text, title_rect)

    screen.blit(start_game_text,
                (start_game_button.centerx - start_game_text.get_width() // 2,
                 start_game_button.centery - start_game_text.get_height() // 2))
    screen.blit(quit_text, (quit_button.centerx - quit_text.get_width() // 2,
                            quit_button.centery - quit_text.get_height() // 2))
    screen.blit(options_text, (options_button.centerx - options_text.get_width() // 2,
                               options_button.centery - options_text.get_height() // 2))
    pygame.display.flip()

# Main loop
running = True
start_time = time.time()


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player.shoot(mouse_x, mouse_y)

    keys = pygame.key.get_pressed()
    dx, dy = 0, 0

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        dx -= PLAYER_SPEED
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        dx += PLAYER_SPEED
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        dy -= PLAYER_SPEED
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        dy += PLAYER_SPEED

    player.move(dx, dy)

    current_time = time.time()

    # Update projectiles
    for projectile in projectiles:
        projectile.rect.x += projectile.vx
        projectile.rect.y += projectile.vy
        if projectile.rect.y < 0 or projectile.rect.y > HEIGHT or \
           projectile.rect.x < 0 or projectile.rect.x > WIDTH:
            projectiles_to_remove.append(projectile)

    for projectile in projectiles.copy():
        for enemy in enemies.copy():
            if projectile.rect.colliderect(enemy.rect):
                #projectiles.remove(projectile)
                enemies.remove(enemy)
                score += 1
                enemyhit_sound.play()

    #for projectile in projectiles_to_remove:
        #projectiles.remove(projectile)

    for projectile in projectiles:
        if projectile.direction == "left":
            rotated_image = pygame.transform.flip(projectile.image, True, False)
        else:
            rotated_image = projectile.image
        screen.blit(rotated_image, projectile.rect)

    for enemy in enemies:
        enemy.update()

        if enemy.rect.left < 0:
            enemy.vx = -enemy.vx
            enemy.rect.left = 0

        if enemy.rect.right > WIDTH:
            enemy.vx = -enemy.vx
            enemy.rect.right = WIDTH

        if enemy.rect.top < 0:
            enemy.vy = -enemy.vy
            enemy.rect.top = 0

        if enemy.rect.bottom > HEIGHT:
            enemy.vy = -enemy.vy
            enemy.rect.bottom = HEIGHT

    pygame.display.flip()

    # Timer
    elapsed_time = time.time() - start_time
    if elapsed_time > game_time:
        running = False

    # Spawn new enemies
    if len(enemies) < 5 and random.randint(0, 100) < 3:
        enemies.append(Enemy())

    # Collision detection between player and enemies
    if current_time - last_collision_time >= COLLISION_COOLDOWN:
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                player.health -= 1
                #print("Player-enemy collision detected!")
                last_collision_time = current_time
                if player.health <= 0:
                    game_over = True
                break

    for enemy in enemies_to_remove:
        enemies.remove(enemy)
    enemies_to_remove.clear()

    screen.blit(background_image, (0, 0))

    # Draw health bars
    for i in range(player.health):
        if player.health == 3:
            health_color = GREEN
        elif player.health == 2:
            health_color = YELLOW
        else:
            health_color = RED

        health_bar_rect = pygame.Rect(HEALTH_BAR_PADDING + i * (HEALTH_BAR_WIDTH + HEALTH_BAR_PADDING),
                                      HEALTH_BAR_PADDING,
                                      HEALTH_BAR_WIDTH,
                                      HEALTH_BAR_HEIGHT)
        pygame.draw.rect(screen, health_color, health_bar_rect)

    # Draw enemies
    for enemy in enemies:
        screen.blit(enemy.image, enemy.rect)

    # Draw player
    screen.blit(player.image, player.rect)

    if score > current_session_high_score:
        current_session_high_score = score

    # Draw score
    score_text = font.render(f"Fish Skewered: {score}", True, (BLUE))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

    # display the high score
    high_score_text = font.render(f"High Score: {current_session_high_score}", True, (BLUE))
    screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, 35))

    # Draw timer
    remaining_time = max(0, game_time - elapsed_time)
    time_text = font.render(f"Time: {int(remaining_time)}", True, (BLUE))
    screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 60))

    # Draw game over screen
    if game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(DARK_RED_BLUE)
        game_over_text = font.render("Game Over", True, BLUE)
        retry_text = font.render("Retry", True, BLUE)
        quit_text_game_over = font.render("Quit", True, BLUE)

        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        retry_button.topleft = (WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2 - BUTTON_HEIGHT // 2)
        quit_button_game_over.topleft = (WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2 + BUTTON_HEIGHT)

        screen.blit(game_over_text, game_over_rect)
        pygame.draw.rect(screen, BLACK, retry_button)
        pygame.draw.rect(screen, BLACK, quit_button_game_over)
        screen.blit(retry_text, (retry_button.centerx - retry_text.get_width() // 2,
                                 retry_button.centery - retry_text.get_height() // 2))
        screen.blit(quit_text_game_over, (quit_button_game_over.centerx - quit_text_game_over.get_width() // 2,
                                           quit_button_game_over.centery - quit_text_game_over.get_height() // 2))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
