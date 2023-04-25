#!/usr/bin/env python3

from game.game import Game
from components.snake import Snake
from components.entity import Entity
from components.utils import Action, Direction

import pygame
import pickle
import neat
import math
import os

def save_generation(generation, generation_num, save_folder):
    # Create the folder if it doesn't exist
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Save the generation to a file
    filename = os.path.join(save_folder, f"generation_{generation_num}.pkl")
    with open(filename, "wb") as f:
        pickle.dump(generation, f)

def evaluate_fitness(genome, config):
    width, height = 420, 420
    screen = pygame.display.set_mode((width, height))
    game = Game(screen, Entity(200, 200, 20, (0, 255, 0)), (255, 255, 255), fps=15)
    network = neat.nn.FeedForwardNetwork.create(genome, config)
    frames = 0
    max_moves = 50
    debuff = 0

    max_length = math.sqrt(width**2 + height**2)

    while game.snake.is_alive:
        frames += 1
        max_moves -= 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.snake.is_alive = False
                break

        game.surface.fill("black")

        game.snake.draw(game.surface)
        game.draw_apple()

        game.clock.tick(game.fps)

        inputs = game.sensor_data(game.snake.head.position())
        # print("Sensors:", inputs)
        output = network.activate(inputs)
        # print("OUTPUT:", output)
        action = output.index(max(output))
        # print("ACTION:", action)
        # print()
        pygame.display.update()

        if action == 0:
            action = Direction.EAST
        elif action == 1:
            action = Direction.NORTH
        elif action == 2:
            action = Direction.WEST
        else:
            action = Direction.SOUTH

        game.snake.direction(action)
        if game.snake.is_eating(game.apple):
            # If snake collides with apple, spawn new apple and add to snake
            game.snake.add()
            game.apple = game.spawn_apple()
            max_moves = 200

        if not game.in_bounds():
            debuff = 2000
            game.snake.is_alive = False
            break

        if game.snake.is_collision():
            # If snake collides with itself, reset
            game.snake.is_alive = False
            break
            # game.snake.reset()
            # game.apple = game.spawn_apple()

        if max_moves == 0:
            game.snake.is_alive = False
            break

    pygame.quit()
    return game.snake.length * 500 + frames ** 2 + max_length - game.distance(game.snake.head.position(), game.apple.position()) - debuff

def evaluate_genomes(genomes, config):
    for genome_id, genome in genomes:
        fitness = evaluate_fitness(genome, config)
        genome.fitness = fitness
        print(f"Fitness[{genome_id}]:", fitness)

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(evaluate_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    parent = os.getcwd()
    config_path = os.path.join(parent + '/config', 'config-feedforward2.txt')
    run(config_path)
