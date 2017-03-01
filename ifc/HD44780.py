'''
  Copyright (c) 2017 Ioannes Bracciano

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
'''


# This module Provides an interface for HD44780 controllers, or other
# controllers that have a similar instruction set as HD44780
#
# TODO Implement reading data back from the controller through the rw pin
#      Currently not implemented as voltage incompatibility between the HD44780
#      and the RPi require a regulator so as not to burn the latter
#
# Author and Maintainer
# Ioannes Bracciano <john.bracciano@gmail.com>


from RPi import GPIO as GPIO
from time import sleep


# Default pin numbers (BCM numbering)
PIN_DEFS = {
    'rs':    21 if GPIO.RPI_REVISION==1 else 27,
    'e' :    22,
    'db':   [4, 25, 24, 23] }
#            ^  ^   ^   ^
#          DB7 DB6 DB5 DB4


###########################
# --- INSTRUCTION SET --- #
###########################

                        #                Pin order              #
                        # RS RW DB7 DB6 DB5 DB4 DB3 DB2 DB1 DB0 #

# Clear Display (rewrites RAM with spaces)
__INSTR_CLR_DISP                      = 0b0000000001

# Return Home (RAM contents not changed)
__INSTR_RET_HOME                      = 0b0000000010

# Set cursor moving left without screen shift
__INSTR_ENTRY_MODE_LEFT_NO_SCR_SHIFT  = 0b0000000100

# Set cursor moving left with screen shift
__INSTR_ENTRY_MODE_LEFT_SCR_SHIFT     = 0b0000000101

# Set cursor moving left without screen shift
__INSTR_ENTRY_MODE_RIGHT_NO_SCR_SHIFT = 0b0000000110

# Set cursor moving left with screen shift
__INSTR_ENTRY_MODE_RIGHT_SCR_SHIFT    = 0b0000000111

# Turns on display
__INSTR_DISP_ON_CURSOR_OFF_BLINK_OFF  = 0b0000001100

# Turns display and cursor on
__INSTR_DISP_ON_CURSOR_ON_BLINK_OFF   = 0b0000001110

# Turns display, cursor and cursor blink on
__INSTR_DISP_ON_CURSOR_ON_BLINK_ON    = 0b0000001111

# Turns display off
__INSTR_DISP_OFF                      = 0b0000001000

# Shifts cursor to the left
# Same as subtracting 1 from the address counter
__INSTR_SHIFT_CURSOR_LEFT             = 0b0000010000

# Shifts cursor to the right
# Same as incrementing the address counter by 1
__INSTR_SHIFT_CURSOR_RIGHT            = 0b0000010100

# Shifts screen to the left
# Results to text on the screen being shifted,
# but cursor position remains the same
__INSTR_SHIFT_SCREEN_LEFT             = 0b0000011000

# Shifts screen to the right
# Results to text on the screen being shifted,
# but cursor position remains the same
__INSTR_SHIFT_SCREEN_RIGHT            = 0b0000011100

# Sets 4 bit mode, 1 line of text and 5x8 dots font size
__INSTR_SET_4_BITS_1_LINE_5_X_8_DOTS  = 0b0000100000

# Sets 4 bit mode, 1 line of text and 5x11 dots font size
__INSTR_SET_4_BITS_1_LINE_5_X_11_DOTS = 0b0000100100

# Sets 4 bit mode, 2 lines of text
# (font is automatically set to 5x8 dots in 2 line mode)
__INSTR_SET_4_BITS_2_LINES            = 0b0000101000

# Sets 8 bit mode, 1 line of text and 5x8 dots font size
__INSTR_SET_8_BITS_1_LINE_5_X_8_DOTS  = 0b0000110000

# Sets 8 bit mode, 1 line of text and 5x11 dots font size
__INSTR_SET_8_BITS_1_LINE_5_X_11_DOTS = 0b0000110100

# Sets 8 bit mode, 2 lines of text
# (font is automatically set to 5x8 dots in 2 line mode)
__INSTR_SET_8_BITS_2_LINES            = 0b0000111000

# Sets the CGRAM address. CGRAM is where user can load
# up to 8 of his own dot patterns for display on the sreen
# Remember to replace last 6 bits with the actual address
__INSTR_SET_CGRAM_ADDR                = 0b0001000000

# Sets the DDRAM address
# In single line display mode, the addresses span from
# 0x00 to 0x4f
# When both lines of text are used, the addresses span
# from 0x00 to 0x27 for th first line and from 0x40 to
# 0x67 for the second line
# Remember to replace last 7 bits with the actual address
__INSTR_SET_DDRAM_ADDR                = 0b0010000000

# Writes data to CGRAM or DDRAM, according to the
# previously set address (see __INSTR_SET_xxRAM_ADDR)
# Remember to replace last 8 bits with the character code
__INSTR_WRITE_TO_RAM                  = 0b1000000000


from sys import modules

# Getting a pointer to this module
this = modules[__name__]


# Initializes HD44780 driver
# This needs to be called before any other function, providing the correct
# pin numbers (BCM numbering, most significant first)
def init (pins=None):
  if pins:
    if "rs" not in pins or "e" not in pins or "db" not in pins:
      raise KeyError("Invalid format of pins dictionary.\
          Keys 'rs', 'e' and 'db' must be included")

  this.__pins = pins or PIN_DEFS
  this.__bit_mode = len(this.__pins['db'])
  this.__lines = 1
  this.cursor = True
  this.cursor_blink = True

  GPIO.setmode(GPIO.BCM)
  GPIO.setup(this.__pins['rs'], GPIO.OUT)
  GPIO.setup(this.__pins['e'], GPIO.OUT)
  for i in range(this.__bit_mode):
    GPIO.setup(this.__pins['db'][i], GPIO.OUT)

  # Initialization process requires to send the 'Set Function'
  # instruction 3 times at specific time intervals
  # For more info checkout
  # http://www.8051projects.net/lcd-interfacing/initialization.php
  reconfigure()
  sleep(0.005)
  reconfigure()
  sleep(0.0002)
  reconfigure()

  # Initialization process complete
  # Clear the screen
  clear()


# Sets the bit mode to either 4 or 8 bits
# Call reconfigure for the changes to take effect
def set_bit_mode(bit_mode):
  if bit_mode not in (4,8):
    raise ValueError("Invalid bit mode set: {}".format(bit_mode))
  this.__bit_mode = bit_mode


# Sets the number of lines of text on the screen (1 or 2)
# Call reconfigure for the changes to take effect
def set_lines(lines):
  if lines not in (1,2):
    raise ValueError("Invalid number of lines set: {}".format(lines))
  this.__lines = lines
  

# Reconfigures the function of the controller
# You can select bit mode and lines of text calling
# the appropriate functions
def reconfigure():
  if this.__bit_mode == 4 and this.__lines == 1:
    __instruct(this.__INSTR_SET_4_BITS_1_LINE_5_X_8_DOTS)
  elif this.__bit_mode == 4 and this.__lines == 2:
    __instruct(this.__INSTR_SET_4_BITS_2_LINES)
  elif this.__bit_mode == 8 and this.__lines == 1:
    __instruct(this.__INSTR_SET_8_BITS_1_LINE_5_X_8_DOTS)
  elif this.__bit_mode == 4 and this.__lines == 2:
    __instruct(this.__INSTR_SET_8_BITS_2_LINES)

  
# Turns display on or reconfigures cursor
# appearance settings
# Remember to call this after initialization to
# turn screen on (as well as after changing the cursor parameters)
def turn_display_on():
  if this.cursor and this.cursor_blink:
    __instruct(this.__INSTR_DISP_ON_CURSOR_ON_BLINK_ON)
  elif this.cursor:
    __instruct(this.__INSTR_DISP_ON_CURSOR_ON_BLINK_OFF)
  else:
    __instruct(this.__INSTR_DISP_ON_CURSOR_OFF_BLINK_OFF)


# Turns the display off
def turn_display_off():
  __instruct(this.__INSTR_DISP_OFF)


# Clears the display
def clear():
  __instruct(this.__INSTR_CLR_DISP)


# Shift cursor to the left by the specified number of places
def shift_cursor_left(places=1):
  for i in range(places):
    __instruct(this.__INSTR_SHIFT_CURSOR_LEFT)


# Shift cursor to the right by the specified number of places
def shift_cursor_right(places=1):
  for i in range(places):
    __instruct(this.__INSTR_SHIFT_CURSOR_RIGHT)


# Shift screen to the left
def shift_screen_left(places=1):
  for i in range(places):
    __instruct(this.__INSTR_SHIFT_SCREEN_LEFT)


# Shift screen to the right
def shift_screen_right(places=1):
  for i in range(places):
    __instruct(this.__INSTR_SHIFT_SCREEN_RIGHT)


# Sets the CGRAM address
# User has the ability to load up to 8 custom character patterns
def set_cgram_address(address):
  if address < 0x00 or address >0x3f:
    raise ValueError("Invalid CGRAM address set: {}\
        CGRAM address space spans from 0x00 to 0x3f".format(address))
  __instruct(this.__INSTR_SET_CGRAM_ADDR | address)


# Sets the DDRAM address
def set_ddram_address(address):
  if this.__lines == 1:
    if address < 0x00 or address > 0x4f:
      raise ValueError("Invalid DDRAM address set: {}\
          DDRAM address space spans from 0x00 to 0x4f (1 line)".format(address))
     
  else:
    if address < 0x00 or address > 0x27 and address <0x40 or address > 0x67:
      raise ValueError("Invalid DDRAM address set: {}\
          DDRAM address space spans from 0x00 to 0x27 (first line) and\
          from 0x40 to 0x67 (second line)".format(address))

  __instruct(this.__INSTR_SET_DDRAM_ADDR | address)


# Write bytes to CGRAM or DDRAM,
# depending on the previously set address
def write(bytes_):
  if type(bytes_) == str:
    for byte in bytes_:
      __instruct(this.__INSTR_WRITE_TO_RAM | ord(byte))
  elif type(bytes_) == int:
    __instruct(this.__INSTR_WRITE_TO_RAM | (bytes_ & 0xff))
                            # & 0xff to ensure byte does not overflow


# Signals the enable pin
# (sets it to HIGH and then back to LOW)
# When signaled, the 'enable' pin lets the
# currently formed instruction be executed.
# See the controller's documentation for the
# instruction codes
def __signal_enable():
  GPIO.output(this.__pins['e'], GPIO.HIGH)
  GPIO.output(this.__pins['e'], GPIO.LOW)


# Prepares the instruction and sends it to the controller
# depending on the bit mode selected
def __instruct(instruction):
  # Prepare bits
  bits = bin(instruction)[2:].zfill(10)
  # Prepare rs pin
  GPIO.output(this.__pins['rs'], int(bits[0]))
  
  if this.__bit_mode == 4:
    __instruct_4_bit_mode(bits)
  else:
    __instruct_8_bit_mode(bits)

  sleep(0.001)


# Breaks instruction to two and send it to the controller
# 4 bits at a time  
def __instruct_4_bit_mode(bits):

  for i in range(2,6):
    GPIO.output(this.__pins['db'][i-2], int(bits[i]))

  __signal_enable()

  for i in range(6,10):
    GPIO.output(this.__pins['db'][i-6], int(bits[i]))

  __signal_enable()


# Sends the whole instruction to the controller
def __instruct_8_bit_mode(bits):
  for i in range(2,10):
    GPIO.output(this.__pins['db'][i-2], int(bits[i]))

  __signal_enable()

