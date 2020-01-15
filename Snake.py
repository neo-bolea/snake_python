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
    BlockType.Air : [50] * 3,
    BlockType.Snake : [240] * 3,
    BlockType.Food : (200, 0, 0),
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

        self.blocks = np.ndarray(shape=resolution, dtype=Block)
        self.blocks.fill(Block(BlockType.Air))

    def update(self):
        pass

    def create_food(self):
        food = Food(self)
        while self.blocks[food.pos].type != BlockType.Air:
            food = Food(self)

        self.blocks[food.pos] = Block(BlockType.Food, food=food)
        
    def set_block(self, pos, type):
        pos = (pos[0] % self.width, pos[1] % self.height)
        self.blocks[int(pos[0]), int(pos[1])] = Block(type)

    def get_block(self, pos):
        pos = (pos[0] % self.width, pos[1] % self.height)
        return self.blocks[int(pos[0]), int(pos[1])]

    def clear_snake(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.blocks[x, y].type == BlockType.Snake:
                    self.blocks[x, y].type = BlockType.Air

class Screen:
    def __init__(self, world, res = (500, 500), ui_width = 50):
        gameDisplayResolution = res
        res = (res[0], res[1] + ui_width)
        self.ui_width = ui_width
        self.world = world

        self.blockSize = [r / g for (r, g) in zip(gameDisplayResolution, world.resolution)]
        self.gameDisplay = pygame.display.set_mode(res)

        pygame.font.init()
        self.font = pygame.font.Font("fonts/slkscr.ttf", 40)
        self.font_color = [240] * 3
        self.clear_color = [20] * 3

    def display(self):

        for x in range(self.world.width):
            for y in range(self.world.height):
                self.displayPixel(x, y, Colors[self.world.blocks[x, y].type])

        pygame.display.update()
        self.gameDisplay.fill(self.clear_color)


    def render_text(self, pos, text):
        label = self.font.render(text, 1, self.font_color)
        self.gameDisplay.blit(label, pos)

    def displayPixel(self, x, y, value):
        x = x * self.blockSize[0]
        y = y * self.blockSize[1] + self.ui_width
        pygame.draw.rect(self.gameDisplay, value, [x, y, self.blockSize[0], self.blockSize[1]])

    def draw_rect_min_max(self, min_corner, max_corner, color=[255] * 3):
        left = min_corner[0]
        top = max_corner[1]
        width = max_corner[0] - min_corner[0]
        height = max_corner[1] - min_corner[1]
        pygame.draw.rect(self.gameDisplay, color, pygame.Rect(left, top, width, height))

class Inputs:
    def __init__(self):
        self.keys = {}
        
    def is_pressed(self, key_code):
        if key_code.isdigit():
            key = int(key_code)
        else:
            key = ord(key_code)
        return self.keys.get(key, False)

    def update(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            key = event.dict["key"]
            self.keys[key] = True if  event.type == pygame.KEYDOWN else False


class Snake:
    class Controls:
        def __init__(self, up, right, down, left):
            self.up    = np.array([up]).flatten()
            self.down  = np.array([down]).flatten()
            self.left  = np.array([left]).flatten()
            self.right = np.array([right]).flatten()
            self.inputs = None

        def is_pressed(self, direction):
            for dir in direction:
                if self.inputs.is_pressed(dir):
                    return True

            return False

    def __init__(self, screen, world, inputs, speed = 5, 
                 controls = Controls('w', 'd', 's', 'a'), ui_pos = (10, 10)):
        self.screen = screen
        self.world = world
        self.inputs = inputs
        self.controls = controls
        self.controls.inputs = self.inputs

        self.moveMS = 1 / speed
        self.curTime = time()

        self.segments = np.ndarray(shape=(1, 2), dtype=np.int8)
        self.segments[0] = [world.width / 2, world.height / 2]

        self.direction = Cardinal.Right
        self.last_direction = self.direction
        self.last_tail_pos = self.segments[0]

        self.score = 0
        self.ui_pos = ui_pos
        
    def update(self):
        if self.controls.is_pressed(self.controls.up) and self.last_direction != Cardinal.Down: self.direction = Cardinal.Up
        if self.controls.is_pressed(self.controls.right) and self.last_direction != Cardinal.Left: self.direction = Cardinal.Right
        if self.controls.is_pressed(self.controls.down) and self.last_direction != Cardinal.Up: self.direction = Cardinal.Down
        if self.controls.is_pressed(self.controls.left) and self.last_direction != Cardinal.Right: self.direction = Cardinal.Left

        snakeLives = True
        if(time() - self.curTime > self.moveMS):
            self.curTime = time()
            snakeLives = self.check_events()
            self.move()

        self.world.clear_snake()
        self.update_in_world()

        self.display_score()

        return snakeLives

    def check_events(self):
        nextPos = self.segments[0] + Directions[self.direction]
        next_block = self.world.get_block(nextPos) 
        self.check_for_food(next_block)
        return not self.check_for_death(nextPos, next_block)

    def check_for_food(self, nextBlock):
        if(nextBlock.type == BlockType.Food):
            self.eat()

    def check_for_death(self, nextPos, next_block):
        if nextPos[0] == self.segments[-1][0] and nextPos[1] == self.segments[-1][1]:
            return False
        return next_block.type == BlockType.Snake

    def move(self):
        self.last_tail_pos = np.array(self.segments[-1])

        for s in range(len(self.segments) - 1, 0, -1):
            self.segments[s] = self.segments[s - 1]

        self.segments[0] = self.segments[0] + Directions[self.direction]
        self.last_direction = self.direction

        
    def reset(self):
        main()

    def update_in_world(self):
        for segment in self.segments:
            self.world.set_block(segment, BlockType.Snake)

    def eat(self):
        self.world.set_block(self.segments[0], BlockType.Air)
        self.add_segment()
        self.world.create_food()

        self.score = self.score + 1

    def add_segment(self):
        self.segments = np.append(self.segments, [self.last_tail_pos], 0)

    def display_score(self):
        self.screen.render_text(self.ui_pos, str(self.score))

class Food:
    def __init__(self, world):
        self.pos = (randrange(0, world.width), randrange(0, world.height))

class UI:
    class Button:
        def __init__(self, screen, min_corner, max_corner, action, color = [255] * 3):
            self.min_corner = min_corner
            self.max_corner = max_corner
            self.action = action

            self.screen = screen
            self.color = color

        def is_pressed(self, mouse_pos):
            return mouse_pos[0] > self.min_corner[0] and \
                mouse_pos[0] <= self.max_corner[0] and \
                mouse_pos[1] > self.min_corner[1] and \
                mouse_pos[1] <= self.max_corner[1]

    def __init__(self):
        self.buttons = np.ndarray(shape=(0), dtype=UI.Button)

    def add_button(self, button):
        np.append(self.buttons, button)

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            self.on_left_click(mouse_pos)

        for button in self.buttons:
            self.screen.draw_rect_min_max(button.min_corner, button.max_corner, button.color)

    def on_left_click(self, mouse_pos):
        for button in self.buttons:
            if button.is_pressed(mouse_pos):
                button.action()
                return

class Program:
    def __init__(self):
        self.inputs = Inputs()
        self.ui = UI()
        self.reset()

        self.ui.add_button(Button((20, 20), (30, 30), action)

    def action(self):
        print("Clicked!")

    def reset(self):
        self.world = World()
        self.screen = Screen(self.world)
        self.snake = Snake(self.screen, self.world, self.inputs, speed=5, 
            controls=Snake.Controls(
                ['w', pygame.K_UP], ['d', pygame.K_RIGHT], 
                ['s', pygame.K_DOWN], ['a', pygame.K_LEFT]))

        #self.snake2 = Snake(self.screen, self.world, self.inputs, speed=5, 
        #    controls=Snake.Controls(
        #        ['w', pygame.K_UP], ['d', pygame.K_RIGHT], 
        #        ['s', pygame.K_DOWN], ['a', pygame.K_LEFT]))

        self.world.create_food()

    def start(self):
        pygame.init()

        running = True
        while(running):
            self.world.update()
            gameOver = not self.snake.update()
            if gameOver:
                self.reset()
            self.screen.display()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.inputs.update(event)
                    self.ui.update(event)

if __name__ == "__main__":
    program = Program()
    program.start()