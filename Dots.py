# Copyright (c) 2017 Ioannes Bracciano
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


'''
  This python module greatly extends the functionality of
  16x1 or 16x2 dot character LCD displays, using the HD44780
  controller or one alike, as well as it provides an easy way
  to interact with it. Briefly you can:
    * Display text on the LCD screen (duh)
    * Split the text into unlimited lines and lines into unlimited cells
    * Format cell widths using tab stops
    * Scroll through all of the contents with ease and in many different ways
    * Load extended dot patterns and draw them on the screen (coming soon)


  Author and Maintainer
  Ioannes Bracciano <john.bracciano@gmail.com>
'''


# Constants and Flags
# -------------------

# Current module version
VERSION = '0.7.1'

# Defines the number of lines on the LCD screen
LCD_LINES = 2

# Defines the number of characters per line
CHARS_PER_LINE = 16

# Flag to make cursor visible via the `cursor` function
CURSOR_VISIBLE = 0x01

# Flag to make cursor blink via the `cursor` function
CURSOR_BLINK = 0x02


# _Buffer is a helper class to control the module's
# internal text buffer. It parses the given text to lines
# ad holds an internal pointer to the current line
class _Buffer:

  # Parses the raw string internally and constructs the lines array
  # If 'string' is None, then it clears the buffer's contents
  def parse(self, string):
    self._lines = []
    self._raw = string

    if self._raw:
      for line in self._raw.split('\n'):
        self._lines += [ _Line(self).parse(line) ]
      
    self._reset()
    return self


  # Appends more lines at the end of the buffer
  def append(self, string):
    return self.parse(self._raw + '\n' + string)

  
  # Clears the buffer contents
  def clear(self):
    return self.parse(None)


  # Returns the _Line of text at index
  # If index is left blank, _current_line_index is used
  # If index exceeds line_count(), it returns None
  def line(self, index=None):
    if self._lines:
      index = self._current_line_index if index == None else index
      #return self._lines[ index % self.line_count() ]
      if index < self.line_count():
        return self._lines[ index ]
    
    return None


  # Returns the number of lines in the buffer
  def line_count(self):
    return len(self._lines)


  # Returns True if the given _Line is currently displayed on the LCD
  # Returns False otherwise
  def is_displayed(self, line):
    index = self._lines.index(line)
    if index is not None and index in range(self._current_line_index,\
                                self._current_line_index + LCD_LINES):
      return True
    else: return False


  # Returns True if contents can scroll to 'position', False otherwise
  # In other words True is returned if 'position' is within [0, line_count())
  def scrolls_to(self, position):
    return position in range(self.line_count())


  # Scrolls to the line at 'position'
  # If 'position' is negative it scrolls to the first line, whereas
  # if 'position' is equal or greater line_count(), it scrolls to the last
  # _Line
  def scroll_to(self, position):
    if self.scrolls_to(position):
      self._current_line_index = position
    else:
      self.scroll_top() if position < 0 else self.scroll_bottom()


  # Scrolls the contents down by 'offset' lines
  # Returns True if contents will further scroll to that direction by the same
  # amount, False otherwise
  def scroll_down(self, offset=1):
    self.scroll_to( self._current_line_index + offset )
    return self.scrolls_to( self._current_line_index + offset )


  # Scrolls the contents up by 'offset' lines
  # Returns True if contents will further scroll to that direction by the same
  # amount, False otherwise
  def scroll_up(self, offset=1):
    self.scroll_to( self._current_line_index - offset )
    return self.scrolls_to( self._current_line_index - offset )


  # Scrolls the contents to the first line in the buffer
  def scroll_top(self):
    self.scroll_to(0)


  # Scrolls the contents to the last line in the buffer
  def scroll_bottom(self):
    self.scroll_to(self.line_count() - 1)


  # Concatenates all the lines in the buffer into one formatted string
  # Mainly to be called from __str__() so users are able to print the
  # buffer on the computer without any effort
  def _format_contents(self):
    if self._lines:
      formatted = ""

      for i in range(LCD_LINES):
        formatted += str(self[ self._current_line_index + i ]) + '\n'

      return formatted


  # Resets the internal line index
  def _reset(self):
    self._current_line_index = 0


  # Initializes the _Buffer
  def __init__(self):
    self._lines = []
    self._current_line_index = 0

  
  # Uses _format_contents to return a formatted string of its contents
  # Falls back to its name
  def __str__(self):
    return self._format_contents() or _Buffer.__name__


  # Overloads operator.len() to return the _Buffer's line_count()
  def __len__(self):
    return self.line_count()


  # Overloads operator [] to access a line in the buffer
  def __getitem__(self, index):
    return self.line(index)


  # Returns the internal _lines array when involved in for...in loops
  def __iter__(self):
    return iter(self._lines)


# Class _Buffer END
################################################################################


# Helper class that formats a given line of string for display
# on the lcd screen
# The text in the line can be split into multiple cells using tab stops
# Each cell is displayed and scrolled seperately on the screen
class _Line:

  # Parses the given string
  def parse(self, string):
    self._cells = []
    self._raw = string

    if self._raw:
      cells = self._raw.split('\t')

      for cell in cells:
        self._cells += [ _Cell(self, text=cell) ]
      
      self._auto_tab_stops()
    
    self._reset()
    return self


  # Returns the text contained in cell at index
  # If index is left blank, the internal cell index is used
  # If index exceeds cell_count(), it circles back to the beginning
  def cell(self, index=None):
    if self._cells:
      index = self._current_cell_index if index == None else index
      # return self._cells[ index % self.cell_count() ]
      if index < self.cell_count():
        return self._cells[ index ]
    
    return None


  # Returns the number of cells in the last parsed line of text
  # That typically corresponds to the number of '\t' characters
  # in the line plus 1
  def cell_count(self):
    return len(self._cells)


  # Lets the user set custom tab stops
  # Tab stops are used to control the number and width of cells
  # in a line of text. These cells will be displayed and scrolled
  # independently. You can change between cells using the '\t'
  # character when you provide the string to be written on the LCD screen
  def set_tab_stops(self, tab_stops):
    if len(tab_stops) < (len(self._cells) - 1):
      raise ValueError("Fewer tab stops given than tab characters in line")
    if not all(x < y for x, y in zip(tab_stops, tab_stops[1:])):
      raise ValueError("Tab stops must be in ascending order")
 
    self._tab_stops = tab_stops
    self._distribute_cell_widths()


  # Returns True if this _Line is currently displayed on the LCD screen
  # Returns False otherwise
  def is_displayed(self, cell=None):
    if cell:
      index = self._cells.index(cell)
    
      if self.is_displayed() and index in range(self._current_cell_index,\
                   self._current_cell_index + self._last_visible_cell_index):
        return True
      else: return False

    else: return self._parent.is_displayed(self)


  # Returns True if contents can scroll to 'position', False otherwise
  # In other words True is returned if 'position' is within [0, cell_count())
  def scrolls_to(self, position):
    return position in range(self.cell_count())


  # Scrolls to the cell at 'position'
  # If 'position' is negative it scrolls to the first cell, whereas
  # if 'position' is equal or grater than cell_count(), it scrolls to the last
  # cell
  def scroll_to(self, position):
    if self.scrolls_to(position):
      self._current_cell_index = position
    else:
      self.scroll_start() if position < 0 else self.scroll_end()


  # Scrolls the contents to the left by 'offset' cells
  def scroll_left(self, offset=1):
    self.scroll_to( self._current_cell_index + offset )
    return self.scrolls_to( self._current_cell_index + offset )


  # Scrolls the contents to the right by 'offset' cells
  def scroll_right(self, offset=1):
    self.scroll_to( self._current_cell_index - offset )
    return self.scrolls_to( self._current_cell_index - offset )


  # Scrolls to the start of the line
  def scroll_start(self):
    self.scroll_to(0)


  # Scrolls to the end of the line
  def scroll_end(self):
    self.scroll_to(self.cell_count() - 1)


  # Turns its contents into a formatted string to be written on the LCD screen
  def _format_contents(self, tab_stops=None):
    formatted = ""

    if self._cells:
      for cell in self._cells[self._current_cell_index:]:
        if len(formatted) >= CHARS_PER_LINE: break
        formatted += str(cell)
        self._last_visible_cell_index = self._cells.index(cell)

      return formatted[:CHARS_PER_LINE]


  # Resets the internal cell index
  def _reset(self):
    self._current_cell_index = 0
    self._last_visible_cell_index = 0


  # Generates evenly spaced tab stops based on their count
  # Up to 16 tab stops can be generated automatically and fitted
  # within the 16-character line of the lcd screen. If their width
  # cannot be divided exactly to an integer amount, it will be floored
  # to the nearest integer, so contents of the last cell might be
  # partly or totally hidden, and you should call scroll_left() on the
  # line to make them visible
  def _auto_tab_stops(self):
    count = min(self.cell_count(), 16)
    tab_stops = [] 
    for i in range(count - 1):
      tab_stops += [(16 / count) * (i + 1)]

    self.set_tab_stops(tab_stops)
  
  
  # Distributes the width of each cell in the line
  def _distribute_cell_widths(self):
    for cell in self._cells:
      index = self._cells.index(cell)
      cell.set_width( self._calculate_cell_width(index) )


  # Calculates the width of a cell based on its bounding tab stops
  # If index is left blank, _current_cell_index will be used.
  # Notice that this function does not check if index is out of bounds
  def _calculate_cell_width(self, index):
    last = ([0] + self._tab_stops)[-1]
    padding_end = 16 - (last % 16)
    cell_start = ([0] + self._tab_stops)[index]
    cell_end   = (self._tab_stops + [last + padding_end])[index]
    return cell_end - cell_start
     

  # Initializes the _Line
  def __init__(self, parent):
    if not isinstance(parent, _Buffer):
      raise TypeError("Parent should be an instance of _Buffer")
    self._parent = parent
    self.parse(None)


  # Returns the formatted contents of the line that are to be written
  # on the lcd screen, or __name__ if no line is yet parsed
  def __str__(self):
    return self._format_contents() or _Line.__name__


  # Returns the _Line's cumulative sum of its cell widths
  def __len__(self):
    length = 0
    for cell in self._cells:
      length += cell.get_width()
    return length


  # Makes it possible to access a _Cell by applying indexing on the _Line
  def __getitem__(self, index):
    return self.cell(index)


  # The next two methods implement the iterator protocol in
  # order to make instaces of this class iterable. Users can
  # therefore iterate between cells in a line easily in a
  # for...in loop
  def __iter__(self):
    return iter(self._cells)


# Class _Line END
################################################################################


class _Cell:

  # Sets the width of the cell
  def set_width(self, width):
    if width < 1 or width > CHARS_PER_LINE:
      raise ValueError("Width of cell should be between 1 and {} characters"\
                                                      .format(CHARS_PER_LINE))

    self._width = width
    self.scroll_to(0)


  # Returns the width of the cell
  def get_width(self):
    return self._width


  # Returns true if the _Cell is currently displayed on the LCD screen
  # Returns False otherwise
  def is_displayed(self):
    return self._parent.is_displayed(self)


  # Returns True if contents can scroll to 'position', False otherwise
  # Contents can scroll until there are no more hidden characters past the
  # right boundary of the cell
  def scrolls_to(self, position):
    return position in range(len(self.text) - self.get_width() + 1)


  # Scrolls the text to the character at 'position' within the displayed string
  # If 'position' is zero or negative, it scrolls to the top, whereas if
  # 'position' causes the last character in the text to be displayed before the
  # right boundary of the cell (displaces the text too much), it scrolls to the
  # end
  def scroll_to(self, position):
    if self.scrolls_to(position):
      self._scroll_offset = position
    elif len(self.text) > self.get_width():
      self.scroll_start() if position < 0 else self.scroll_end()


  # Scrolls the contents to the left by 'offset' characters
  def scroll_left(self, offset=1):
    self.scroll_to( self._scroll_offset + offset )
    return self.scrolls_to( self._scroll_offset + offset )


  # Scrolls the contents to the right by 'offset' characters
  def scroll_right(self, offset=1):
    self.scroll_to( self._scroll_offset - offset )
    return self.scrolls_to( self._scroll_offset - offset )


  # Scrolls to the start of the text
  def scroll_start(self):
    self.scroll_to(0)


  # Scrolls to the end of the text
  def scroll_end(self):
    self.scroll_to(len(self.text) - self.get_width())


  # Returns the portion of text that fits inside the cell. If the
  # text length is larger than the cell's width, it can be scrolled
  # using scroll_right(), scroll_left() or scroll_to() methods
  def _format_contents(self):
    start = self._scroll_offset
    end = start + self.get_width()
    return self.text[ start : end ].ljust(self.get_width())


  # Initializes the cell with some text and specifies its width
  # (16 characters by default)
  def __init__(self, parent, text, width=16):
    if not isinstance(parent, _Line):
      raise TypeError("Parent must be an instance of _Line")
    self._parent = parent
    self.text = text
    self.set_width(width)
    self._scroll_offset = 0


  def __str__(self):
    return self._format_contents() or _Cell.__name__


# Class _Cell END
################################################################################


from abc import ABCMeta, abstractmethod
from threading import Timer


# _Scroller is a base class that serves as a common ancestor of the concrete
# implementation of all the _Scroller classes. It provides the common interface
# used by _ScrollerBuilder
class _Scroller:

  # Make this an abstract class 
  __metaclass__ = ABCMeta


  # Performs the scrolling once
  def once(self):
    self._perform_scroll()


  # Performs the scrolling repeatedly every 'seconds'
  # This method starts a new Timer that calls the same function after the given
  # time delay in seconds, until the contents of the container can no longer
  # scroll. If circular is set to True, the scrolling is going to repeat back
  # and forth forever until stop() is called
  def every(self, seconds, callback=None):
    if not self._stopped:
      if self._perform_scroll():
        Timer(seconds, self.every, [seconds, callback]).start()
      elif callback: Timer(seconds, callback).start()
    else: self._stopped = False

    return self

  # Scrolls indefinitely left and right every 'seconds'
  def bounce(self, seconds):

    def _bounce():
      if not self._stopped:
        self.every(seconds, _reverse)

    def _reverse():
      if not self._stopped:
        self._scroll_offset = -self._scroll_offset
        _bounce()

    _bounce()
    return self


  # Stops the scrolling of the contents
  def stop(self):
    self._stopped = True


  # Registers a scroll of the contents of a container by offset many places
  # A positive value scrolls the contents to a positive direction while a
  # negative one scrolls the contents to a negative direction, however these
  # directions are defined by the concrete child classes
  def _scroll(self, offset):
    self._scroll_offset = offset


  # Performs the actual scroll by the value previously specified with _scroll()
  # Child classes implement this method to provide custom scroll functionality
  # for all the different types of containers (_Buffer, _Line and _Cell)
  @abstractmethod
  def _perform_scroll(self):
    pass


# Class _Scroller END
################################################################################


# _ScreenScroller is a _Scroller helper class that provides an easy way to
# scroll the contents on the LCD screen line by line, if the _Buffer contains
# more lines than the screen itself
class _ScreenScroller(_Scroller):

  # Scrolls the contents in the buffer upwards
  # If 'by' value scrolls to an offset past the buffer contents, it simply
  # reaches the top of the scrolling (scrolls to the first line)
  # Returns self for call chaining
  def up(self, by=1):
    self._scroll( -by )
    return self


  # Scrolls the contents in the buffer downwards
  # If 'by' value scrolls to an offset past the buffer contents, it simply
  # reaches the bottom of the scrolling (scrolls to the last line)
  # Returns self for call chaining
  def down(self, by=1):
    self._scroll( +by )
    return self


  # Interfaces with the buffer to perform the actual scrolling
  # Returns True if contents can further scroll to that direction,
  # False otherwise
  def _scroll_up(self, offset):
    return self.__buffer.scroll_up(offset)


  # Interfaces with the buffer to perform the actual scrolling
  # Returns True if contents can further scroll to that direction,
  # False otherwise
  def _scroll_down(self, offset):
    return self.__buffer.scroll_down(offset)
  
  
  # Performs a scroll up of the contents on the screen by abs(_scroll_value)
  # lines if _scroll_value is negative, or a scroll down by the same amount
  # if positive
  def _perform_scroll(self):
    will_scroll_further = False

    if self._scroll_offset < 0:
      will_scroll_further =  self._scroll_up(abs(self._scroll_offset))
    else:
      will_scroll_further = self._scroll_down(self._scroll_offset)

    self._rewrite()
    return will_scroll_further


  # Initializes the _Scroller
  def __init__(self, buffer, rewrite):
    self.__buffer = buffer
    self._rewrite = rewrite
    self._scroll_offset = buffer._current_line_index
    self._stopped = False


# Class _ScreenScroller END
################################################################################


# _LineScroller is a _Scroller helper class that provides an easy way to
# scroll the contents of a _Line on the LCD screen cell by cell, if the _Line
# is longer than the screen's width
class _LineScroller(_Scroller):

  # Scrolls the contents in the _Line to the right
  # If 'by' value defines  an offset past the start of the _Line, it simply
  # scrolls to the first cell, ignoring the extra offset
  # Returns self for call chaining
  def right(self, by=1):
    self._scroll( -by )
    return self


  # Scrolls the contents in the _Line to the left
  # If 'by' value defines an offset past the end of the _Line, it simply
  # scrolls to the last cell, ignoring the extra offset
  # Returns self for call chaining
  def left(self, by=1):
    self._scroll( +by )
    return self


  # Interfaces with the _Line to perform the actual scrolling
  # Returns True if contents can further scroll to that direction,
  # False otherwise
  def _scroll_right(self, offset):
    return self._line.scroll_right(offset)


  # Interfaces with the _Line to perform the actual scrolling
  # Returns True if contents can further scroll to that direction,
  # False otherwise
  def _scroll_left(self, offset):
    return self._line.scroll_left(offset)
  
  
  # Performs a scroll of the contents to the right by abs(_scroll_value) cells
  # _scroll_offset is negative, or a scroll to the left by the same amount if
  # _scroll_offset is positive
  def _perform_scroll(self):
    will_scroll_further = False

    if self._scroll_offset < 0:
      will_scroll_further =  self._scroll_right(abs(self._scroll_offset))
    else:
      will_scroll_further = self._scroll_left(self._scroll_offset)

    if self._line.is_displayed(): self._rewrite()

    return will_scroll_further


  # Initializes the _Scroller
  def __init__(self, line, rewrite):
    self._line = line
    self._rewrite = rewrite
    self._scroll_offset = line._current_cell_index
    self._stopped = False


# Class _LineScroller END
################################################################################


# _CellScroller is a _Scroller helper class that provides an easy way to
# scroll the contents of a _Cwithin a _Line independently, character by
# character, if the text displayed in it is longer than its width
class _CellScroller(_Scroller):

  # Scrolls the contents in the _Cell to the right
  # If 'by' value defines an offset past the first character in the text,
  # it simply scrolls to the start, ignoring the extra offset
  # Returns self for call chaining
  def right(self, by=1):
    self._scroll( -by )
    return self


  # Scrolls the contents in the _Cell to the left
  # If 'by' value defines an offset past the cell contents, it simply
  # scrolls to the end, ignoring the extra offset
  # Returns self for call chaining
  def left(self, by=1):
    self._scroll( +by )
    return self


  # Interfaces with the _Cell to perform the actual scrolling
  # Returns True if contents can further scroll to that direction,
  # False otherwise
  def _scroll_right(self, offset):
    return self._cell.scroll_right(offset)


  # Interfaces with the _Cellr to perform the actual scrolling
  # Returns True if contents can further scroll to that direction,
  # False otherwise
  def _scroll_left(self, offset):
    return self._cell.scroll_left(offset)
  
  
  # Performs a scroll of the contents to the right by abs(_scroll_value)
  # characters _scroll_offset is negative, or a scroll to the left by the same
  # amount if _scroll_offset is positive
  def _perform_scroll(self):
    will_scroll_further = False

    if self._scroll_offset < 0:
      will_scroll_further =  self._scroll_right(abs(self._scroll_offset))
    else:
      will_scroll_further = self._scroll_left(self._scroll_offset)

    if self._cell.is_displayed(): self._rewrite()

    return will_scroll_further


  # Initializes the _Scroller
  def __init__(self, cell, rewrite):
    self._cell = cell
    self._rewrite = rewrite
    self._scroll_offset = cell._scroll_offset
    self._stopped = False


# Class _CellScroller END
################################################################################


from sys import modules

# Get a pointer to this module
this = modules[__name__]


# The buffer is used to internally hold and manipulate
# the string that is currently shown on the LCD
this.__buffer = _Buffer()


from ifc import HD44780


# Initializes controller and turns the display on
def init(pins=None, lines=None):
  global LCD_LINES
  LCD_LINES = lines or LCD_LINES

  HD44780.init(pins)
  HD44780.set_function( bit_mode = len(HD44780.__pins['db']),
                        num_lines = LCD_LINES   )
  HD44780.display_on()


# Clears the display of all text
def clear():
  HD44780.clear()


# Displays the given text on the LCD screen
# The text is saved and parsed in ythe _Buffer. You can provide an unlimited
# number of characters and lines. You can use the '\t' character to split a
# line into different cells and then set_tab_stops() to format their width.
def display(text):
  this.__buffer.parse(text)
  __rewrite()


# Formats the string currently displayed on the screen
# tab_stops are used to divide the screen into multiple parts (columns). These
# columns will display text in their own width and scroll independently. You
# can change between columns using the \t character when you provide the string
# to be written on the LCD
# Future development will include text alignment options
def format(tab_stops):

  if tab_stops:
    if all(isinstance(x, (int, long)) for x in tab_stops):
      for line in this.__buffer:
        line.set_tab_stops(tab_stops)
    elif len(tab_stops) == len(this.__buffer):
      for line in this.__buffer:
        line.set_tab_stops(tab_stops[ this.__buffer._current_line_index ])
    else:
      for n_tab_stops in tab_stops:
        n = len(n_tab_stops)
        for line in this.__buffer:
          if line.cell_count() - 1 == n:
            line.set_tab_stops(n_tab_stops)
  
  __rewrite()


# Shows or hides the cursor on the screen
def cursor(flags):
  HD44780.display_on( flags & CURSOR_VISIBLE,
                      flags & CURSOR_BLINK )


# Returns a specific _Scroller instance acording to the type of the parameter
# given
def scroll(what=None):

  if isinstance(what, _Line):
    return _LineScroller(what, __rewrite)
  elif isinstance(what, _Cell):
    return _CellScroller(what, __rewrite)
  else:
    return _ScreenScroller(this.__buffer, __rewrite)



# Returns the inner _Buffer object
def buffer():
  return this.__buffer


# Gets a _Line form the inner _Buffer
# If provided with an 'index' it returns the _Line at that index in the buffer
# If provided with an 'offset' it returns the _Line that is 'offset' many
# places away from the current _Line on the LCD screen
# If nothing is provided it returns the current _Line
def line(index=None, offset=None):

  if index:
    return this.__buffer[index]
  elif offset:
    return this.__buffer[ this.__buffer._current_line_index + offset ]
  else:
    return this.__buffer.line()


from threading import Lock


# Create a lock to secure the process of writing text on the screen because
# different threads created by multiple scrollers can mess it up
lock = Lock()


# Writes LCD_LINES many formatted _Lines from the _Buffer (if there are enough)
# to the LCD screen. This function blocks other threads from accessing it while
# it executes on some other thread
def __rewrite():
  lock.acquire()
  
  HD44780.clear()

  for offset in range(LCD_LINES):
    if line(offset=offset) == None: break
    HD44780.write(str(line(offset=offset)))
    HD44780.set_ddram_address(0x40)
  
  lock.release()

