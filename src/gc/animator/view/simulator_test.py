from simulator import Point
import unittest


"""
run using:

    python -m unittest view.simulator_test
"""


class TestPoint(unittest.TestCase):

    def test_translate_should_add(self):
        point = Point(0, 0, 0)
        point.translate(Point(1, 2, 3))
        self.assertEqual(point.x, 1)
        self.assertEqual(point.y, 2)
        self.assertEqual(point.z, 3)


if __name__ == '__main__':
    unittest.main()
