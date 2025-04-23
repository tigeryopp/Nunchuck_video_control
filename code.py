import time
import board
import busio
import adafruit_nunchuk
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

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

        # Now call the original Nunchuk constructor
        super().__init__(i2c, **kwargs)


nc = MyChuck(busio.I2C(board.GP21, board.GP20))

while True:
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
    time.sleep(0.5)




# # while True:
#     try:
#         while not nc.i2c.try_lock():
#             pass
#         print("I2C bus locked from subclass!")
#         nc.i2c.writeto(0x52, b"")
#         print("got data")
#     except OSError:
#         # some OS's dont like writing an empty bytesting...
#         # Retry by reading a byte
#         try:
#             result = bytearray(1)
#             nc.i2c.readfrom_into(nc.address, result)
#             print("got data")
#         except OSError:
#             # pylint: disable=raise-missing-from
#             print("No I2C device at address: 0x%x" % nc.address)
#             # pylint: enable=raise-missing-from
#     finally:
#         if nc.i2c and nc.i2c.try_lock():
#             nc.i2c.unlock()
#     print("loop continuing")

#******


# nc = adafruit_nunchuk.Nunchuk(busio.I2C(board.GP21, board.GP20))
# kbd = Keyboard(usb_hid.devices)

# while True:

#     with nc.i2c_device as device:
#         while not busio.I2C(board.GP21, board.GP20).try_lock():
#             time.sleep(0)
#         try:
#             device.write(b"")
#         except:
#             pass
#     #         # ]
#     #         # .i2c.writeto(nc.address, b"")
#     #     except OSError:
#     #         print("device disconnected.")
#     #     finally:    
#     #         time.sleep(1)


# while True:
#     success = True # nchuk.update();  // Get new data from the controller
    
#     while (success == False):
#         print("Controller disconnected!")
#         time.sleep(1)

#     # Z button -> spacebar (start/pause)
#     zButton = nc.buttons.Z
#     if zButton != SpacebarState:
#         if zButton == False:
#             kbd.send(Keycode.SPACEBAR)
#             print("spacebar")
#         SpacebarState = zButton
    
#     # C button -> esc (get out of screen, in the future something else?)
#     cButton = nc.buttons.C
#     if cButton != EscState:
#         if cButton == False:
#             kbd.send(Keycode.ESCAPE)
#             print("escape")
#         EscState = cButton

#     # Joystick: right (fast-forward, x), left (rewind, z), up (speed up, d), down (slow down, a)
#     x, y = nc.joystick
#     # ax, ay, az = nc.acceleration
#     # print("joystick = {},{}".format(x, y))
#     # print("accceleration ax={}, ay={}, az={}".format(ax, ay, az))
    
#     # fastfwd/rewind
#     if x < 50:
#         joyX = -1
#     elif x > 205:
#         joyX = 1
#     else:
#         joyX = 0

#     # speed up/slow down
#     if y < 50:
#         joyY = -1
#     elif y > 205:
#         joyY = 1
#     else:
#         joyY = 0

#     # fastfwd/rewind send key
#     if (joyX != joyXPrevState) & (joyY == joyYPrevState):
#         if joyX == -1:
#             kbd.send(Keycode.Z)
#             print("backward")
#         elif joyX == 1:
#             kbd.send(Keycode.X)
#             print("forward")    
#     joyXPrevState = joyX

#     # speed up/slow down send key
#     if joyY != joyYPrevState:
#         if joyY == -1:
#             kbd.send(Keycode.S)
#             print("slow down")
#         elif joyY == 1:
#             kbd.send(Keycode.D)
#             print("speed up")    
#     joyYPrevState = joyY
    
#     time.sleep(0.01)

