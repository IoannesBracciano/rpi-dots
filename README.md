# Dots
A python module that facilitates the programming of 16x1 or 16x2 dor pattern
liquid crystal displays that use the HD44780 or a similar controller, by
providing an easy to use python interface to communicate with the display but
also greatly extending the capabilities of it. Briefly, you can:
* Display text on the LCD screen (duh)
* Have unlimited lines of text
* Split lines into unlimited cells and format cell widths using tab stops
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

```python
Dots.init()
```

Dots assumes that you have connected your screen to the following RPi pins
(following the BCM numbering):

```python
# Default pins
PIN_DEFS = {
    'rs':    21 if GPIO.RPI_REVISION==1 else 27,
    'e' :    22,
    'db':   [4, 25, 24, 23] }
```

These defaults come from the HD44780 module, and mostly work for RPi model B,
but you can override them by providing your own dictionary to the init function:

```python
# Define custom pins
my_pins = {
    'rs':    12
    'e' :    13,
    'db':   [17, 16, 15, 14] }

# Feed them into the init function
Dots.init(my_pins)
```

Your dictionary should not ommit any of these entries, or a KeyError will be
raised. Notice that `my_pins['db']` array starts with pin DB7 (data most
significant bit) and goes all the way down to DB4 (for 4-bit mode) or DB0 (data
least significant bit, for 8 bit-mode).

## Versioning
### version 0.7 (**current**)
An early stage of the module that allows to:
* Display text on the LCD screen
* Split the text into unlimited lines and lines into unlimited cells
* Format cell widths using tab stops
* Scroll the screen up and down, lines and cells left and right, once or
  every number of seconds

---

Author and Maintainer: [Ioannes Bracciano]

[Read the license]()


