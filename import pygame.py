import pygame
import sys
import random
import time
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1280, 720
FPS = 120
WHITE = (255, 255, 255)
DARK_GREY = (50, 50, 50)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
PLAYER_SPEED = 5
ENEMY_SPEED = 1

# Health bar constants
HEALTH_BAR_WIDTH = 100
HEALTH_BAR_HEIGHT = 20
HEALTH_BAR_PADDING = 10

COLLISION_COOLDOWN = 1.5  # Cooldown Seconds

player_health = 3

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Damn Few")

clock = pygame.time.Clock()

background_color = (72, 118, 255)

# Load font for the score and time display
font = pygame.font.Font(None, 36)

# Load player character image
player_image = pygame.Surface((40, 40))
player_image.fill((0, 255, 0))

# Load enemy character image
enemy_image = pygame.Surface((40, 40))
enemy_image.fill((102, 205, 170))

# Load projectile image
projectile_image = pygame.Surface((10, 10))
projectile_image.fill((255, 0, 0))

enemies = []

class Enemy:
    def __init__(self):
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(0, HEIGHT // 2)

projectiles = []

class Projectile:
    def __init__(self, x, y, vx, vy):
        self.image = projectile_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vx = vx
        self.vy = vy

# Start menu loop
start_menu_running = True
start_game_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)

while start_menu_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if start_game_button.collidepoint(event.pos):
                start_menu_running = False
            elif quit_button.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

    screen.fill(DARK_GREY)  
    
    # Render title text
    title_font = pygame.font.Font(None, 120)
    title_text = title_font.render("The Damn Few", True, RED)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    
    start_game_text = font.render("Start Game", True, RED)
    quit_text = font.render("Quit", True, RED)
    
    pygame.draw.rect(screen, BLACK, start_game_button)  # Set button color to black
    pygame.draw.rect(screen, BLACK, quit_button)  # Set button color to black
    
    # Blit title text to the screen
    screen.blit(title_text, title_rect)
    
    screen.blit(start_game_text, (start_game_button.centerx - start_game_text.get_width() // 2, start_game_button.centery - start_game_text.get_height() // 2))
    screen.blit(quit_text, (quit_button.centerx - quit_text.get_width() // 2, quit_button.centery - quit_text.get_height() // 2))
    
    pygame.display.flip()


    start_game_text = font.render("Start Game", True, RED)
    quit_text = font.render("Quit", True, RED)
    
    pygame.draw.rect(screen, BLACK, start_game_button)
    pygame.draw.rect(screen, BLACK, quit_button)
    
    screen.blit(start_game_text, (start_game_button.centerx - start_game_text.get_width() // 2, start_game_button.centery - start_game_text.get_height() // 2))
    screen.blit(quit_text, (quit_button.centerx - quit_text.get_width() // 2, quit_button.centery - quit_text.get_height() // 2))
    
    pygame.display.flip()

# Main game loop
running = True
start_time = time.time()
score = 0

player_rect = player_image.get_rect()
player_rect.center = (WIDTH // 2, HEIGHT // 2)  # Start player at the center

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - player_rect.centerx
            dy = mouse_y - player_rect.centery
            angle = math.atan2(dy, dx)
            vx = math.cos(angle) * 5  # Adjust speed as needed
            vy = math.sin(angle) * 5  # Adjust speed as needed
            projectiles.append(Projectile(player_rect.centerx, player_rect.centery, vx, vy))

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

    last_collision_time = time.time()


    # Update projectiles
    for projectile in projectiles:
        projectile.rect.x += projectile.vx
        projectile.rect.y += projectile.vy
        if projectile.rect.y < 0 or projectile.rect.y > HEIGHT or \
           projectile.rect.x < 0 or projectile.rect.x > WIDTH:
            projectiles.remove(projectile)

    # Update enemies and check boundaries
    for enemy in enemies:
        enemy.rect.x += ENEMY_SPEED
        if enemy.rect.left < 0 or enemy.rect.right > WIDTH:
            ENEMY_SPEED = -ENEMY_SPEED
            enemy.rect.y += 40

    # Update time
    elapsed_time = time.time() - start_time
    if elapsed_time > 120:
        running = False

    # Spawn new enemies
    if len(enemies) < 5 and random.randint(0, 100) < 3:
        enemies.append(Enemy())

    # Collision detection between projectiles and enemies
        for projectile in projectiles:
            for enemy in enemies:
             if projectile.rect.colliderect(enemy.rect):
                projectiles.remove(projectile)
                enemies.remove(enemy)
                score += 1
                print("Enemy destroyed by projectile!")

    # Collision detection between player and enemies
    current_time = time.time()
    if current_time - last_collision_time >= COLLISION_COOLDOWN:
        for enemy in enemies:
            if player_rect.colliderect(enemy.rect):
                player_health -= 1
                print("Player-enemy collision detected!")
                last_collision_time = current_time  # Update last collision time
                if player_health <= 0:
                    running = False
                break  # Exit the loop after a collision

    # Clear the screen
    screen.fill(background_color)


    # Draw health bars
    for i in range(player_health):
        health_bar_rect = pygame.Rect(HEALTH_BAR_PADDING + i * (HEALTH_BAR_WIDTH + HEALTH_BAR_PADDING),
                                      HEALTH_BAR_PADDING,
                                      HEALTH_BAR_WIDTH,
                                      HEALTH_BAR_HEIGHT)
        pygame.draw.rect(screen, RED, health_bar_rect)

    # Draw enemies
    for enemy in enemies:
        screen.blit(enemy.image, enemy.rect)

    # Draw player
    screen.blit(player_image, player_rect)

    # Draw projectiles
    for projectile in projectiles:
        screen.blit(projectile.image, projectile.rect)

    # Draw score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

    # Draw time remaining
    remaining_time = max(0, 120 - elapsed_time)
    time_text = font.render(f"Time: {int(remaining_time)}", True, (255, 255, 255))
    screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 40))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()


