class BlockType(Enum):
    Air = 0
    Snake = 1
    Food = 2
    Wall = 3

globals().update(BlockType.__members__)

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