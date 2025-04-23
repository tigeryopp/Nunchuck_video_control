import time
import board
import busio
import adafruit_nunchuk

zButton = 0
cButton = 0
SpacebarState = 0
EscState = 0

joyX = 0
joyY = 0
joyXPrevState = 0
joyYPrevState = 0

nc = adafruit_nunchuk.Nunchuk(busio.I2C(board.GP21, board.GP20))

# while True:

#     with nc.i2c_device as device:
#         device._I2CDevice__probe_for_device()
#     #     while not busio.I2C(board.GP21, board.GP20).try_lock():
#     #         time.sleep(0)
#     #     try:
#     #         device.i2c
#     #         # ]
#     #         # .i2c.writeto(nc.address, b"")
#     #     except OSError:
#     #         print("device disconnected.")
#     #     finally:    
#     #         time.sleep(1)


while True:
    success = True # nchuk.update();  // Get new data from the controller
    
    while (success == False):
        print("Controller disconnected!")
        time.sleep(1)

    # Z button -> spacebar (start/pause)
    zButton = nc.buttons.Z
    if zButton != SpacebarState:
        if zButton == False:
            """
            output spacebar
            """
            print("spacebar")
        SpacebarState = zButton
    
    # C button -> esc (get out of screen, in the future something else?)
    cButton = nc.buttons.C
    if cButton != EscState:
        if cButton == False:
            """
            output esc key
            """
            print("escape")
        EscState = cButton

    # Joystick: right (fast-forward, x), left (rewind, z), up (speed up, d), down (slow down, a)
    x, y = nc.joystick
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

    # fastfwd/rewind
    if (joyX != joyXPrevState) & (joyY == joyYPrevState):
        if joyX == -1:
            """
            'x' key
            """
            print("backward")
        elif joyX == 1:
            """
            'z' key
            """
            print("forward")    
    joyXPrevState = joyX

    # speed up/slow down
    if joyY != joyYPrevState:
        if joyY == -1:
            """
            'a' key
            """
            print("slow down")
        elif joyY == 1:
            """
            'd' key
            """
            print("speed up")    
    joyYPrevState = joyY
    
    time.sleep(0.01)

