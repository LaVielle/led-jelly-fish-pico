from math import floor
from random import randint
import time
from gammaCorrection import gammaCorrectRgb, gammaCorrectSingleValue
from neopixel import Neopixel

from machine import Pin
led = Pin(25, Pin.OUT)

class Strip:
    def __init__(self, numPixels: int, pin: int, stateMachine: int):
        self.neopixel = Neopixel(numPixels, stateMachine, pin, "GRB")
        self.numPixels = numPixels
        self.pixelOnIndex = 0
        self.randomPixelBlinkCount = 0
        self.isAnimationEnabled = False
        self.isFadingIn = True

        self.hue = 0
        self.sat = 255
        self.brightness = 0

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # We should only use these methods to update the neopixels.
    # They have built in gamma correction.
    def udpateBrightness(self, brightness: int):
        self.neopixel.brightness(gammaCorrectSingleValue(brightness))
    
    def updatePixel(self, index, color):
        self.neopixel.set_pixel(index, gammaCorrectRgb(color))

    def updateFill(self, color):
        self.neopixel.fill(gammaCorrectRgb(color))

    def show(self):
        self.neopixel.show()

    def colorHSV(self, h, s, v):
        return self.neopixel.colorHSV(h, s, v)

    def updateFillHSV(self, h, s, v):
        self.hue = h
        self.sat = s
        self.brightness = v

        self.updateFill(
            self.colorHSV(h,s,v)
            )

    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    def setIsAnimationEnabled(self, enabled: bool):
        self.isAnimationEnabled = enabled

    def setIsFadingIn(self, isFadingIn: bool):
        self.isFadingIn = isFadingIn

    def calculateAnimationCycleEnd(self):
        if (self.isAnimationEnabled):
            if (self.isFadingIn == False and self.brightness == 0):
                return True
        
        return False

    def calcRandomePixelBlinkCycleEnd(self):
        if (self.randomPixelBlinkCount == 50):
            return True
        return False

    def setPixelOnIndex(self, newPixelOnIndex: int):
        self.pixelOnIndex = newPixelOnIndex
    
    def setHue(self, h: int):
        self.hue = h

    def setRandomPixelBlinkCount(self, c: int):
        self.randomPixelBlinkCount = c

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 





bodyStrip = Strip(10, 0, 0)
armStrip = Strip(5, 1, 1)

# Set initial brightness to max
bodyStrip.udpateBrightness(255)
armStrip.udpateBrightness(255)

bodyStrip.setIsAnimationEnabled(True)


MIN_BRIGHTNESS = 0
MAX_BRIGHTNESS = 255

MIN_HUE = 0
MAX_HUE = 65535

def iterateFullStripFade(isFadingIn: bool, brightness: int):
    newBrightness = brightness
    newIsFadingIn = isFadingIn

    if (isFadingIn):
        if (brightness == MAX_BRIGHTNESS):
            newIsFadingIn = False
        else:
            newBrightness = brightness + 1
    else:
        if (brightness == MIN_BRIGHTNESS):
            newIsFadingIn = True
        else:
            newBrightness = brightness - 1
    
    return newBrightness, newIsFadingIn

def iterateHue(h):
    return h + 50

def iterateRandomPixelBlink(pixelOnIndex: int, numPixels: int, hue: int):
    newPixel = pixelOnIndex
    
    while(newPixel == pixelOnIndex):
        newPixel = randint(0, numPixels - 1)

    newHue = hue + randint(0, floor(MAX_HUE / 10))

    print('newPixel', newPixel)
    print('newHue', newHue)

    return newPixel, newHue

while(True):

    if (bodyStrip.isAnimationEnabled):
        newHue = iterateHue(bodyStrip.hue)
        animationResult = iterateFullStripFade(bodyStrip.isFadingIn, bodyStrip.brightness)
        newBrightness = animationResult[0]
        newIsFadingIn = animationResult[1]

        bodyStrip.setIsFadingIn(newIsFadingIn)
        bodyStrip.updateFillHSV(newHue, 255, newBrightness)
        bodyStrip.show()

        isAnimationCycleEnded = bodyStrip.calculateAnimationCycleEnd()

        if (isAnimationCycleEnded):
            bodyStrip.setIsAnimationEnabled(False)
            armStrip.setIsAnimationEnabled(True)

        time.sleep_ms(5)

    # if (bodyStrip.isAnimationEnabled):
    #     animationResult = iterateRandomPixelBlink(bodyStrip.pixelOnIndex, bodyStrip.numPixels, bodyStrip.hue)
    #     newPixelOn = animationResult[0]
    #     newHue = animationResult[1]

    #     # Turn off prev pixel
    #     bodyStrip.updatePixel(bodyStrip.pixelOnIndex, (0,0,0))

    #     # Turn on next pixel
    #     bodyStrip.updatePixel(newPixelOn, bodyStrip.colorHSV(newHue, 255, 255))
    #     bodyStrip.setPixelOnIndex(newPixelOn)
    #     bodyStrip.setHue(newHue)
    #     bodyStrip.setRandomPixelBlinkCount(bodyStrip.randomPixelBlinkCount + 1)

    #     isAnimationCycleEnded = bodyStrip.calcRandomePixelBlinkCycleEnd()

    #     print('isAnimationCycleEnded', isAnimationCycleEnded)
    #     print('armStrip.randomPixelBlinkCount', bodyStrip.randomPixelBlinkCount)
        
    #     if (isAnimationCycleEnded):
    #         bodyStrip.setIsAnimationEnabled(False)
    #         bodyStrip.setRandomPixelBlinkCount(0)
    #         bodyStrip.updateFillHSV(0, 255, 0)
    #         armStrip.setIsAnimationEnabled(True)

    #     bodyStrip.show()

    # Arm Strip Random Pixel Animation
    if (armStrip.isAnimationEnabled):
        animationResult = iterateRandomPixelBlink(armStrip.pixelOnIndex, armStrip.numPixels, armStrip.hue)
        newPixelOn = animationResult[0]
        newHue = animationResult[1]

        # Turn off prev pixel
        armStrip.updatePixel(armStrip.pixelOnIndex, (0,0,0))

        # Turn on next pixel
        armStrip.updatePixel(newPixelOn, armStrip.colorHSV(newHue, 255, 255))
        armStrip.setPixelOnIndex(newPixelOn)
        armStrip.setHue(newHue)
        armStrip.setRandomPixelBlinkCount(armStrip.randomPixelBlinkCount + 1)

        isAnimationCycleEnded = armStrip.calcRandomePixelBlinkCycleEnd()

        print('isAnimationCycleEnded', isAnimationCycleEnded)
        print('armStrip.randomPixelBlinkCount', armStrip.randomPixelBlinkCount)
        
        if (isAnimationCycleEnded):
            armStrip.setIsAnimationEnabled(False)
            armStrip.setRandomPixelBlinkCount(0)
            armStrip.updateFillHSV(0, 255, 0)
            bodyStrip.setIsAnimationEnabled(True)

        armStrip.show()

        time.sleep_ms(50)


# while(True):
    
#     if (bodyStrip.isAnimationEnabled):
#         newHue = iterateHue(bodyStrip.hue)
#         animationResult = iterateFullStripFade(bodyStrip.isFadingIn, bodyStrip.brightness)
#         newBrightness = animationResult[0]
#         newIsFadingIn = animationResult[1]

#         bodyStrip.setIsFadingIn(newIsFadingIn)
#         bodyStrip.updateFillHSV(newHue, 255, newBrightness)
#         bodyStrip.show()

#         isAnimationCycleEnded = bodyStrip.calculateAnimationCycleEnd()

#         if (isAnimationCycleEnded):
#             bodyStrip.setIsAnimationEnabled(False)
#             armStrip.setIsAnimationEnabled(True)


#     if (armStrip.isAnimationEnabled):
#         newHue = iterateHue(armStrip.hue)
#         animationResult = iterateFullStripFade(armStrip.isFadingIn, armStrip.brightness)
#         newBrightness = animationResult[0]
#         newIsFadingIn = animationResult[1]

#         armStrip.setIsFadingIn(newIsFadingIn)
#         armStrip.updateFillHSV(newHue, 255, newBrightness)
#         armStrip.show()

#     isAnimationCycleEnded = armStrip.calculateAnimationCycleEnd()

#     if (isAnimationCycleEnded):
#         armStrip.setIsAnimationEnabled(False)
#         bodyStrip.setIsAnimationEnabled(True)
        

#     time.sleep_ms(5)

#     led.toggle()