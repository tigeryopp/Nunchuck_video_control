import time
import board
import digitalio
import usb_hid
import adafruit_nunchuk

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

"""while True:
    if btn_record.value:
        keyboard.press(Keycode.R)
        time.sleep(0.1)
        keyboard.release(Keycode.R)
    time.sleep(0.1)"""

nc = adafruit_nunchuk.Nunchuk(board.I2C())

while True:
    x, y = nc.joystick
    ax, ay, az = nc.acceleration
    print("joystick = {},{}".format(x, y))
    print("accceleration ax={}, ay={}, az={}".format(ax, ay, az))

    if nc.buttons.C:
        led.value = True
    if nc.buttons.Z:
        led.value = True
    else:
        led.value = False
    time.sleep(0.5)