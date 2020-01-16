import numpy as np
from PIL import Image
import pygame

from random import randrange

from collections import deque
from enum import Enum
from time import time

class KeyState(Enum):
    Up = 0
    Down = 1
    Pressed = 2
    Released = 3
        
class Inputs:
    def __init__(self):
        self.keys = {}

    def update(self):
        for (key, state) in self.keys.items():
            if state == KeyState.Pressed: 
                self.keys[key] = KeyState.Down
            elif state == KeyState.Released: self.keys[key] = KeyState.Up
        
    def on_event(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            key = event.dict["key"]
            self.keys[key] = KeyState.Pressed if event.type == pygame.KEYDOWN else KeyState.Released

    def process_key(self, key_code):
        if isinstance(key_code, np.int32): return key_code
        elif key_code.isdigit(): return int(key_code)
        else: return ord(key_code)

    def get_key_state(self, key_code):
        key = self.process_key(key_code)
        return self.keys.get(key, KeyState.Up)

    def is_up(self, key_code):
        return self.get_key_state(key_code) == KeyState.Up

    def is_down(self, key_code):
        return self.get_key_state(key_code) == KeyState.Down
        
    def is_pressed(self, key_code):
        return self.get_key_state(key_code) == KeyState.Pressed

    def is_released(self, key_code):
        return self.get_key_state(key_code) == KeyState.Released


class Screen:
    def __init__(self, world, ui, resolution=(500, 500), ui_width=50):
        self.ui = UI(self)
        self.world = world
        self.set_resolution(resolution, ui_width)

        self.font = pygame.font.Font("fonts/slkscr.ttf", 40)
        self.font_color = [240] * 3
        self.clear_color = [20] * 3

    def set_resolution(self, resolution, ui_width=None):
        if ui_width: self.ui_width = ui_width

        gameDisplayResolution = resolution
        resolution = (resolution[0], resolution[1] + ui_width)

        self.blockSize = [r / g for (r, g) in zip(gameDisplayResolution, world.resolution)]
        self.gameDisplay = pygame.display.set_mode(resolution)

    def display(self):
        for x in range(self.world.width):
            for y in range(self.world.height):
                self.display_pixel(x, y, self.world.blocks[x, y].color)

        self.ui.update()
        pygame.display.update()
        self.gameDisplay.fill(self.clear_color)

    def on_event(self, event):
        self.ui.on_event(event)

    def render_text(self, pos, text, color=None):
        if not color: color = self.font_color
        label = self.font.render(text, 1, color)
        self.gameDisplay.blit(label, pos)

    def display_pixel(self, x, y, value):
        x = x * self.blockSize[0]
        y = y * self.blockSize[1] + self.ui_width
        pygame.draw.rect(self.gameDisplay, value, [x, y, self.blockSize[0], self.blockSize[1]])

    def draw_rect_min_max(self, min_corner, max_corner, color=[255] * 3):
        left = min_corner[0]
        top = min_corner[1]
        width = max_corner[0] - min_corner[0]
        height = max_corner[1] - min_corner[1]
        pygame.draw.rect(self.gameDisplay, color, pygame.Rect(left, top, width, height))


class UI:
    class Button:
        def __init__(self, text, pos, action, max_size=None, square=False, bg_color=[0]*3, text_color=[255]*3):
            self.text = text
            self.pos = pos
            self.square = square
            self.max_size = max_size
            self.action = action
            self.bg_color = bg_color
            self.text_color = text_color

        def set_font(self, font):
            orig_size = font.size(self.text)
            size = orig_size
            if self.max_size != None:
                size = tuple(max(s, m) for s, m in zip(size, self.max_size))
            if self.square:
                max_side = max(size)
                size = [max_side] * len(size)
            
            self.text_corner = tuple(p - s / 2 for p, s in zip(self.pos, orig_size))
            self.min_corner = tuple(p - s / 2 for p, s in zip(self.pos, size))
            self.max_corner = tuple(p + s / 2 for p, s in zip(self.pos, size))

        def is_pressed(self, mouse_pos):
            return mouse_pos[0] > self.min_corner[0] and \
                mouse_pos[0] <= self.max_corner[0] and \
                mouse_pos[1] > self.min_corner[1] and \
                mouse_pos[1] <= self.max_corner[1]

    def __init__(self, screen):
        self.screen = screen
        self.buttons = np.ndarray(shape=(0), dtype=UI.Button)

    def add_button(self, button):
        self.buttons = np.append(self.buttons, button)
        button.set_font(self.screen.font)
        return button

    def on_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            self.on_left_click(mouse_pos)

    def update(self):
        for button in self.buttons:
            self.screen.draw_rect_min_max(button.min_corner, button.max_corner, button.bg_color)
            self.screen.render_text(button.text_corner, button.text, button.text_color)

    def on_left_click(self, mouse_pos):
        for button in self.buttons:
            if button.is_pressed(mouse_pos):
                button.action()
                return


class Screen:
    def __init__(self, world, resolution=(500, 500), ui_width=50):
        self.ui = UI(self)
        self.world = world
        self.set_resolution(resolution, ui_width)

        self.font = pygame.font.Font("fonts/slkscr.ttf", 40)
        self.font_color = [240] * 3
        self.clear_color = [20] * 3

    def set_resolution(self, resolution, ui_width=None):
        if ui_width: self.ui_width = ui_width

        gameDisplayResolution = resolution
        resolution = (resolution[0], resolution[1] + ui_width)

        self.blockSize = [r / g for (r, g) in zip(gameDisplayResolution, self.world.resolution)]
        self.gameDisplay = pygame.display.set_mode(resolution)

    def display(self):
        for x in range(self.world.width):
            for y in range(self.world.height):
                self.display_pixel(x, y, self.world.blocks[x, y].color)

        self.ui.update()
        pygame.display.update()
        self.gameDisplay.fill(self.clear_color)

    def on_event(self, event):
        self.ui.on_event(event)

    def render_text(self, pos, text, color=None):
        if not color: color = self.font_color
        label = self.font.render(text, 1, color)
        self.gameDisplay.blit(label, pos)

    def display_pixel(self, x, y, value):
        x = x * self.blockSize[0]
        y = y * self.blockSize[1] + self.ui_width
        pygame.draw.rect(self.gameDisplay, value, [x, y, self.blockSize[0], self.blockSize[1]])

    def draw_rect_min_max(self, min_corner, max_corner, color=[255] * 3):
        left = min_corner[0]
        top = min_corner[1]
        width = max_corner[0] - min_corner[0]
        height = max_corner[1] - min_corner[1]
        pygame.draw.rect(self.gameDisplay, color, pygame.Rect(left, top, width, height))


class UI:
    class Button:
        def __init__(self, text, pos, action, max_size=None, square=False, bg_color=[0]*3, text_color=[255]*3):
            self.text = text
            self.pos = pos
            self.square = square
            self.max_size = max_size
            self.action = action
            self.bg_color = bg_color
            self.text_color = text_color

        def set_font(self, font):
            orig_size = font.size(self.text)
            size = orig_size
            if self.max_size != None:
                size = tuple(max(s, m) for s, m in zip(size, self.max_size))
            if self.square:
                max_side = max(size)
                size = [max_side] * len(size)
            
            self.text_corner = tuple(p - s / 2 for p, s in zip(self.pos, orig_size))
            self.min_corner = tuple(p - s / 2 for p, s in zip(self.pos, size))
            self.max_corner = tuple(p + s / 2 for p, s in zip(self.pos, size))

        def is_pressed(self, mouse_pos):
            return mouse_pos[0] > self.min_corner[0] and \
                mouse_pos[0] <= self.max_corner[0] and \
                mouse_pos[1] > self.min_corner[1] and \
                mouse_pos[1] <= self.max_corner[1]

    def __init__(self, screen):
        self.screen = screen
        self.buttons = np.ndarray(shape=(0), dtype=UI.Button)

    def add_button(self, button):
        self.buttons = np.append(self.buttons, button)
        button.set_font(self.screen.font)
        return button

    def on_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            self.on_left_click(mouse_pos)

    def update(self):
        for button in self.buttons:
            self.screen.draw_rect_min_max(button.min_corner, button.max_corner, button.bg_color)
            self.screen.render_text(button.text_corner, button.text, button.text_color)

    def on_left_click(self, mouse_pos):
        for button in self.buttons:
            if button.is_pressed(mouse_pos):
                button.action()
                return


class BlockType(Enum):
    Air = 0
    Snake = 1
    Food = 2
    Wall = 3


DefaultHittable = {
    BlockType.Air : False,
    BlockType.Snake : True,
    BlockType.Food : False,
    BlockType.Wall : True,
}

DefaultColors = {
    BlockType.Air : [50] * 3,
    BlockType.Snake : [240] * 3,
    BlockType.Food : (200, 0, 0),
    BlockType.Wall : [20] * 3,
}


class Block:
    def __init__(self, type, food=None, color=None):
        self.set_type(type, color)

        if type == BlockType.Food:
            self.food = food

    def set_type(self, type, color=None):
        self.type = type
        self.color = color if color != None else DefaultColors[type]


class Food:
    def __init__(self, world):
        self.pos = (randrange(0, world.width), randrange(0, world.height))


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
        
    def set_block(self, pos, block):
        if(isinstance(block, BlockType)):
            self.set_block(pos, Block(block))
        elif(isinstance(block, Block)):
            pos = (pos[0] % self.width, pos[1] % self.height)
            self.blocks[int(pos[0]), int(pos[1])] = block

    def set_blocks(self, blocks):
        for x in range(self.width):
            for y in range(self.height):
                self.set_block((x, y), blocks[x, y])

    def get_block(self, pos):
        pos = (pos[0] % self.width, pos[1] % self.height)
        return self.blocks[int(pos[0]), int(pos[1])]

    def clear_snake(self, color):
        for x in range(self.width):
            for y in range(self.height):
                if self.blocks[x, y].type == BlockType.Snake and self.blocks[x, y].color == color:
                    self.blocks[x, y].set_type(BlockType.Air)


class Cardinal(Enum):
    Up    = 0
    Right = 1
    Down  = 2
    Left  = 3

Directions = {
    Cardinal.Up    : (0, -1),
    Cardinal.Right : (1, 0),
    Cardinal.Down  : (0, 1),
    Cardinal.Left  : (-1, 0),
}

class Game:
    def __init__(self, level):
        self.level = level

    def start(self, manager):
        self.manager = manager
        self.inputs = manager.inputs

        self.reset()

    def increase_difficulty(self):
        global curDifficulty
        curDifficulty = curDifficulty + 1
        curDifficulty = min(curDifficulty, 20)
        self.snake.set_speed(curDifficulty)

    def decrease_difficulty(self):
        global curDifficulty
        curDifficulty = curDifficulty - 1
        curDifficulty = max(curDifficulty, 0)
        self.snake.set_speed(curDifficulty)

    def reset(self):
        global curDifficulty

        self.world = World(resolution=level.shape)
        self.screen = Screen(self.world, resolution=tuple(i*30 for i in level.shape))
        self.ui = self.screen.ui
        self.ui.add_button(UI.Button("-", (100, 25), self.decrease_difficulty, square=True, bg_color=[10]*3, text_color=[120]*3))
        self.ui.add_button(UI.Button("+", (150, 25), self.increase_difficulty, square=True, bg_color=[10]*3, text_color=[120]*3))
        self.snake = Snake(self.screen, self.world, self.inputs, speed=curDifficulty, max_stored_inputs=2, color=[255]*3,
            controls=Snake.Controls(
                ['w', pygame.K_UP], ['d', pygame.K_RIGHT], 
                ['s', pygame.K_DOWN], ['a', pygame.K_LEFT]))

        #self.snake2 = Snake(self.screen, self.world, self.inputs, start_pos=(0, 0), speed=15, max_stored_inputs=2, color=(0, 255, 0),
        #    controls=Snake.Controls(
        #        [pygame.K_UP], [pygame.K_RIGHT], 
        #        [pygame.K_DOWN], [pygame.K_LEFT]))

        self.world.set_blocks(level)
        self.world.create_food()

    def launch(self):
        pygame.init()

        running = True
        while(running):
            self.world.update()
            gameOver = not self.snake.update()
            #gameOver = gameOver or not self.snake2.update()
            if gameOver:
                self.reset()

            self.inputs.update()
            self.screen.display()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.inputs.on_event(event)
                    self.screen.on_event(event)


class SceneManager:
    def __init__(self, start_scene):
        self.difficulty = 7

        self.inputs = Inputs()
        pygame.font.init()

        self.go_to_scene(start_scene)

    def go_to_scene(self, scene):
        self.cur_scene = scene
        scene.start(self)
        scene.launch()

    def load_scene(self, file):
        pass
    
curDifficulty = 7

class Snake:
    class RecordedInput:
        def __init__(self, key):
            self.key = key
            self.time = time()

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

    def __init__(self, screen, world, inputs, speed = 5, color=None,
                 controls = Controls('w', 'd', 's', 'a'), start_pos=None, ui_pos = (10, 10), 
                 max_stored_inputs=3, input_decay=0.4):
        self.screen = screen
        self.world = world
        self.inputs = inputs
        self.controls = controls
        self.controls.inputs = self.inputs
        self.color = color

        self.set_speed(speed)
        self.curTime = time()

        self.segments = np.ndarray(shape=(1, 2), dtype=np.int8)
        self.segments[0] = start_pos if start_pos else [world.width / 2, world.height / 2]

        self.input_decay = input_decay
        self.stored_inputs = deque(maxlen=max_stored_inputs)
        self.stored_inputs.append(Snake.RecordedInput(Cardinal.Right))
        self.last_direction = self.stored_inputs[0].key
        self.last_tail_pos = self.segments[0]

        self.score = 0
        self.ui_pos = ui_pos
        
    def set_speed(self, speed):
        self.moveMS = 1 / speed

    def update(self):
        if self.controls.is_pressed(self.controls.up): self.stored_inputs.appendleft(Snake.RecordedInput(Cardinal.Up))
        if self.controls.is_pressed(self.controls.right): self.stored_inputs.appendleft(Snake.RecordedInput(Cardinal.Right))
        if self.controls.is_pressed(self.controls.down): self.stored_inputs.appendleft(Snake.RecordedInput(Cardinal.Down))
        if self.controls.is_pressed(self.controls.left): self.stored_inputs.appendleft(Snake.RecordedInput(Cardinal.Left))

        snakeLives = True
        time_now = time()
        if(time_now - self.curTime > self.moveMS):
            self.curTime = time_now

            direction = self.get_next_input()

            snakeLives = self.check_events(direction)
            self.move(direction)

        self.world.clear_snake(self.color)
        self.update_in_world()

        self.display_score()

        return snakeLives

    def check_events(self, direction):
        nextPos = tuple(s + d for s, d in zip(self.segments[0], Directions[direction]))
        next_block = self.world.get_block(nextPos) 
        self.check_for_food(next_block)
        return not self.check_for_death(nextPos, next_block)

    def check_for_food(self, nextBlock):
        if(nextBlock.type == BlockType.Food):
            self.eat()

    def check_for_death(self, nextPos, next_block):
        if nextPos[0] == self.segments[-1][0] and nextPos[1] == self.segments[-1][1]:
            return False
        return DefaultHittable[next_block.type]

    def move(self, direction):
        self.last_tail_pos = np.array(self.segments[-1])

        for s in range(len(self.segments) - 1, 0, -1):
            self.segments[s] = self.segments[s - 1]

        self.segments[0] = self.segments[0] + Directions[direction]
        self.last_direction = direction

    def get_next_input(self):
        while(len(self.stored_inputs) > 0):
            next_input = self.stored_inputs.pop()
            time_now = time()
            if next_input.time < time_now - self.input_decay:
                continue

            if (next_input.key == Cardinal.Up and self.last_direction != Cardinal.Down) or \
               (next_input.key == Cardinal.Right and self.last_direction != Cardinal.Left) or \
               (next_input.key == Cardinal.Down and self.last_direction != Cardinal.Up) or \
               (next_input.key == Cardinal.Left and self.last_direction != Cardinal.Right):
                return next_input.key

        return self.last_direction

        
    def reset(self):
        main()

    def update_in_world(self):
        for segment in self.segments:
            self.world.set_block(segment, Block(BlockType.Snake, color=self.color))

    def eat(self):
        self.world.set_block(self.segments[0], BlockType.Air)
        self.add_segment()
        self.world.create_food()

        self.score = self.score + 1

    def add_segment(self):
        self.segments = np.append(self.segments, [self.last_tail_pos], 0)

    def display_score(self):
        self.screen.render_text(self.ui_pos, str(self.score))


if __name__ == "__main__":
    level = np.array(
        [[BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air],
         [BlockType.Air, BlockType.Wall, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air],
         [BlockType.Air, BlockType.Wall, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air],
         [BlockType.Air, BlockType.Wall, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air],
         [BlockType.Air, BlockType.Wall, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air],
         [BlockType.Air, BlockType.Wall, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air],
         [BlockType.Air, BlockType.Wall, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air],
         [BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air],
         [BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Wall, BlockType.Air, BlockType.Air, BlockType.Air],
         [BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Wall, BlockType.Air, BlockType.Air, BlockType.Air],
         [BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Wall, BlockType.Air, BlockType.Air, BlockType.Air],
         [BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Wall, BlockType.Air, BlockType.Air, BlockType.Air],
         [BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Wall, BlockType.Air, BlockType.Air, BlockType.Air],
         [BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Wall, BlockType.Air, BlockType.Air, BlockType.Air],
         [BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Wall, BlockType.Air, BlockType.Air, BlockType.Air],
         [BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air, BlockType.Air],]
    )

    SceneManager(Game(level))