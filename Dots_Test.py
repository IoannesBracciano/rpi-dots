# Python script to test the functionality of Dots.py
#
# Author and Maintainer
# Ioannes Bracciano <john.bracciano@gmail.com>


import unittest
import Dots


# Tests the basic text formatting
class TextFormattingTestCase(unittest.TestCase):
  
  def setUp(self):
    self.buffer = Dots._Buffer().parse("\tDots\nBy Ioannes Bracciano")
    self.first_line = self.buffer.line(0)
    self.second_line = self.buffer.line(1)


  # Tests the number of _Lines in the _Buffer after the parsing of the text
  def test_num_of_lines(self):
    self.assertEqual(self.buffer.line_count(), 2,\
        "Expected 2 _Lines in _Buffer, found {}".format(self.buffer.line_count()))


  # Tests the number of _Cells in each _Line in the _Buffer
  def test_num_of_cells(self):
    self.assertEqual(self.first_line.cell_count(), 2,\
        "Expected 2 _Cells in first _Line, found {}".format(self.first_line.cell_count()))

    self.assertEqual(self.second_line.cell_count(), 1,\
        "Expected 1 _Cell in second _Line, found {}".format(self.second_line.cell_count()))


  # Tests the length of the formatted contents of each _Line in the _Buffer
  def test_line_length(self):
    self.assertEqual(len(str(self.first_line)), 16,\
        "Expected 16 characters in first line, found {}".format(len(str(self.first_line))))
    self.assertEqual(len(str(self.second_line)), 16,\
        "Expected 16 characters in first line, found {}".format(len(str(self.second_line))))


  # Tests tab stop positions and their effect in formatting the contents of the
  # _Lines in the _Buffer
  def test_line_tab_stops(self):

    # Testing auto tab stops
    tab_stops = self.first_line._tab_stops

    self.assertEqual(len(tab_stops), 1,\
        "Expected 1 tab stop in first _Line, found {}".format(len(tab_stops)))
    self.assertEqual(tab_stops[0], 8,\
        "Expected tab stop at position 8, found at {}".format(tab_stops[0]))
    self.assertEqual(str(self.first_line), "        Dots    ",\
        "Malformatted text in first line: {}".format(str(self.first_line)))

    tab_stops = self.second_line._tab_stops

    self.assertEqual(len(tab_stops), 0,\
        "Expected 0 tab stops in second _Line, found {}".format(len(tab_stops)))
    self.assertEqual(str(self.second_line), "By Ioannes Bracc",\
        "Malformatted text in second line: {}".format(str(self.second_line)))

    # Testing custom tab stops
    self.first_line.set_tab_stops([6])
    tab_stops = self.first_line._tab_stops
    
    self.assertEqual(tab_stops[0], 6,\
        " Expected tab stop at position 6, found at {}".format(tab_stops[0]))
    self.assertEqual(str(self.first_line), "      Dots      ",\
        "Malformatted text in first line: {}".format(str(self.second_line)))

    # Tests malformed tab stops
    with self.assertRaises(ValueError) as cm:
      self.first_line.set_tab_stops([9,2])
    self.assertTrue("ascending" in cm.exception.message.lower())

    with self.assertRaises(ValueError) as cm:
      self.first_line.set_tab_stops([])
    self.assertTrue("fewer" in cm.exception.message.lower())

    

# Tests text scrolling
class TextScrollingTestCase(unittest.TestCase):

  def setUp(self):
    self.buffer = Dots._Buffer().parse("\
1\t2\t3\t4\t5\t6\t7\t8\t9\t10\t11\t12\t13\t14\t15\t16\n\
1\t2\t3\t4\t5\t6\t7\t8\t9\n\
This\tis\ta\tthird\tline")
    self.L1 = self.buffer.line(0)
    self.L2 = self.buffer.line(1)
    self.L3 = self.buffer.line(2)

    self.L1.set_tab_stops([2,   4,  6,  8,  10, 12, 14, 16,\
                           18,  20, 22, 24, 26, 28, 30, 32])

  
  # Tests the scrolling of the contents on the screen line by line
  def test_screen_scrolling(self):
    self.assertEqual(self.buffer.line(), self.L1,\
        "Expected current _Line in _Buffer to be '{}' before scrolling".format(str(self.L1)))
    self.buffer.scroll_to(1)
    self.assertEqual(self.buffer.line(), self.L2,\
        "Expected current _Line in _Buffer to be '{}' after scrolling to it".format(str(self.L2)))
    self.buffer.scroll_to(9)
    self.assertEqual(self.buffer.line(), self.L3,\
        "Expected current _Line in _Buffer to be '{}' after scrolling past it".format(str(self.L3)))
    self.buffer.scroll_to(-1)
    self.assertEqual(self.buffer.line(), self.L1,\
        "Expected current _Line in _Buffer to be '{}' after scrolling before it".format(str(self.L1)))


  def test_line_scrolling(self):
    self.assertEqual(str(self.L1), "1 2 3 4 5 6 7 8 ",\
        "Unexpected contents in first _Line before scrolling: {}".format(str(self.L1)))

    self.L1.scroll_to(8) # Scroll to eighth cell
    self.assertEqual(str(self.L1), "9 10111213141516",\
        "Unexpected contents in first _Line after scrolling to the 8th cell: {}".format(str(self.L1)))
    self.L1.scroll_to(17)
    self.assertEqual(str(self.L1), "16",\
        "Unexpected contents in first _Line after scrolling past its last cell: {}".format(str(self.L1)))
    self.L1.scroll_to(-1)
    self.assertEqual(str(self.L1), "1 2 3 4 5 6 7 8 ",\
        "Unexpected contents in first _Line after scrolling before its first cell: {}".format(str(self.L1)))
    


  def test_cell_scrolling(self):
    self.assertEqual(str(self.L3), "Thiis a  thiline",\
        "Unexpected contents in third _Line before scrolling: {}".format(str(self.L3)))
    self.L3.set_tab_stops([5,8,10,12])
    self.assertEqual(str(self.L3), "This is a thline",\
        "Unexpected contents in third _Line after setting tab stops: {}".format(str(self.L3)))
    self.L3[3].scroll_to(1)
    self.assertEqual(str(self.L3), "This is a hiline",\
        "Unexpected contents in third _Line after scrolling 3rd cell by 1 character: {}".format(str(self.L3)))
    self.L3[3].scroll_to(6)
    self.assertEqual(str(self.L3), "This is a rdline",\
        "Unexpected contents in third _Line after scrolling 3rd cell past the last character: {}".format(str(self.L3)))
    self.L3[3].scroll_to(-1)
    self.assertEqual(str(self.L3), "This is a thline",\
        "Unexpected contents in third _Line after scrolling 3rd cell before the first character: {}".format(str(self.L3)))
    



if __name__ == "__main__":
  suite = unittest.TestLoader().loadTestsFromTestCase(TextFormattingTestCase)
  unittest.TextTestRunner(verbosity=2).run(suite)

  suite = unittest.TestLoader().loadTestsFromTestCase(TextScrollingTestCase)
  unittest.TextTestRunner(verbosity=2).run(suite)

