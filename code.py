import time
import board
import busio
import adafruit_nunchuk
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse

zButton = 0
cButton = 0
SpacebarState = 0
EscState = 0

joyX = 0
joyY = 0
joyXPrevState = 0
joyYPrevState = 0


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

i2c = busio.I2C(board.GP21, board.GP20)
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

while True:
    # print("1")
    # check_disconnect() d
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
    #     print("2")
    # print("3")
    nc.i2c.unlock()
    # print("4")
    try:
        # Z button -> spacebar (start/pause)
        zButton = nc.buttons.Z
        if zButton != SpacebarState:
            if zButton == False:
                kbd.send(Keycode.SPACEBAR)
                print("spacebar")
            SpacebarState = zButton
        
        # C button -> esc (get out of screen, in the future something else?)
        cButton = nc.buttons.C
        if cButton != EscState:
            # # Escape key
            # if cButton == False:
            #     kbd.send(Keycode.ESCAPE)
            #     print("escape")

            # # Macro to move mouse left and click (so that mouse on left screen window)
            if cButton == False:
                ms.move(x = -1200)
                ms.click(Mouse.LEFT_BUTTON)
                print("mouse to left macro")
            EscState = cButton
            EscState = cButton

        # Joystick: right (fast-forward, x), left (rewind, z), up (speed up, d), down (slow down, a)
        x, y = nc.joystick
        if x == 255 or y == 255:
            # print("Invalid joystick values detected, skipping input processing.")
            time.sleep(1)  # Small delay to avoid busy-waiting and prevent unwanted behavior
            continue
        # ax, ay, az = nc.acceleration
        # print("joystick = {},{}".format(x, y))
        # print("accceleration ax={}, ay={}, az={}".format(ax, ay, az))
        
        # fastfwd/rewind
        if x < 50:
            joyX = -1
        elif x > 205:
            joyX = 1
        else:
            joyX = 0

        # speed up/slow down
        if y < 50:
            joyY = -1
        elif y > 205:
            joyY = 1
        else:
            joyY = 0

        # fastfwd/rewind send key
        if (joyX != joyXPrevState) & (joyY == joyYPrevState):
            if joyX == -1:
                kbd.send(Keycode.Z)
                print("backward")
            elif joyX == 1:
                kbd.send(Keycode.X)
                print("forward")    
        joyXPrevState = joyX

        # speed up/slow down send key
        if joyY != joyYPrevState:
            if joyY == -1:
                kbd.send(Keycode.S)
                print("slow down")
            elif joyY == 1:
                kbd.send(Keycode.D)
                print("speed up")
                print(x,y)    
        joyYPrevState = joyY
        
        time.sleep(0.01)
    
    except Exception as e:
        print(e)
