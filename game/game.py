#!/usr/bin/env python3

import pygame
import math
import random

from components.entity import Entity
from components.snake import Snake
from components.utils import Action, Direction

v = pygame.Vector2

class Game:
    def __init__(self, surface: pygame.Surface, head: Entity, body_color: tuple[int, int, int], fps: int = 12):
        self.surface = surface
        self.snake = Snake(head, body_color)
        self.size = head.size
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.board = self.generate_cells()
        self.apple = self.spawn_apple()
        self.vectors = self.board_vectors()
        self.sensors = self.generate_sensors(self.snake.head.position())

        pygame.init()

    def board_vectors(self):
        """Creates vectors surrounding the board of the game"""
        # Screen size
        width = self.surface.get_width()
        height = self.surface.get_height()

        # In direction of unit circle
        right = v(width - width, height - 0)
        top = v(width - 0, 0 - 0)
        left = v(0 - 0, height - 0)
        bottom = v(width - 0, height - height)

        # All edges of screen border as vectors
        return [right, top, left, bottom]

    def line_collision(self, line_start, line_end, entity: Entity):
        """Determine collision between a line and an entity"""
        rect = pygame.Rect(entity.x, entity.y, entity.size, entity.size)

        # Check if either endpoint of the line is inside the rectangle
        if rect.collidepoint(line_start) or rect.collidepoint(line_end):
            return True

        # Check if the line intersects with any of the four sides of the rectangle
        if rect.collidepoint(line_start[0], line_start[1] + 1) or rect.collidepoint(line_start[0], line_start[1] - 1):
            return True

        if rect.collidepoint(line_end[0], line_end[1] + 1) or rect.collidepoint(line_end[0], line_end[1] - 1):
            return True

        if rect.collidepoint(line_start[0] + 1, line_start[1]) or rect.collidepoint(line_start[0] - 1, line_start[1]):
            return True

        if rect.collidepoint(line_end[0] + 1, line_end[1]) or rect.collidepoint(line_end[0] - 1, line_end[1]):
            return True

        # Line does not intersect
        return False

    def generate_sensors(self, point) -> tuple[list[v], list[int]]:
        """Generate vectors from a point to the screen"""
        # Distances 8 directions
        distances = self.calculate_sensor_length(point)

        # Vectors for those distances
        vectors = []

        for i in range(0, 8):
            angle = 45 * i
            if i == 0 or i == 4:
                vector = v(distances[i], 0)
            elif i == 1 or i == 5:
                vector = v(0, -distances[i])
            elif i == 2 or i == 6:
                vector = v(-distances[i], 0)
            elif i == 3 or i == 7:
                vector = v(0, distances[i])
            vector.rotate_ip(angle)
            vector += point
            vectors.append(vector)
        return (vectors, distances)

    def sensor_data(self, point):
        """Generate the 24 sensor outputs"""
        sensors, distances = self.generate_sensors(point)
        apple_data = []
        entity_data = [0] * 8

        for i, sensor in enumerate(sensors):
            # Check if sensors collide with apple
            apple_data.append(int(pygame.draw.line(self.surface, (0, 0, 255), point, sensor, 1)
                              .colliderect((self.apple.x, self.apple.y, self.size, self.size))))

            for entity in self.snake.body:
                # Check if sensors intersect the snake body
                if entity != self.snake.head:
                    if pygame.draw.line(self.surface, (0, 0, 255), point, sensor).colliderect(
                            (entity.x, entity.y, self.size, self.size)):
                        entity_data[i] = 1
                        continue

        # Combine data and flatten
        output = list(zip(distances, apple_data, entity_data))
        return [element for sensor_point in output for element in sensor_point]

    def distance(self, start, end):
        return math.sqrt((end[1] - start[1])**2 + (end[0] - start[0])**2)

    def calculate_wall_distances(self, point) -> list[int]:
        """Calculate the ditances between the point and the screen in 8 directions"""
        x, y = point
        width, height = self.surface.get_width(), self.surface.get_height()
        distances = []

        # Calculate distance to edges
        distances.append(width - x)
        distances.append(math.sqrt((width - x - self.size)**2 + y**2))
        distances.append(y)
        distances.append(math.sqrt(x**2 + y**2))
        distances.append(x)
        distances.append(math.sqrt(x**2 + (height - y - self.size)**2))
        distances.append(height - y)
        distances.append(math.sqrt((width - x - self.size)**2 + (height - y - self.size)**2) + self.size)

        # Round distances
        distances = [math.ceil(distance) for distance in distances]

        return distances

    def calculate_sensor_length(self, point):
        # print("Calculate senor length point:", point)
        # print("HEAD POINT:", self.snake.head.position())
        # Distances to the walls from the current point
        wall_distances = self.calculate_wall_distances(point)
        # Distances to entity objects from the current point
        entity_collisions = self.calculate_entity_collision_points(point)

        entity_distances = [
            min([self.distance(point, collision) for collision in sensor], default=wall_distances[i])
            for i, sensor in enumerate(entity_collisions)
        ]

        return entity_distances

    def calculate_entity_collision_points(self, point) -> list[int]:
        """Calculate the collision points between the sensors and the body/apple"""
        x, y = point
        closest_points = [[] for _ in range(8)]

        # Get snake permissions without head
        positions = self.snake.all_positions()
        positions.append(self.apple.position())
        try:
            positions.remove(self.snake.head.position())
        except ValueError:
            pass

        # 0 degrees collision
        for x in range(int(point[0]), self.surface.get_width(), self.size):
            if (x, point[1]) in positions:
                closest_points[0].append((x, point[1]))
        x, y = point

        # 45 degrees collision
        while x > 0 and y > 0:
            if (x, y) in positions:
                closest_points[1].append((x, y))
            x += self.size
            y -= self.size
        x, y = point

        # 90 degrees collision
        for y in range(int(point[1]), 0, -self.size):
            if (point[0], y) in positions:
                closest_points[2].append((point[0], y))
        x, y = point

        # 135 degrees collision
        while x > 0 and y > 0:
            if (x, y) in positions:
                closest_points[3].append((x, y))
            x -= self.size
            y -= self.size
        x, y = point

        # 180 degrees collision
        for x in range(int(point[0]), 0, -self.size):
            if (x, point[1]) in positions:
                closest_points[4].append((x, point[1]))
        x, y = point

        # 225 degrees collision
        while x > 0 and y < self.surface.get_height():
            if (x, y) in positions:
                closest_points[5].append((x, y))
            x -= self.size
            y += self.size
        x, y = point

        # 270 degrees collision
        for y in range(int(point[1]), self.surface.get_height(), self.size):
            if (point[0], y) in positions:
                closest_points[6].append((point[0], y))
        x, y = point

        # 315 degrees collision
        while x < self.surface.get_width() and y < self.surface.get_height():
            if (x, y) in positions:
                closest_points[7].append((x, y))
            x += self.size
            y += self.size

        return closest_points

    def render_vectors(self, screen, point):
        points, _ = self.generate_sensors(point)
        for vector in points:
            # Draw vector in blue
            pygame.draw.line(screen, (0, 0, 255), point, vector, 1)

    def vector_intersection(self, vector1: v, vector2: v) -> v:
        """Determine the intersection point between 2 vectors"""
        # Calculate determinant and check if vectors are parallel
        determinant = vector1.x * vector2.y - vector1.y * vector2.x
        if determinant == 0:
            return None

        # Calculate intersection point
        dx = vector2.x - vector1.x
        dy = vector2.y - vector1.y

        t1 = (vector2.x * vector1.y - vector2.y * vector1.x) / determinant
        intersection_x = vector1.x + t1 * dx
        intersection_y = vector1.y + t1 * dy

        # Intersection vector
        return v(intersection_x, intersection_y)

    def generate_cells(self):
        """Generate the cell positions for the board"""
        board = []

        # Iterate through each position
        for col in range(0, self.surface.get_height() // self.size):
            for row in range(0, self.surface.get_width() // self.size):
                board.append((col * self.size, row * self.size))
        return board

    def in_bounds(self):
        """Verify the snake head is in bounds"""
        x, y = self.snake.head.position()
        width, height = self.surface.get_width(), self.surface.get_height()
        return 0 <= x < width and 0 <= y < height

    def available_positions(self):
        """Generate all positions not taken by the snake"""
        snake_pos = self.snake.positions()
        available = [position for position in self.board if position not in snake_pos]
        return available

    def spawn_apple(self):
        """Spawn an apple in one of the available screen positions"""
        available = self.available_positions()
        x, y = available[random.randrange(0, len(available))]
        return Entity(x, y, self.size, (255, 0, 0))

    def draw_apple(self):
        """Render the apple to the screen"""
        pygame.draw.rect(self.surface, self.apple.color, (self.apple.x, self.apple.y, self.apple.size, self.apple.size))

    def play(self):
        """Human interaction"""
        running = True
        pause = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        pause = not pause

            # Paint the screen black
            self.surface.fill("black")

            # Determine action from key pressed
            action = Action.NONE
            if not pause:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_w]:
                    action = Action.STRAIGHT
                elif keys[pygame.K_a]:
                    action = Action.LEFT
                elif keys[pygame.K_d]:
                    action = Action.RIGHT

            if not pause:
                # Set the action on the snake
                self.snake.move(action)

                if self.snake.is_eating(self.apple):
                    # If snake collides with apple, spawn new apple and add to snake
                    self.snake.add()
                    self.apple = self.spawn_apple()

                if self.snake.is_collision() or not self.in_bounds():
                    # If snake collides with itself, reset
                    self.snake.reset()
                    self.apple = self.spawn_apple()

                # Render the game
                self.snake.draw(self.surface)
                self.draw_apple()

                # self.render_vectors(self.surface, v(self.snake.head.x, self.snake.head.y))

                # Update the sensors
                # print("HEAD POINT:", self.snake.head.position())
                print("Sensors:", self.sensor_data(self.snake.head.position()))

                # Update game
                pygame.display.update()
                self.clock.tick(12)

        # Game has been exited
        pygame.quit()

# width, height = 800, 800
# screen = pygame.display.set_mode((width, height))
# game = Game(screen, Entity(width / 2, height / 2, 20, (0, 255, 0)), (255, 255, 255))
# game.play()
