class Scene:
    def start(self, manager):
        pass

    def create_ui(self):
        pass

    def stop(self):
        pass

class Game(Scene):
    def __init__(self, level):
        self.level = level

    def start(self, manager):
        self.manager = manager
        self.inputs = manager.inputs
        self.screen = manager.screen

        self.reset()
        self.ui = screen.ui
        self.ui.add_button(UI.Button("-", (100, 25), self.decrease_difficulty, square=True, bg_color=[10]*3, text_color=[120]*3))
        self.ui.add_button(UI.Button("+", (150, 25), self.increase_difficulty, square=True, bg_color=[10]*3, text_color=[120]*3))

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

    def start(self):
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


class Difficulty(Enum):
    Easy = 0
    Middle = 1
    Hard = 2


class SceneManager:
    def __init__(self, start_scene):
        self.difficulty = 7

        self.inputs = Inputs()
        pygame.font.init()


        self.go_to_scene(start_scene)

    def go_to_scene(self, scene):
        self.cur_scene = scene
        scene.start(self)

    def load_scene(self, file):
        pass
    
curDifficulty = 7