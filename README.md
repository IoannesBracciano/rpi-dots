# Dots
A python module that facilitates the programming of 16x1 or 16x2 dor pattern
liquid crystal displays that use the HD44780 or a similar controller, by
providing an easy to use python interface to communicate with the display but
also greatly extending the capabilities of it. Briefly, you can:
* Display text on the LCD screen (duh)
* Split the text into unlimited lines and lines into unlimited cells
* Format cell widths using tab stops
* Scroll through all of the contents with ease and in many different ways
* Load extended dot patterns and draw them on the screen (coming soon)

## Prerequisities
This module makes use of the HD44780 module, found also in my rpi-ifc repo

## Installation
Just grab the files, put them in the same directory as your project and import
appropriately. Don't forget to also copy thi ifc folder that contains the
necessary dependency modules

## Usage
You should initialize the module before doing anything else using:

```
Dots.init()
```

Dots assumes that you have connected your screen to the following RPi pins
(following the BCM numbering):

```
PIN_DEFS = {
    'rs':    21 if GPIO.RPI_REVISION==1 else 27,
    'e' :    22,
    'db':   [4, 25, 24, 23] }
```

These defaults come from the HD44780 module, and mostly work for RPi model B,
but you can override them by providing your own dictionary to the init function:

```
my_pins = {
    'rs':    12
    'e' :    13,
    'db':   [17, 16, 15, 14] }

Dots.init(my_pins)
```

Notice that `my_pins['db']` array starts with pin DB7 (the least significant)
4 'db' pins will initialize the LCD to 4-bit mode, while 8 will initialize to
8 bit-mode



