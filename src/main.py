from math import floor
from random import randint, random
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

ANIMATIONS = [
    0, # swoosh
    1, # rbreath
    2 # randomBlink
]
ANIMATION_PROBABILITIES = [
    0.45, # swoosh
    0.45, # rbreath
    0.1 # randomBlink
]
MIN_ANIMATION_ITERATIONS = 2
MAX_ANIMATION_ITERATIONS = 100

class Strip:
    def __init__(self, numPixels: int, pin: int, stateMachine: int):
        self.neopixel = Neopixel(numPixels, stateMachine, pin, "GRB")
        self.numPixels = numPixels
        self.pixelOnIndex = 0
        self.randomPixelBlinkCount = 0
        self.isAnimationEnabled = False
        self.isFadingIn = True
        
        self.swooshOffset = floor(numPixels / 3)
        self.adjSwooshIndex = -self.swooshOffset

        self.hue = 0
        self.sat = 255
        self.brightness = 0

        self.animationType = self.calculateNextAnimationType()
        self.targetAnimationIterations = randint(MIN_ANIMATION_ITERATIONS, MAX_ANIMATION_ITERATIONS)
        self.animationIterations = 0

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

    def calculateNextAnimationType(self):
        seed = random()
        if (seed < 0.45):
            return 0
        if (seed < 0.90):
            return 1
        if (seed < 0.9):
            return 2 

    def calculateResetAnimationIteration(self):
        if (self.animationIterations == self.targetAnimationIterations):
            newAnimationType = self.calculateNextAnimationType()

            # ensure newAnimationType is not same as current animationType
            while (newAnimationType == self.animationType):
                newAnimationType = self.calculateNextAnimationType()
            
            self.animationType = newAnimationType

            self.targetAnimationIterations = randint(MIN_ANIMATION_ITERATIONS, MAX_ANIMATION_ITERATIONS)
            self.animationIterations = 0
        else:
            self.animationIterations += 1

    def calcRandomPixelBlinkCycleEnd(self):
        if (self.randomPixelBlinkCount == 50):
            self.calculateResetAnimationIteration()
            return True
        return False

    def calculateSwooshAnimationCycleEnd(self):
        if (self.adjSwooshIndex >= self.numPixels + self.swooshOffset):
            self.calculateResetAnimationIteration()
            return True
        return False

    def calculateBreathCycleEnd(self):
        if (self.isAnimationEnabled):
            if (self.isFadingIn == False and self.brightness == 0):
                self.calculateResetAnimationIteration()
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

    def animateSwoosh(self, onAnimationEnd):
        for ledIndex in range(self.numPixels):
            distanceFromSwooshIndex = abs(distanceBetweenFloats(self.adjSwooshIndex, ledIndex))
            adjBrightness = max(
                floor(translate(distanceFromSwooshIndex, 0, self.swooshOffset, 255, 0)),
                0
            )

            newHue = self.hue + 10
            self.setHue(newHue)

            adjColor = self.colorHSV(newHue, 255, adjBrightness)
            self.updatePixel(ledIndex, adjColor)
        self.show()

        newSwooshIndex = iterateSwooshIndex(self.adjSwooshIndex)
        self.setSwooshIndex(newSwooshIndex)

        isAnimationCycleEnded = self.calculateSwooshAnimationCycleEnd()

        if (isAnimationCycleEnded):
            self.setSwooshIndex(-self.swooshOffset)
            self.setIsAnimationEnabled(False)
            onAnimationEnd()

        time.sleep_ms(5)
    
    def animateRandomBlink(self, onAnimationEnd):
        animationResult = iterateRandomPixelBlink(self.pixelOnIndex, self.numPixels, self.hue)
        newPixelOn = animationResult[0]
        newHue = animationResult[1]

        # Turn off prev pixel
        self.updatePixel(self.pixelOnIndex, (0,0,0))

        # Turn on next pixel
        self.updatePixel(newPixelOn, self.colorHSV(newHue, 255, 255))
        self.setPixelOnIndex(newPixelOn)
        self.setHue(newHue)
        self.setRandomPixelBlinkCount(self.randomPixelBlinkCount + 1)

        isAnimationCycleEnded = self.calcRandomPixelBlinkCycleEnd()
        
        if (isAnimationCycleEnded):
            self.setIsAnimationEnabled(False)
            self.setRandomPixelBlinkCount(0)
            self.updateFillHSV(0, 255, 0)
            onAnimationEnd()

        self.show()

        time.sleep_ms(50)

    def animateBreath(self, onAnimationEnd):
        newHue = iterateHue(self.hue, 20)
        animationResult = iterateFullStripFade(self.isFadingIn, self.brightness)
        newBrightness = animationResult[0]
        newIsFadingIn = animationResult[1]

        self.setIsFadingIn(newIsFadingIn)
        self.updateFillHSV(newHue, 255, newBrightness)
        self.show()

        isAnimationCycleEnded = self.calculateBreathCycleEnd()

        if (isAnimationCycleEnded):
            self.setIsAnimationEnabled(False)
            onAnimationEnd()

        time.sleep_ms(30)

    def animate(self, onAnimationEnd):
        if (self.animationType == 0):
            return self.animateSwoosh(onAnimationEnd)
        if (self.animationType == 1):
            return self.animateBreath(onAnimationEnd)
        if (self.animationType == 2):
            return self.animateRandomBlink(onAnimationEnd)

bodyStrip = Strip(15, 0, 0)
armStrip = Strip(10, 1, 1)

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

def iterateHue(h, increment: int = 50):
    return h + increment

def iterateRandomPixelBlink(pixelOnIndex: int, numPixels: int, hue: int):
    newPixel = pixelOnIndex
    
    while(newPixel == pixelOnIndex):
        newPixel = randint(0, numPixels - 1)

    newHue = hue + randint(0, floor(MAX_HUE / 10))

    return newPixel, newHue

def iterateSwooshIndex(smooshIndex: float):
    newSwooshIndex = smooshIndex + 0.1
    return newSwooshIndex


while(True):

    if (bodyStrip.isAnimationEnabled):
        bodyStrip.animate(lambda: armStrip.setIsAnimationEnabled(True))


    if (armStrip.isAnimationEnabled):
        armStrip.animate(lambda: bodyStrip.setIsAnimationEnabled(True))