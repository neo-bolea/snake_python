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