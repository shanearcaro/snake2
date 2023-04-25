#!/usr/bin/env python3

from enum import Enum

class Action(Enum):
    """Actions that a snake can take"""
    NONE = 0
    STRAIGHT = 1
    LEFT = 2
    RIGHT = 3


class Direction(Enum):
    """Direction snake is moving"""
    NORTH = 0
    WEST = 1
    SOUTH = 2
    EAST = 3

def left(direction: Direction) -> Direction:
    """Returns the direction to the left of the given direction"""
    new_value = (direction.value + 1) % len(Direction)
    return Direction(new_value)

def right(direction: Direction) -> Direction:
    """Returns the direction to the right of the given direction"""
    new_value = (direction.value - 1) % len(Direction)
    return Direction(new_value)
