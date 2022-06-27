import time
from gammaCorrection import gammaCorrectRgb
from neopixel import Neopixel

index = 0
numpix = 10
strip = Neopixel(numpix, 0, 0, "GRB")

strip.brightness(100)

hue = 0
while(True):
    color = strip.colorHSV(hue, 255, 150)
    strip.set_pixel(index, gammaCorrectRgb(color))
    strip.show()
    time.sleep_ms(100)

    
    hue += 550

    if (index < numpix - 1):
        index += 1
    else:
        index = 0