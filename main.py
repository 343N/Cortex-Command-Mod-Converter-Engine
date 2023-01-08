from test.test_reader import TestReader
import unittest
import sys



if __name__ == "__main__":
    if ("test" in sys.argv):
        unittest.TextTestRunner().run(unittest.defaultTestLoader.discover('test'))