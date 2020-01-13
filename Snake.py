from pygame import key
from pygame import Vector2
import pygame
import numpy as np

from enum import Enum
import os
from time import sleep

class BlockType(Enum):
    Air = 0
    Snake = 1
    Food = 2

Colors = {
    BlockType.Air : "O",
    BlockType.Snake : "X",
    BlockType.Food : "E",
}

class Cardinal(Enum):
    Up    = 0
    Right = 1
    Down  = 2
    Left  = 3

Directions = {
    Cardinal.Up    : Vector2(0, 1),
    Cardinal.Right : Vector2(1, 0),
    Cardinal.Down  : Vector2(0, -1),
    Cardinal.Left  : Vector2(-1, 0),
}


class Screen:
    def __init__(self, rows = 20, cols = 20):
        self.rows = rows
        self.cols = cols

        self.screen = np.ndarray(shape=(rows, cols), dtype=BlockType)
        self.screen.fill(BlockType.Air)

    def drawPixel(self, x, y, value):
        self.screen[x % self.rows, y % self.cols] = value

    def display(self):
        print()

        for x in range(self.screen.shape[0]):
            for y in range(self.screen.shape[1]):
                print(Colors[BlockType(self.screen[x, y])], end = " ")
            print()

        sleep(0.2)
        self.clear()

    def clear(self):
        self.screen.fill(BlockType.Air)

class Snake:
    def __init__(self):
        self.screen = screen
        self.segments = np.ndarray(shape=(1, 2), dtype=np.int8)
        self.segments[0] = [screen.cols / 2, screen.rows / 2]

        self.direction = Cardinal.Right
        
    def update(self):
        for segment in np.flip(self.segments, 0):
            pass


        self.segments[0] = self.segments[0] + Directions[self.direction]

        for segment in self.segments:
            screen.drawPixel(segment[0], segment[1], BlockType.Snake)

        if inputs.is_pressed("w"): self.direction = Cardinal.Up
        if inputs.is_pressed("d"): self.direction = Cardinal.Right
        if inputs.is_pressed("s"): self.direction = Cardinal.Down
        if inputs.is_pressed("a"): self.direction = Cardinal.Left

    def eat(self):
        pass

class Inputs:
    def __init__(self):
        self.keys = {}
        
    def is_pressed(self, key_code):
        return self.keys.get(key_code, False)

    def update(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            key = event.dict["key"]
            self.keys[key] = True if pygame.KEYDOWN else False

if __name__ == "__main__":
    pygame.init()

    screen = Screen()
    inputs = Inputs()
    snake = Snake()

    while(True):
        screen.display()
        snake.update()
        
        event = pygame.event.poll()
        inputs.update(event)
