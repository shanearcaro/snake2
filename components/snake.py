#!/usr/bin/env python3

from components.entity import Entity
from components.utils import Action, Direction
from components.utils import left, right

class Snake:
    def __init__(self, head: Entity, body_color: tuple[int, int, int]):
        self.head = head
        self.start_x = head.x
        self.start_y = head.y
        self.tail = head
        self.body = [self.head]
        self.body_color = body_color
        self.length = 1
        self.fitness = 0
        self.moving = False
        self.is_alive = True

    def draw(self, surface):
        """Render all elements of the snake onto the surface"""
        for entity in self.body:
            entity.draw(surface)

    def move(self, action: Action):
        """Move the snake with the new action"""
        if action == Action.NONE and not self.moving:
            return
        direction = None

        if not self.moving:
            self.moving = True

            # Put direction in default state
            direction = Direction.NORTH

            # Check directions left and right
            if action == Action.LEFT:
                direction = Direction.WEST
            elif action == Action.RIGHT:
                direction = Direction.EAST
        else:
            # Set to head's direction
            direction = self.head.direction

            # Check actions left and right
            if action == Action.LEFT:
                direction = left(direction)
            elif action == Action.RIGHT:
                direction = right(direction)

        # Set new head direction and position
        # Need to update direction then move
        self.head.direction = direction
        self.head.move()

        for i in range(len(self.body) - 1, 0, -1):
            entity = self.body[i]
            # If not the head element
            if entity != self.head:
                neighbor = self.body[i - 1]

                # Move entity then update direction
                entity.move()
                entity.direction = neighbor.direction

    def direction(self, action: Direction):
        """Move the snake with the new action"""
        if action is None and not self.moving:
            return

        if not self.moving:
            self.moving = True

        # Set new head direction and position
        # Need to update direction then move
        self.head.direction = action
        self.head.move()

        for i in range(len(self.body) - 1, 0, -1):
            entity = self.body[i]
            # If not the head element
            if entity != self.head:
                neighbor = self.body[i - 1]

                # Move entity then update direction
                entity.move()
                entity.direction = neighbor.direction

    def positions(self):
        """Get all snake body positions"""
        return [entity.position() for entity in self.body]

    def all_positions(self):
        body = self.body[1:]
        s = self.head.size

        positions = []
        for entity in body:
            x, y = entity.position()
            positions.append((x, y))
            positions.append((x + s, y))
            positions.append((x, y + s))
            positions.append((x + s, y + s))
        return positions

    def add(self):
        """Add an element to the snake"""
        x, y = self.tail.position()
        size = self.tail.size
        td = self.tail.direction

        # Spawn tail in opposite direction tail is going
        if (td == Direction.NORTH):
            y += size
        elif (td == Direction.SOUTH):
            y -= size
        elif (td == Direction.EAST):
            x -= size
        else:
            x += size

        # Create enttiy in correct location
        entity = Entity(x, y, size, self.body_color)
        entity.direction = td

        # Update snake attributes
        self.body.append(entity)
        self.tail = entity
        self.length += 1

    def reset(self):
        """Reset the snake's state to default"""
        # Reset head position
        self.head.x = self.start_x
        self.head.y = self.start_y

        # Remove all body elements reset snake attributes
        self.body = [self.head]
        self.tail = self.head
        self.length = 1
        self.fitness = 0

        # Stop snake from moving on reset
        self.moving = False

    def is_collision(self):
        """Verify if the head has collided with the body"""
        head_position = self.head.position()
        body_positions = [entity.position() for entity in self.body if entity != self.head]

        # If head is in same position as body element
        return head_position in body_positions

    def is_eating(self, apple: Entity):
        """Verify if the snake has collided with the apple"""
        return self.head.position() == apple.position()
