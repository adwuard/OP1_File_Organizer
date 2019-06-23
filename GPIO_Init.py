import os
import time
import RPi.GPIO as GPIO
import SSD1306
from PIL import ImageFont, Image

# import Adafruit_GPIO.SPI as SPI

__author__ = "Hsuan Han Lai (Edward Lai)"
__date__ = "2019-04-02"

workDir = os.path.dirname(os.path.realpath(__file__))

# Input pins:
L_pin, R_pin, C_pin, U_pin, D_pin = 27, 23, 4, 17, 22
A_pin, B_pin = 5, 6

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(L_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(R_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(U_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(D_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(C_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
RST = 24  # Raspberry Pi pin configuration:
disp = SSD1306.SSD1306_128_64(rst=RST)  # 128x64 display with hardware I2C

# SPI Protocol Config
# Note you can change the I2C address by passing an i2c_address parameter like:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)
# Alternatively you can specify an explicit I2C bus number, for example
# with the 128x32 display you would use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=2)


# Initialize library and clear image from last session.
disp.begin()


# disp.clear()
# disp.display()


def getLargeFont():
    return ImageFont.truetype(workDir + "/Fonts/Georgia Bold.ttf", 12)


def getFont():
    return ImageFont.truetype(workDir + "/Fonts/Georgia Bold.ttf", 10)


def getSmallFont():
    return ImageFont.truetype(workDir + "/Fonts/Georgia Bold.ttf", 9)


def clearDisplay():
    disp.clear()


def displayImage(img):
    disp.clear()
    disp.image(img)
    disp.display()


def displayPng(pathToImage):
    image = Image.new('1', (128, 64))
    image.paste(Image.open(pathToImage).convert("1"))
    displayImage(image)


def getKeyStroke():
    time.sleep(0.05)
    try:
        while 1:
            if not GPIO.input(U_pin):
                return "UP"
            if not GPIO.input(L_pin):
                return "LEFT"
            if not GPIO.input(R_pin):
                return "RIGHT"
            if not GPIO.input(D_pin):
                return "DOWN"
            if not GPIO.input(C_pin):
                time.sleep(0.2)
                return "CENTER"
            if not GPIO.input(A_pin):
                time.sleep(0.2)
                return "A"
            if not GPIO.input(B_pin):
                time.sleep(0.2)
                return "B"
    except KeyboardInterrupt:
        GPIO.cleanup()


def checkKeyInterrupt():
    time.sleep(0.05)
    if not GPIO.input(U_pin):
        return "UP"
    if not GPIO.input(L_pin):
        time.sleep(0.1)
        return "LEFT"
    if not GPIO.input(R_pin):
        time.sleep(0.1)
        return "RIGHT"
    if not GPIO.input(D_pin):
        return "DOWN"
    if not GPIO.input(C_pin):
        time.sleep(0.2)
        return "CENTER"
    if not GPIO.input(A_pin):
        return "A"
    if not GPIO.input(B_pin):
        return "B"
    else:
        return ""


def getAnyKeyEvent():
    if getKeyStroke() != "":
        return True
