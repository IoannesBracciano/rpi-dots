# Python script to test the functionality of Dots.py
#
# Author and Maintainer
# Ioannes Bracciano <john.bracciano@gmail.com>


import unittest
import Dots


class SimpleTestCase(unittest.TestCase):

  def test_parsing(self):
    # Parse an empty string
    Dots.buffer().parse("")
    # Assert no lines are in the buffer
    self.assertEqual(Dots.buffer().line_count(), 0,\
        "Expected 0 lines in buffer, found {}".format(Dots.buffer().line_count()))

    # Parse a simple string of two lines
    Dots.buffer().parse("\tDots\nBy Ioannes Bracciano")
    # Assert number of lines is 2
    self.assertEqual(Dots.buffer().line_count(), 2,\
        "Expected 2 lines in buffer, found: {}".format(Dots.buffer().line_count()))
    # Assert first line has two cells
    self.assertEqual(Dots.line(0).cell_count(), 2,\
        "Expected 2 cells in first line, found {}".format(Dots.line(0).cell_count()))
    # Assert second line has only one cell
    self.assertEqual(Dots.line(1).cell_count(), 1,\
        "Expected 1 cell in second line, found {}".format(Dots.line(1).cell_count()))
    
    # Append one more line to the buffer
    Dots.buffer().append("One more line")
    # Assert number of lines is now 3
    self.assertEqual(Dots.buffer().line_count(), 3,\
        "Expected 3 lines in buffer, found {}".format(Dots.buffer().line_count()))
  

  def test_formatting(self):
    Dots.buffer().parse("0\t1\t2\t3\t4\t5\t6\t7\t8\t9\t10\t11\t12\t13\t14\t15")
    # Assert number of cells in line
    self.assertEqual(Dots.line().cell_count(), 16,\
        "Expected 16 cells in line, found: {}".format(Dots.line().cell_count()))
    # Assert auto tab stops were calculated correctly
    self.assertListEqual(Dots.line()._tab_stops, range(1,16),\
        "Unexpected automatically set tab stops: {}".format(Dots.line()._tab_stops))
    # Assert line formats the contents correctly
    self.assertEqual(str(Dots.line()), "0123456789111111",\
        "Contents of line malformed: {}".format(str(Dots.line())))

    # Assert malformed tab stop arrays raise the correct exception
    with self.assertRaises(ValueError) as cm:
      Dots.line().set_tab_stops(range(15,0,-1))
    self.assertTrue("ascending" in cm.exception.message.lower())

    with self.assertRaises(ValueError) as cm:
      Dots.line().set_tab_stops([])
    self.assertTrue("fewer" in cm.exception.message.lower())

    # Assert setting new tab stop positions affects the formatted contents of
    # the line
    Dots.line().set_tab_stops([1,2,3,4,5,6,7,8,9,11,13,15,17,19,21])
    self.assertEqual(str(Dots.line()), "0123456789 10111",\
        "Set tab stops, but contents did not format correctly: {}".format(str(Dots.line())))


  def test_screen_scrolling(self):
    # Parse five lines of text
    Dots.buffer().parse("One\nTwo\nThree\nFour\nFive")
    # Assert we are on the first line
    self.assertEqual(Dots.line(), Dots.line(0),\
        "Unexpected current line, should be '{}', found '{}'".format(str(Dots.line(0)), str(Dots.line())))
    # Scroll down one line and assert we are on the second line
    Dots.scroll().down().once()
    self.assertEqual(Dots.line(), Dots.line(1),\
        "Unexpected current line, should be '{}', found '{}'".format(str(Dots.line(1)), str(Dots.line())))
    # Assert scrolling past the last line actually scrolls to it
    Dots.scroll().down( by=4 ).once()
    self.assertEqual(Dots.line(), Dots.line(4),\
        "Unexpected current line, should be '{}', found '{}'".format(str(Dots.line(4)), str(Dots.line())))
    # Assert scrolling before the first line actually scrolls to it
    Dots.scroll().up( by=5 ).once()
    self.assertEqual(Dots.line(), Dots.line(0),\
        "Unexpected current line, should be '{}', found '{}'".format(str(Dots.line(0)), str(Dots.line())))


  def test_line_scrolling(self):
    Dots.buffer().parse("0\t1\t2\t3\t4\t5\t6\t7\t8\t9\t10\t11\t12\t13\t14\t15")
    Dots.line().set_tab_stops(range(3,48,3))
    # Assert we are on the first cell
    self.assertEqual(Dots.line().cell(), Dots.line().cell(0),\
        "Unexpected current cell, should be '{}', found '{}'".format(str(Dots.line().cell(0)), str(Dots.line().cell())))
    # Scroll the line left and assert we are on the second cell
    Dots.scroll(Dots.line()).left().once()
    self.assertEqual(Dots.line().cell(), Dots.line().cell(1),\
        "Unexpected current cell, should be '{}', found '{}'".format(str(Dots.line().cell(1)), str(Dots.line().cell())))
    self.assertEqual(str(Dots.line()), "1  2  3  4  5  6",\
        "Performed scrolling left, but contents of line did not scroll correctly: {}".format(str(Dots.line())))
    # Assert scrolling past the last cell actually scrolls to it
    Dots.scroll(Dots.line()).left( by=15 ).once()
    self.assertEqual(Dots.line().cell(), Dots.line().cell(15),\
        "Unexpected current cell, should be '{}', found '{}'".format(str(Dots.line().cell(15)), str(Dots.line().cell())))
    self.assertEqual(str(Dots.line()), "15 ",\
        "Tried scrolling past the last cell in line: {}".format(str(Dots.line())))
    # Assert scrolling before the first cell actually scrolls to it
    Dots.scroll(Dots.line()).right( by=16 ).once()
    self.assertEqual(Dots.line().cell(), Dots.line().cell(0),\
        "Unexpected current cell, should be '{}', found '{}'".format(str(Dots.line().cell(0)), str(Dots.line().cell())))
    self.assertEqual(str(Dots.line()), "0  1  2  3  4  5",\
        "Tried scrolling before the first cell in line: {}".format(str(Dots.line())))


  def test_cell_scrolling(self):
    Dots.buffer().parse("abcdefghijklmnopqrstuvwxyz")
    # Assert cell contents before scrolling
    self.assertEqual(str(Dots.line().cell()), "abcdefghijklmnop",\
        "Malformed cell contents: {}".format(str(Dots.line().cell())))
    # Scroll cell to the left and assert cell contents scrolled
    Dots.scroll(Dots.line().cell()).left().once()
    self.assertEqual(str(Dots.line().cell()), "bcdefghijklmnopq",\
        "Performed scrolling left, but contents of cell did not scroll correctly: {}".format(str(Dots.line().cell())))
    # Assert scrolling past the last character in cell actually scrolls to it
    Dots.scroll(Dots.line().cell()).left( by=25 ).once()
    self.assertEqual(str(Dots.line().cell()), "klmnopqrstuvwxyz",\
        "Tried scrolling past the last character in cell: {}".format(str(Dots.line().cell())))
    # Assert scrolling before the first character in cell actually scrolls to it
    Dots.scroll(Dots.line().cell()).right( by=26 ).once()
    self.assertEqual(str(Dots.line().cell()), "abcdefghijklmnop",\
        "Tried scrolling before the first character in cell: {}".format(str(Dots.line().cell())))



if __name__ == "__main__":
  Dots.init()
  suite = unittest.TestLoader().loadTestsFromTestCase(SimpleTestCase)
  unittest.TextTestRunner(verbosity=2).run(suite)

