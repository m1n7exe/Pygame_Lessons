import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hollow Knight Clone | Arrow Keys: Move, Space: Jump, Z: Attack, Up+Z: Upward Slash")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (20, 20, 20)
LIGHT_GRAY = (100, 100, 100)
BLUE = (0, 0, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 60), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 4, HEIGHT // 2)
        self.velocity_y = 0
        self.jumping = False
        self.health = 5
        self.attacking = False
        self.attack_cooldown = 0
        self.facing_right = True
        self.animation_count = 0
        self.slash_rect = pygame.Rect(0, 0, 0, 0)
        self.hit_pause = 0
        self.slash_animation = []
        self.slash_frame = 0
        self.invincibility = 0
        self.flicker = False
        self.blade_pos = 0
        self.slashing_upward = False

    def animate(self):
        self.image.fill((0, 0, 0, 0))
        
        # Body (capsule shape)
        pygame.draw.ellipse(self.image, BLACK, (5, 10, 30, 50))
        pygame.draw.rect(self.image, BLACK, (5, 30, 30, 20))
        
        # White outline
        pygame.draw.ellipse(self.image, WHITE, (5, 10, 30, 50), 2)
        pygame.draw.rect(self.image, WHITE, (5, 30, 30, 20), 2)
        
        # Eyes
        eye_x = 25 if self.facing_right else 15
        pygame.draw.circle(self.image, WHITE, (eye_x, 25), 5)

        # Blade
        blade_x = 35 if self.facing_right else 5
        blade_y = 30 + self.blade_pos
        pygame.draw.line(self.image, WHITE, (blade_x, blade_y), (blade_x, blade_y + 20), 2)

    def create_slash_animation(self):
        self.slash_animation = []
        for i in range(10):
            slash = pygame.Surface((120, 60), pygame.SRCALPHA)
            arc_rect = pygame.Rect(0, 0, 120, 60)
            if self.slashing_upward:
                start_angle = math.pi * 3/2
                end_angle = math.pi * 5/2
            else:
                start_angle = 0 if self.facing_right else math.pi
                end_angle = math.pi if self.facing_right else math.pi * 2
            pygame.draw.arc(slash, WHITE, arc_rect, start_angle, end_angle, 10 - i)
            self.slash_animation.append(slash)

    def update(self):
        if self.hit_pause > 0:
            self.hit_pause -= 1
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
            self.facing_right = True
        if keys[pygame.K_SPACE] and not self.jumping:
            self.velocity_y = -15
            self.jumping = True
        if keys[pygame.K_z] and self.attack_cooldown == 0:
            self.attacking = True
            self.attack_cooldown = 30
            self.slashing_upward = keys[pygame.K_UP]
            self.create_slash_animation()
            self.slash_frame = 0
            self.blade_pos = -10

        self.velocity_y += 0.8
        self.rect.y += self.velocity_y

        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.jumping = False

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if self.attacking:
            self.slash_frame += 1
            self.blade_pos += 4
            if self.slash_frame >= len(self.slash_animation):
                self.attacking = False
                self.slash_frame = 0
            if self.slashing_upward:
                self.slash_rect = pygame.Rect(self.rect.centerx - 30, self.rect.top - 60, 60, 60)
            elif self.facing_right:
                self.slash_rect = pygame.Rect(self.rect.right, self.rect.top - 10, 120, 60)
            else:
                self.slash_rect = pygame.Rect(self.rect.left - 120, self.rect.top - 10, 120, 60)
        else:
            self.slash_rect = pygame.Rect(0, 0, 0, 0)
            self.blade_pos = max(0, self.blade_pos - 2)

        if self.invincibility > 0:
            self.invincibility -= 1
            self.flicker = not self.flicker

        self.animate()
        self.rect.clamp_ip(screen.get_rect())

    def draw(self, surface):
        if self.invincibility == 0 or self.flicker:
            surface.blit(self.image, self.rect)
        if self.attacking and self.slash_frame < len(self.slash_animation):
            if self.slashing_upward:
                slash_x = self.rect.centerx - 30
                slash_y = self.rect.top - 60
            elif self.facing_right:
                slash_x = self.rect.right
                slash_y = self.rect.top - 10
            else:
                slash_x = self.rect.left - 120
                slash_y = self.rect.top - 10
            slash_surf = self.slash_animation[self.slash_frame]
            if self.slashing_upward:
                slash_surf = pygame.transform.rotate(slash_surf, 90)
            elif not self.facing_right:
                slash_surf = pygame.transform.flip(slash_surf, True, False)
            surface.blit(slash_surf, (slash_x, slash_y))

    def get_hit(self):
        if self.invincibility == 0:
            self.health -= 1
            self.hit_pause = 10
            self.invincibility = 90

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = 1
        self.speed = random.randint(1, 3)
        self.animation_count = 0

    def animate(self):
        self.image.fill((0, 0, 0, 0))
        
        if self.enemy_type == "crawler":
            # Crawler enemy (similar to previous insect-like enemy)
            pygame.draw.ellipse(self.image, LIGHT_GRAY, (10, 10, 30, 40))
            leg_offset = abs(math.sin(self.animation_count * 0.2)) * 5
            pygame.draw.line(self.image, LIGHT_GRAY, (15, 30), (5, 40 + leg_offset), 2)
            pygame.draw.line(self.image, LIGHT_GRAY, (35, 30), (45, 40 - leg_offset), 2)
            pygame.draw.line(self.image, LIGHT_GRAY, (15, 40), (5, 50 - leg_offset), 2)
            pygame.draw.line(self.image, LIGHT_GRAY, (35, 40), (45, 50 + leg_offset), 2)
            eye_x = 30 if self.direction > 0 else 20
            pygame.draw.circle(self.image, WHITE, (eye_x, 20), 5)
            pygame.draw.circle(self.image, BLACK, (eye_x + (2 if self.direction > 0 else -2), 20), 2)
        
        elif self.enemy_type == "flyer":
            # Flying enemy
            wing_offset = abs(math.sin(self.animation_count * 0.4)) * 10
            pygame.draw.ellipse(self.image, RED, (10, 20, 30, 20))
            pygame.draw.polygon(self.image, RED, [(10, 30), (0, 30 - wing_offset), (0, 30 + wing_offset)])
            pygame.draw.polygon(self.image, RED, [(40, 30), (50, 30 - wing_offset), (50, 30 + wing_offset)])
            pygame.draw.circle(self.image, WHITE, (35 if self.direction > 0 else 15, 25), 5)
        
        elif self.enemy_type == "shooter":
            # Shooting enemy
            pygame.draw.rect(self.image, GREEN, (10, 10, 30, 30))
            pygame.draw.rect(self.image, BLACK, (15, 15, 20, 20))
            pygame.draw.line(self.image, GREEN, (25, 40), (25, 50), 3)

    def update(self):
        if self.enemy_type == "crawler":
            self.rect.x += self.speed * self.direction
            if self.rect.left < 0 or self.rect.right > WIDTH:
                self.direction *= -1
        elif self.enemy_type == "flyer":
            self.rect.x += self.speed * self.direction
            self.rect.y += math.sin(self.animation_count * 0.1) * 2
            if self.rect.left < 0 or self.rect.right > WIDTH:
                self.direction *= -1
        elif self.enemy_type == "shooter":
            if random.random() < 0.01:  # 1% chance to shoot each frame
                self.shoot()
        
        self.animation_count += 1
        self.animate()

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.centery)
        all_sprites.add(bullet)
        bullets.add(bullet)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(DARK_GRAY)
        pygame.draw.line(self.image, LIGHT_GRAY, (0, 0), (width, 0), 3)
        for i in range(0, width, 20):
            pygame.draw.line(self.image, LIGHT_GRAY, (i, 0), (i, 10), 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Sprite Groups
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Create platforms
platform_list = [(0, HEIGHT - 40, WIDTH, 40),
                 (WIDTH // 2 - 50, HEIGHT * 3 // 4, 100, 20),
                 (WIDTH // 4 - 50, HEIGHT // 2, 100, 20),
                 (WIDTH * 3 // 4 - 50, HEIGHT // 2, 100, 20)]

for plat in platform_list:
    p = Platform(*plat)
    all_sprites.add(p)
    platforms.add(p)

def spawn_enemy():
    enemy_type = random.choice(["crawler", "flyer", "shooter"])
    e = Enemy(random.randint(0, WIDTH), random.randint(0, HEIGHT - 100), enemy_type)
    all_sprites.add(e)
    enemies.add(e)

for _ in range(5):
    spawn_enemy()

# Game loop
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
running = True
enemy_spawn_timer = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()

    if player.velocity_y > 0:
        hits = pygame.sprite.spritecollide(player, platforms, False)
        if hits:
            player.rect.bottom = hits[0].rect.top
            player.velocity_y = 0
            player.jumping = False

    enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
    if enemy_hits and player.invincibility == 0:
        player.get_hit()
        if player.health <= 0:
            running = False

    bullet_hits = pygame.sprite.spritecollide(player, bullets, True)
    if bullet_hits and player.invincibility == 0:
        player.get_hit()
        if player.health <= 0:
            running = False

    if player.attacking:
        for enemy in enemies:
            if player.slash_rect.colliderect(enemy.rect):
                enemies.remove(enemy)
                all_sprites.remove(enemy)
                player.hit_pause = 5

    enemy_spawn_timer += 1
    if enemy_spawn_timer >= 180:
        spawn_enemy()
        enemy_spawn_timer = 0

    screen.fill(BLACK)
    
    for i in range(0, WIDTH, 100):
        pygame.draw.line(screen, DARK_GRAY, (i, 0), (i, HEIGHT), 2)
    for i in range(0, HEIGHT, 100):
        pygame.draw.line(screen, DARK_GRAY, (0, i), (WIDTH, i), 2)

    all_sprites.draw(screen)
    player.draw(screen)

    for i in range(player.health):
        mask_img = pygame.Surface((20, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(mask_img, WHITE, (0, 0, 20, 30))
        screen.blit(mask_img, (10 + i * 25, 10))

    spotlight = pygame.Surface((200, 200), pygame.SRCALPHA)
    pygame.draw.circle(spotlight, (255, 255, 255, 10), (100, 100), 100)
    screen.blit(spotlight, (player.rect.centerx - 100, player.rect.centery - 100))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
