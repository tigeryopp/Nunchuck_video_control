import time
import board
import busio
import adafruit_nunchuk

class MyChuck(adafruit_nunchuk.Nunchuk):
    def __iit__(self, i2c, *args, **kwargs):
        while not i2c.try_lock():
            pass
        print("I2C bus locked from subclass!")
        i2c.unlock()

        # Now call the original Nunchuk constructor
        super().__init__(i2c, *args, **kwargs)


nc = MyChuck(busio.I2C(board.GP21, board.GP20))

while True:
    pass

# while True:
#     x, y = nc.joystick
#     ax, ay, az = nc.acceleration
#     print("joystick = {},{}".format(x, y))
#     print("accceleration ax={}, ay={}, az={}".format(ax, ay, az))

#     if nc.buttons.C:
#         print("button C")
#     if nc.buttons.Z:
#         print("button Z")
#     time.sleep(0.5)