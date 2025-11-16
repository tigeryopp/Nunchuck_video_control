### Macropad based on fighting game motion inputs
### Adapted from https://critpoints.net/2025/02/05/how-to-code-fighting-game-motion-inputs/

import time
import board
import busio
import adafruit_nunchuk
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse

### Controller Handling
class MyChuck(adafruit_nunchuk.Nunchuk):
    
    def __init__(self, i2c, address: int = 0x52, **kwargs):
        # while not i2c.try_lock():
        #     pass
        # print("I2C bus locked from subclass!")
        # i2c.unlock()
        
        self.i2c = i2c
        self.address = address

        print("Waiting for Nunchuk at address 0x%x..." % address)
        while True:
            while not i2c.try_lock():
                pass
            print("reinit 1")
            try:
                if address in i2c.scan():
                    print("Nunchuk found!")
                    break
            except Exception as e:
                print("Scan failed:", e)
            finally:
                i2c.unlock()
            time.sleep(0.5)

        print("reinit 4")

        # Now call the original Nunchuk constructor
        super().__init__(i2c, **kwargs)
        print("reinit 5")

i2c = busio.I2C(board.D5, board.D4)
nc = MyChuck(i2c)
kbd = Keyboard(usb_hid.devices)
ms = Mouse(usb_hid.devices)

def check_disconnect():
    """
    Checks if controller is disconnected.
    """
    disconnected = False

    while not nc.i2c.try_lock():
        pass
    if nc.address not in nc.i2c.scan():
        disconnected = True
        while nc.address not in nc.i2c.scan():
            print("Controller disconnected...")
            time.sleep(1)
    if disconnected:
        print("Controller reconnected! recovering...")
        time.sleep(0.5)
    nc.i2c.unlock()

### Motion input class
class Direction:
    """
    Direction object stores the properties of each input of a command
    
    direction: D-Pad direction

    window: number of frames allowed for input

    strict: whether it needs to strictly be that direction, e.g. whether ↘ still counts as a down/crouch input
    """
    __slots__ = ("direction", "window", "strict") # with slots on, dictionary of attributes is fixed to those three, thereby saving memory
    
    def __init__(self, direction: int, window: int, strict: bool):
        self.direction = direction
        self.window = window
        self.strict = strict

class Command:
    """
    Class where inputs are stored as a list of Direction objects
    Used to compare with buffer, to check if command inputted properly
    """
    def __init__(self, name: str, new_inputs: list[Direction] | None = None, initiator: tuple | None = None, effect = None):
        """
        new_inputs (optional): can define a command as a list of Direction objects in chronological order of input
        
        initiator (optional): buttons to press so that the command is executed, e.g. C + Z
        equivalent to pressing the attack inputs in fighting games.
        datatype is tuple for now as only 2 buttons
        (STILL UNDER DEVELOPMENT, DATATYPE OF LIST MIGHT CHANGE)

        effect (optional): effect of executing command. probably another class instance
        (STILL UNDER DEVELOPMENT)

        Note: the list of Direction objects need to be stored in reverse as when comparing with buffer, last input is compared first
        Hence when calling the instance, the Direction objects are chronological, but they are stored in the reverse order
        """
        self.name = name
        self.initiator = initiator
        self.effect = effect
        if new_inputs == None:
            self.input_list = []
        else:
            self.input_list = list(reversed(new_inputs))

    def add(self, direction, window, strict):
        """
        Adds inputs to command. reverse() is such that in the list of Direction instances, 
        the order is reversed so the first term is the last-most input, second is second last, and so on
        """
        self.input_list.reverse()
        self.input_list.append(Direction(direction, window, strict))
        self.input_list.reverse()
        return self # Returns instance after executing method. Hence allows methods to be chained
    
    def check_direction(input_direction: int, command_direction: int, strict: bool):
        """
        Checks if direction input in question matches the command input

        takes in D-pad values of the actual input and the command (specified in Direction object), as well as boolean strict (specified in Direction object)

        If strict = True, then only inputs that exactly matches the command are valid.
        Otherwise, the adjacent diagonal directions are also valid

        In actual fighting games the direction the character is facing changes the command that needs to be inputted
        """
        if strict:
            return input_direction == command_direction
        else: # Note: no comparison for 5
            if command_direction == (2 or 8):
                return input_direction in [command_direction - 1, command_direction, command_direction + 1]
            elif command_direction == (4 or 6):
                return input_direction in [command_direction - 3, command_direction, command_direction + 3]
            elif command_direction == (1 or 3):
                return input_direction in [2, command_direction, command_direction + 3]
            elif command_direction == (7 or 9):
                return input_direction in [command_direction - 3, command_direction, 8]

    def check_command(self, buffer_pos: int, command_pos: int) -> bool:
        """
        Checks if recent inputs in buffer matches command. Returns true if it did, False if didn't
        Should account for consecutive duplicate directions (hold), and ignore them (until it reaches the window number of frames, at which you've held too long)

        buffer_pos: index of buffer in which should to perform the check. When starting the command check should start with = 0
        and the recursive nature of this function should take care of the indices for the other command inputs

        command_pos: index of the Directions that need to be inputted for the command (most recent first)
        """
        window_ = self.input_list[command_pos].window
        for i in range(buffer_pos, buffer_pos + window_):
            # if buffer[i] == 5: #skip to next buffer frame if neutral input. I guess this means that you can neutral input during a command and it won't affect
            #     # honestly can think of ways this could be problematic, e.g. just directions or commands that require inputting the same direction twice (backdashing etc.)
            #     continue
            if self.check_direction(buffer[i], self.input_list[command_pos].direction, self.input_list[command_pos].strict):
                if command_pos + 1 > len(self.input_list): # When full command matches
                    print(self.name)
                    return True
                else:
                    duplication = 0
                    while (buffer[buffer_pos] == buffer_pos[buffer_pos + 1]) and (duplication < window_): # Dont count consecutive duplicate (hold) directions, for at max. the window for command input
                        buffer_pos += 1
                        duplication += 1
                    self.check_command(self, buffer_pos+1, command_pos + 1) # Go to check next command
            else:
                return False # return breaks loop and exits function

class Effect():
    """
    Stores effects of successfully executing command as methods
    """
    def __init__(self):
        pass

    def empty(self):
        pass
    
    def press_a(self):
        kbd.send(Keycode.A)
        print("slow down")

    def press_d(self):
        kbd.send(Keycode.D)
        print("speed up")

    def press_z(self):
        kbd.send(Keycode.Z)
        print("backward")
    
    def press_x(self):
        kbd.send(Keycode.X)
        print("forward")  

    def press_space(self):
        kbd.send(Keycode.SPACEBAR)
        print("spacebar")

    def move_mouse(self):
        ms.move(x = -1200)
        ms.click(Mouse.LEFT_BUTTON)
        print("mouse to left macro")

    def led_rainbow(self):
        







### Global Variables
zButton = False
cButton = False
SpacebarState = False
EscState = False

joyXPrevState = False
joyYPrevState = False

# Fighting game variables
"""
D-Pad Values:
↖: 7    ↑: 8    ↗: 9
←: 4    •: 5    →: 6
↙: 1    ↓: 2    ↘: 3

Mapping:
    joyX and joyY both in range [-1, 1]
    encode horizontal inputs in 1~3 by adding 2
    encode vertical inputs in 0, 3, 6 by adding 0, 3, 6
        ↳ dpad = joyX + 2 + (joyY + 1) * 3
    sanity check:   joyX, joyY = 0, 0 -> dpad = 0 + 2 + (0 + 1) * 3 = 5 (neutral)
    sanity check 2: joyX, joyY = -1, -1 -> dpad = -1 + 2 + (-1 + 1) * 3 = 1 (neutral)
"""
frame = 1. / 60

buffer = [] #records recent directional inputs
buffer_length = 20


thresh_positive = 180 # Threshold for joystick to detect positive direction input (up, right)
thresh_negative = 70  #                "                 negative direction input (down, left)
joyX = 0 # Range -1 (left) to 1 (right)
joyY = 0 # Range -1 (down) to 1 (up)
dpad = 5

### Main Loop
while True:
    # Checking for disconnect
    disconnected = False
    while not nc.i2c.try_lock():
        pass
    if nc.address not in nc.i2c.scan():
        disconnected = True
        while nc.address not in nc.i2c.scan():
            print("Controller disconnected...")
            time.sleep(1)
    if disconnected:
        i2c.unlock()
        try:
            print("reinitializing")
            nc = MyChuck(i2c)
            print("Controller reinitialized.")
        except Exception as e:
            print("Reinitialization failed:", e)
            continue  # Retry in next loop
        print(nc)
        # print(nc.buttons.Z)
        time.sleep(0.5)
    nc.i2c.unlock()

    try:
        time_now = time.monotonic()

        # Obtain input, map to D-Pad
        zButton = nc.buttons.Z
        cButton = nc.buttons.C
        x, y = nc.joystick
        if x < thresh_negative:
            joyX = -1
        elif x > thresh_positive:
            joyX = 1
        else:
            joyX = 0
        if y < thresh_negative:
            joyY = -1
        elif y > thresh_positive:
            joyY = 1
        else:
            joyY = 0
        dpad = joyX + 2 + ((joyY + 1) * 3)

        # Update buffer
        if len(buffer) > buffer_length:
            buffer.pop(-1) # Oldest input in buffer erased
        buffer.insert(0, dpad) # This way, most recent input put at beginnng of buffer


        # buffer.append([dpad, zButton, cButton])
        
        print(buffer)
        



        # print(time_now)





        








        # if zButton != SpacebarState:
        #     if zButton == False:
        #         kbd.send(Keycode.SPACEBAR)
        #         print("spacebar")
        #     SpacebarState = zButton
        
        # # C button -> esc (get out of screen, in the future something else?)
        
        # if cButton != EscState:
        #     # # Escape key
        #     # if cButton == False:
        #     #     kbd.send(Keycode.ESCAPE)
        #     #     print("escape")

        #     # # Macro to move mouse left and click (so that mouse on left screen window)
        #     if cButton == False:
        #         ms.move(x = -1200)
        #         ms.click(Mouse.LEFT_BUTTON)
        #         print("mouse to left macro")
        #     EscState = cButton
        #     EscState = cButton

        # # Joystick: right (fast-forward, x), left (rewind, z), up (speed up, d), down (slow down, a)
        

        # # speed up/slow down
        

        # # fastfwd/rewind send key
        # if (joyX != joyXPrevState) & (joyY == joyYPrevState):
        #     if joyX == -1:
        #         kbd.send(Keycode.Z)
        #         print("backward")
        #     elif joyX == 1:
        #         kbd.send(Keycode.X)
        #         print("forward")    
        # joyXPrevState = joyX

        # # speed up/slow down send key
        # if joyY != joyYPrevState:
        #     if joyY == -1:
        #         kbd.send(Keycode.S)
        #         print("slow down")
        #     elif joyY == 1:
        #         kbd.send(Keycode.D)
        #         print("speed up")
        #         print(x,y)    
        # joyYPrevState = joyY
        
        time.sleep(0.01)
    
    except Exception as e:
        print(e)
