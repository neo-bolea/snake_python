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