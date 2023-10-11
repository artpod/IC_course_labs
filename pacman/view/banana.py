import pygame


class Banana(pygame.sprite.Sprite):
    def __init__(self, size):
        super(Banana, self).__init__()
        image = pygame.image.load('view/sprites/banana.png')
        image = pygame.transform.scale(image, (size, size))
        self.image = image

        self.surf = pygame.Surface((size, size))
        self.surf.fill((255, 255, 0))
        self.rect = self.surf.get_rect()
        self.rotation = 0

        if size < 8:
            self.image = self.surf


