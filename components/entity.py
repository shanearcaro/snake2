#!/usr/bin/env python3

from components.utils import Direction
import pygame

class Entity:
    """Building block of a Snake"""

    def __init__(self, x: int, y: int, size: int, color: tuple[int, int, int]):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.direction = None

    def move(self):
        """Move entity in current direction"""
        x, y = self.position()
        d = self.direction
        s = self.size

        # Move the entity
        if d == Direction.NORTH:
            y -= s
        elif d == Direction.SOUTH:
            y += s
        elif d == Direction.EAST:
            x += s
        else:
            x -= s

        # Update location
        self.x = x
        self.y = y

    def draw(self, surface):
        """Render the entity to the screen"""
        pygame.draw.rect(surface, self.color, rect=(self.x, self.y, self.size, self.size))

    def draw_direction(self, surface):
        """Render the direction each entity is facing"""
        font = pygame.font.Font(pygame.font.get_default_font(), 25)

        text = 'N'
        if self.direction == Direction.SOUTH:
            text = 'S'
        elif self.direction == Direction.WEST:
            text = 'W'
        elif self.direction == Direction.EAST:
            text = 'E'
        # now print the text
        text_surface = font.render(text, False, (0, 0, 0), None)
        surface.blit(text_surface, dest=(self.x, self.y))

    def position(self):
        """Return entity's coordinates"""
        return (self.x, self.y)
