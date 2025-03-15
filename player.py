import pygame
import math


class Player(pygame.sprite.Sprite):
    def __init__(self, car_image, x, y, rotations=360):
        """A car Sprite which pre-rotates up to <rotations> lots of
        angled versions of the image.  Depending on the sprite's
        heading-direction, the correctly angled image is chosen.
        The base car-image should be pointing North/Up."""
        pygame.sprite.Sprite.__init__(self)
        self.rot_img = []
        self.min_angle = 360 / rotations
        for i in range(rotations):
            # This rotation has to match the angle in radians later
            # So offet the angle (0 degrees = "north") by 90° to be angled 0-radians (so 0 rad is "east")
            rotated_image = pygame.transform.rotozoom(
                car_image, 360 - 90 - (i * self.min_angle), 0.175
            )  # Reduce scale to 0.5
            self.rot_img.append(rotated_image)
        self.min_angle = math.radians(self.min_angle)
        self.image = self.rot_img[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        # movement
        self.reversing = False
        self.heading = 0
        self.speed = 0
        self.velocity = pygame.math.Vector2(0, 0)
        self.position = pygame.math.Vector2(x, y)
        self.screen_width = pygame.display.get_surface().get_width()
        self.screen_height = pygame.display.get_surface().get_height()

    def turn(self, angle_degrees):
        # Adjust the angle the car is heading, if this means using a different car-image, select that here too
        if self.speed != 0:
                
            self.heading += math.radians(angle_degrees)
            # Decide which is the correct image to display
            image_index = int(self.heading / self.min_angle) % len(self.rot_img)
            # Only update the image if it's changed
            if self.image != self.rot_img[image_index]:
                x, y = self.rect.center
                self.image = self.rot_img[image_index]
                self.rect = self.image.get_rect()
                self.rect.center = (x, y)

    def accelerate(self, amount):
        # Increase the speed either forward or reverse
        if self.speed >= -4 and self.speed <= 10:
            self.speed += amount

    def brake(self):
        # Slow the car until it stops
        if self.speed > 0:
            self.speed -= 0.45
        if self.speed < 0:
            self.speed += 0.45
        if abs(self.speed) < 0.1:
            self.speed = 0

    def update(self):
        # Sprite update function, calcualtes any new position
        self.velocity.from_polar((self.speed, math.degrees(self.heading)))
        self.position += self.velocity
        self.rect.center = (round(self.position[0]), round(self.position[1]))
        # Car loses speed over time
        if self.speed > 0:
            self.speed -= 0.05
        if self.speed < 0:
            self.speed += 0.05

        # Collision detection
        if self.rect.left < 0:
            self.rect.left = 0
            self.position.x = self.rect.centerx
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width
            self.position.x = self.rect.centerx
        if self.rect.top < 0:
            self.rect.top = 0
            self.position.y = self.rect.centery
        if self.rect.bottom > self.screen_height:
            self.rect.bottom = self.screen_height
            self.position.y = self.rect.centery
