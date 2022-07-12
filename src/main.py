from math import floor
from random import randint
import time
from gammaCorrection import gammaCorrectRgb, gammaCorrectSingleValue
from neopixel import Neopixel

# translate
# Prob equivalent of `map` in p5.js
# taken from https://stackoverflow.com/a/1969274/4876564
def translate(value, inputMin, inputMax, outputMin, outputMax):
    # Figure out how 'wide' each range is
    inputSpan = inputMax - inputMin
    outputSpan = outputMax - outputMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - inputMin) / float(inputSpan)

    # Convert the 0-1 range into a value in the right range.
    return outputMin + (valueScaled * outputSpan)

# Mostly taken from https://stackoverflow.com/a/67170437/4876564
def distanceBetweenFloats(index1: float, index2: float):
    return index2 - index1 if index1 < index2  else index2 - index1

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
        
        self.swooshOffset = 5
        self.adjSwooshIndex = -self.swooshOffset

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

    def calcRandomPixelBlinkCycleEnd(self):
        if (self.randomPixelBlinkCount == 50):
            return True
        return False

    def calculateSwooshAnimationCycleEnd(self):
        if (self.adjSwooshIndex >= self.numPixels + self.swooshOffset):
            return True
        return False

    def setPixelOnIndex(self, newPixelOnIndex: int):
        self.pixelOnIndex = newPixelOnIndex
    
    def setHue(self, h: int):
        self.hue = h

    def setRandomPixelBlinkCount(self, c: int):
        self.randomPixelBlinkCount = c

    def setSwooshIndex(self, i: int):
        self.adjSwooshIndex = i

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

def iterateSwooshIndex(smooshIndex: float):
    newSwooshIndex = smooshIndex + 0.1
    return newSwooshIndex


while(True):

    if (bodyStrip.isAnimationEnabled):


        for ledIndex in range(bodyStrip.numPixels):
            distanceFromSwooshIndex = abs(distanceBetweenFloats(bodyStrip.adjSwooshIndex, ledIndex))
            adjBrightness = max(
                floor(translate(distanceFromSwooshIndex, 0, bodyStrip.swooshOffset, 255, 0)),
                0
            )

            newHue = bodyStrip.hue + 10
            bodyStrip.setHue(newHue)

            adjColor = bodyStrip.colorHSV(newHue, 255, adjBrightness)
            bodyStrip.updatePixel(ledIndex, adjColor)
        bodyStrip.show()

        newSwooshIndex = iterateSwooshIndex(bodyStrip.adjSwooshIndex)
        bodyStrip.setSwooshIndex(newSwooshIndex)

        isAnimationCycleEnded = bodyStrip.calculateSwooshAnimationCycleEnd()

        if (isAnimationCycleEnded):
            bodyStrip.setSwooshIndex(-bodyStrip.swooshOffset)
            bodyStrip.setIsAnimationEnabled(False)
            armStrip.setIsAnimationEnabled(True)

        time.sleep_ms(5)

    # if (bodyStrip.isAnimationEnabled):
    #     newHue = iterateHue(bodyStrip.hue)
    #     animationResult = iterateFullStripFade(bodyStrip.isFadingIn, bodyStrip.brightness)
    #     newBrightness = animationResult[0]
    #     newIsFadingIn = animationResult[1]

    #     bodyStrip.setIsFadingIn(newIsFadingIn)
    #     bodyStrip.updateFillHSV(newHue, 255, newBrightness)
    #     bodyStrip.show()

    #     isAnimationCycleEnded = bodyStrip.calculateAnimationCycleEnd()

    #     if (isAnimationCycleEnded):
    #         bodyStrip.setIsAnimationEnabled(False)
    #         armStrip.setIsAnimationEnabled(True)

    #     time.sleep_ms(5)




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

    #     isAnimationCycleEnded = bodyStrip.calcRandomPixelBlinkCycleEnd()

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

        isAnimationCycleEnded = armStrip.calcRandomPixelBlinkCycleEnd()
        
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