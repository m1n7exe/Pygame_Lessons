from player import Player
import pygame
import math

pygame.init()

# Creating window
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Orange car - IJKL, SPACE to brake | White van - WASD, LSHIFT to brake')
background_colour = (46, 143, 61)
screen.fill(background_colour)

# Load images
race_line = pygame.image.load("images/race_line.png")
orange_muscle = pygame.image.load("images/orange_muscle.png")
white_van = pygame.image.load("images/white_van.png")
track_image = pygame.image.load("images/track.png")

# Scale sprites 
track_image = pygame.transform.scale(track_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
race_line = pygame.transform.scale(race_line, (66, 110))

# Sprites
player1 = Player(orange_muscle, 300, 180)
player2 = Player(white_van, 300, 222)

# Sprite groups
all_sprites = pygame.sprite.Group()
all_sprites.add(player1)
all_sprites.add(player2)

# Setup variables
run = True

while run:
    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        player1.brake()
    else:
        if keys[pygame.K_i]:
            player1.accelerate(0.25)
        if keys[pygame.K_k]:
            player1.accelerate(-0.15)

    if keys[pygame.K_j]:
        player1.turn(-4)
    if keys[pygame.K_l]:
        player1.turn(4)
    
    if keys[pygame.K_LSHIFT]:
        player2.brake()
    else:
        if keys[pygame.K_w]:
            player2.accelerate(0.25)
        if keys[pygame.K_s]:
            player2.accelerate(-0.15)

    if keys[pygame.K_a]:
        player2.turn(-4)
    if keys[pygame.K_d]:
        player2.turn(4)

    # Updates
    screen.fill(background_colour)
    screen.blit(track_image, (0, 0))  # Draw the scaled track image
    screen.blit(race_line, (315, 147))

    all_sprites.update()
    all_sprites.draw(screen)

    pygame.display.update()
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()