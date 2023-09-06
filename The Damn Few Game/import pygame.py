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
#background_sound = pygame.mixer.music.load('background.mp3')
#pygame.mixer.music.play(-1)

sfx_volume = 0.1  
music_volume = 0.1  


# Constraints
WIDTH, HEIGHT = 1280, 720
FPS = 60
WHITE = (255, 255, 255)
DARK_GREY = (50, 50, 50)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
PLAYER_SPEED = 5
ENEMY_SPEED = 1
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
DARK_RED_BLUE = (0, 0, 139)

ENEMY_COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (139, 69, 19), (255, 140, 0), (255, 0, 255), (128, 0, 128)]




image = pygame.image.load("Diver.png") 
spear = pygame.image.load("Spear_Black2.png")
background_image = pygame.image.load("Oceanfloor.png") 
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Constants for button dimensions and positions
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_X = WIDTH // 2 - BUTTON_WIDTH // 2
BUTTON_Y_START = HEIGHT // 2 - BUTTON_HEIGHT // 2
BUTTON_Y_SPACE = 60  # Vertical spacing between buttons

# Define the retry and quit buttons
retry_button = pygame.Rect(BUTTON_X, BUTTON_Y_START, BUTTON_WIDTH, BUTTON_HEIGHT)
quit_button_game_over = pygame.Rect(BUTTON_X, BUTTON_Y_START + BUTTON_Y_SPACE, BUTTON_WIDTH, BUTTON_HEIGHT)
options_button = pygame.Rect(BUTTON_X, BUTTON_Y_START + BUTTON_Y_SPACE, BUTTON_WIDTH, BUTTON_HEIGHT)

# Health bar Sizing
HEALTH_BAR_WIDTH = 100
HEALTH_BAR_HEIGHT = 15
HEALTH_BAR_PADDING = 10

COLLISION_COOLDOWN = 1  # Cooldown Seconds

player_health = 3
high_score = 0
current_session_high_score = 0


# Initialize the game_over variable
game_over = False
start_menu_running = True


# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Damn Few")

clock = pygame.time.Clock()
current_time = time.time()

background_color = (0, 0, 0)
font = pygame.font.Font(None, 36)

# Asset image loading
player_image = pygame.image.load("Diver.png").convert()
player_image = pygame.transform.scale(image, (85, 80))  # Resize the image as needed
player_image.set_colorkey((1, 0, 0))  # Set a transparent color if needed


enemy_image = pygame.Surface((40, 40))
enemy_image.fill((102, 205, 170))


projectile_image = pygame.image.load("Diver.png").convert()
projectile_image = pygame.transform.scale(spear, (40, 60))  # Resize the image as needed
projectile_image.set_colorkey((1, 0, 0))  # Set a transparent color if needed

#projectile_image = pygame.Surface((10, 10))
#projectile_image.fill((255, 0, 0))

enemies = []
enemies_to_remove = []

class Enemy:
    def __init__(self):
        # Randomize enemy image size (width and height)
        self.image_width = random.randint(20, 60)
        self.image_height = random.randint(20, 60)
        self.image = pygame.Surface((self.image_width, self.image_height))
        self.color = random.choice(ENEMY_COLORS)
        self.image.fill(self.color)

        # Randomize collision box size (width and height)
        self.collision_width = self.image_width
        self.collision_height = self.image_height

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(0, HEIGHT // 2)
        self.vx = random.uniform(-ENEMY_SPEED, ENEMY_SPEED)
        self.vy = random.uniform(-ENEMY_SPEED, ENEMY_SPEED)
        self.speed = random.uniform(1, 3)

projectiles = []

class Projectile:
    def __init__(self, x, y, vx, vy):
        self.image = projectile_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vx = vx
        self.vy = vy

# Start menu loop
start_game_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 4 + 50, 200, 50)
quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
options_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)

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
                # Open the options menu here
                options_menu_running = True  # Flag to enter the options menu loop
                while options_menu_running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            options_menu_running = False  # Exit options menu
                        # Handle other options menu interactions here

                    # Clear the screen and draw the options menu elements
                    screen.fill(WHITE)

                    # Draw SFX slider background
                    pygame.draw.rect(screen, BLACK, sfx_slider_rect)
                    # Draw SFX slider handle
                    pygame.draw.rect(screen, slider_color, sfx_slider_rect)
                    sfx_slider_handle_x = sfx_slider_rect.left + int(sfx_volume * sfx_slider_rect.width)
                    pygame.draw.circle(screen, slider_handle_color,
                                       (sfx_slider_handle_x, sfx_slider_rect.centery), slider_handle_radius)

                    # Draw music slider background
                    pygame.draw.rect(screen, BLACK, music_slider_rect)
                    # Draw music slider handle
                    pygame.draw.rect(screen, slider_color, music_slider_rect)
                    music_slider_handle_x = music_slider_rect.left + int(music_volume * music_slider_rect.width)
                    pygame.draw.circle(screen, slider_handle_color,
                                       (music_slider_handle_x, music_slider_rect.centery), slider_handle_radius)

                    # Draw titles for sliders
                    sfx_title_text = font.render("SFX Volume", True, BLUE)
                    music_title_text = font.render("Music Volume", True, BLUE)
                    screen.blit(sfx_title_text, (sfx_slider_rect.left, sfx_slider_rect.top - 20))
                    screen.blit(music_title_text, (music_slider_rect.left, music_slider_rect.top - 20))

                    pygame.display.flip()

                # After exiting the options menu, continue with the start menu loop
            elif sfx_slider_rect.collidepoint(event.pos):
                # Handle slider interaction (dragging) here if needed
                pass
            elif music_slider_rect.collidepoint(event.pos):
                # Handle slider interaction (dragging) here if needed
                pass

    screen.fill(DARK_GREY)

    # Game Name
    title_font = pygame.font.Font(None, 120)
    title_text = title_font.render("Scuba Steve", True, BLUE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))

    start_game_text = font.render("Start Game", True, BLUE)
    quit_text = font.render("Quit", True, BLUE)
    options_text = font.render("Options", True, BLUE)
    pygame.draw.rect(screen, BLACK, start_game_button)
    pygame.draw.rect(screen, BLACK, quit_button)
    pygame.draw.rect(screen, BLACK, options_button)

    # Blit title text to the screen
    screen.blit(title_text, title_rect)

    screen.blit(start_game_text,
                (start_game_button.centerx - start_game_text.get_width() // 2,
                 start_game_button.centery - start_game_text.get_height() // 2))
    screen.blit(quit_text, (quit_button.centerx - quit_text.get_width() // 2,
                            quit_button.centery - quit_text.get_height() // 2))
    screen.blit(options_text, (options_button.centerx - options_text.get_width() // 2,
                               options_button.centery - options_text.get_height() // 2))
    pygame.display.flip()

# Main game loop
running = True
start_time = time.time()
score = 0
player_health = 3

player_rect = player_image.get_rect()
player_rect.center = (WIDTH // 2, HEIGHT // 2)  # Player Spawn point

last_collision_time = 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - player_rect.centerx
            dy = mouse_y - player_rect.centery
            angle = math.atan2(dy, dx)
            vx = math.cos(angle) * 5
            vy = math.sin(angle) * 5
            projectiles.append(Projectile(player_rect.centerx, player_rect.centery, vx * 1.5, vy * 1.5))
            projectile_sound.play()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        if player_rect.left > 0:
            player_rect.x -= PLAYER_SPEED
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        if player_rect.right < WIDTH:
            player_rect.x += PLAYER_SPEED
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        if player_rect.top > 0:
            player_rect.y -= PLAYER_SPEED
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        if player_rect.bottom < HEIGHT:
            player_rect.y += PLAYER_SPEED

    current_time = time.time()

    # Update projectiles
    for projectile in projectiles:
        projectile.rect.x += projectile.vx
        projectile.rect.y += projectile.vy
        if projectile.rect.y < 0 or projectile.rect.y > HEIGHT or \
           projectile.rect.x < 0 or projectile.rect.x > WIDTH:
            projectiles.remove(projectile)

    # Update enemies and check boundaries
    for enemy in enemies:
        enemy.rect.x += enemy.vx * enemy.speed
        enemy.rect.y += enemy.vy * enemy.speed

        # Add logic to handle boundary checks with respect to enemy's size
        if enemy.rect.left < 0 or enemy.rect.right > WIDTH:
            enemy.vx = -enemy.vx
            enemy.rect.x += enemy.vx * enemy.speed
            enemy.rect.y += enemy.vy * enemy.speed

        if enemy.rect.top < 0 or enemy.rect.bottom > HEIGHT:
            enemy.vy = -enemy.vy
            enemy.rect.x += enemy.vx * enemy.speed
            enemy.rect.y += enemy.vy * enemy.speed

    # Update time
    elapsed_time = time.time() - start_time
    if elapsed_time > 120:
        running = False

    # Spawn new enemies
    if len(enemies) < 5 and random.randint(0, 100) < 3:
        enemies.append(Enemy())

    # Collision detection between player and enemies
    if current_time - last_collision_time >= COLLISION_COOLDOWN:
        for enemy in enemies:
            if player_rect.colliderect(enemy.rect):
                player_health -= 1
                print("Player-enemy collision detected!")
                last_collision_time = current_time
                if player_health <= 0:
                    game_over = True
                break

    if player_health <= 0:
        game_over = True

    # Check collisions between projectiles and enemies
    for projectile in projectiles.copy():
        for enemy in enemies.copy():
            if projectile.rect.colliderect(enemy.rect):
                print("Enemy Destroyed!")
                projectiles.remove(projectile)
                enemies.remove(enemy)
                score += 1
                enemyhit_sound.play()

    for enemy in enemies_to_remove:
        enemies.remove(enemy)
    enemies_to_remove.clear()

    screen.blit(background_image, (0, 0))

    # Draw health bars
    for i in range(player_health):
        if player_health == 3:
            health_color = GREEN
        elif player_health == 2:
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
    screen.blit(player_image, player_rect)

    # Draw projectiles
    for projectile in projectiles:
        screen.blit(projectile.image, projectile.rect)


    if score > current_session_high_score:
        current_session_high_score = score


    # Draw score
    score_text = font.render(f"Fish Saved: {score}", True, (BLUE))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

    # Render and display the high score
    high_score_text = font.render(f"High Score: {current_session_high_score}", True, (BLUE))
    screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, 35))

    # Draw time remaining
    remaining_time = max(0, 120 - elapsed_time)
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