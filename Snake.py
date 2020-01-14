from pygame import key
from pygame import Vector2
from pygame import surface
from pygame import gfxdraw
import pygame
import numpy as np

from enum import Enum
import os
from time import sleep
from time import time
from random import randrange

class BlockType(Enum):
    Air = 0
    Snake = 1
    Food = 2

Colors = {
    BlockType.Air : (255, 255, 255),
    BlockType.Snake : (0, 0, 0),
    BlockType.Food : (255, 0, 0),
}

class Cardinal(Enum):
    Up    = 0
    Right = 1
    Down  = 2
    Left  = 3

Directions = {
    Cardinal.Up    : Vector2(0, -1),
    Cardinal.Right : Vector2(1, 0),
    Cardinal.Down  : Vector2(0, 1),
    Cardinal.Left  : Vector2(-1, 0),
}

class Block:
    def __init__(self, type, food = None):
        self.type = type
        if type == BlockType.Food:
            self.food = food

class World:
    def __init__(self, resolution=(20, 20)):
        self.width = resolution[0]
        self.height = resolution[1]
        self.resolution = resolution

        self.foods = {}
        self.blocks = np.ndarray(shape=resolution, dtype=Block)
        self.blocks.fill(Block(BlockType.Air))

    def create_food(self):
        food = Food(self)
        while self.blocks[food.pos].type != BlockType.Air:
            food = Food(self)

        self.blocks[food.pos] = Block(BlockType.Food, food=food)
        
    def set_block(self, pos, type):
        pos = (pos[0] % self.width, pos[1] % self.height)
        self.blocks[pos] = Block(type)

    def get_block(self, pos):
        pos = (pos[0] % self.width, pos[1] % self.height)
        return self.blocks[pos[0], pos[1]]

class Screen:
    def __init__(self, world, res = (500, 500)):
        self.world = world

        self.blockSize = [r / g for (r, g) in zip(res, world.resolution)]
        self.gameDisplay = pygame.display.set_mode(res)

    def display(self):
        for x in range(self.world.width):
            for y in range(self.world.height):
                self.displayPixel(x, y, Colors[self.world.blocks[x, y].type])

        pygame.display.update()

    def displayPixel(self, x, y, value):
        x = x * self.blockSize[0]
        y = y * self.blockSize[1]
        pygame.draw.rect(self.gameDisplay, value, [x, y, self.blockSize[0], self.blockSize[1]])

class Inputs:
    def __init__(self):
        self.keys = {}
        
    def is_pressed(self, key_code):
        return self.keys.get(ord(key_code), False)

    def update(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            key = event.dict["key"]
            self.keys[key] = True if  event.type == pygame.KEYDOWN else False


class Snake:
    def __init__(self, screen, world, inputs, speed = 5):
        self.screen = screen
        self.world = world
        self.inputs = inputs

        self.moveMS = 1 / speed
        self.curTime = time()

        self.segments = np.ndarray(shape=(1, 2), dtype=np.int8)
        self.segments[0] = [world.width / 2, world.height / 2]

        self.direction = Cardinal.Right
        
    def update(self):
        if self.inputs.is_pressed("w") and self.direction != Cardinal.Down:  self.direction = Cardinal.Up
        if self.inputs.is_pressed("d") and self.direction != Cardinal.Left:  self.direction = Cardinal.Right
        if self.inputs.is_pressed("s") and self.direction != Cardinal.Up:    self.direction = Cardinal.Down
        if self.inputs.is_pressed("a") and self.direction != Cardinal.Right: self.direction = Cardinal.Left

        if(time() - self.curTime > self.moveMS):
            self.curTime = time()
            self.move()

    def move(self):
        for segment in np.flip(self.segments, 0):
            pass

        last_tail_pos = np.array(self.segments[-1])

        self.segments[0] = self.segments[0] + Directions[self.direction]
        headPos = self.segments[0]

        if(self.world.get_block(headPos).type == BlockType.Food):
            eat(headPos)

        self.draw(last_tail_pos)

    def draw(self, last_tail_pos):
        for segment in self.segments:
            self.world.set_block(segment, BlockType.Snake)

        self.world.set_block(last_tail_pos, BlockType.Air)

    def eat(self):
        pass #TODO


class Food:
    def __init__(self, world):
        self.pos = (randrange(0, world.width), randrange(0, world.height))


def main():
    pygame.init()

    world = World()
    screen = Screen(world)
    inputs = Inputs()
    snake = Snake(screen, world, inputs, 5)

    world.create_food()

    running = True
    while(running):
        snake.update()
        screen.display()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                inputs.update(event)


if __name__ == "__main__":
    main()