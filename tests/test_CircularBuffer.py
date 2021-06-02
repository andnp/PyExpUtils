import unittest
import numpy as np
from PyExpUtils.CircularBuffer import CircularBuffer

class TestCircularBuffer(unittest.TestCase):
    def test_buffer(self):
        np.random.seed(0)
        buffer = CircularBuffer[float](buffer_size=4)

        buffer.add(1)
        x = buffer.sample(1)
        self.assertEqual(x, [1])

        buffer.add(2)
        x = buffer.sample(2)
        self.assertEqual(x, [2, 1])

        buffer.add(3)
        buffer.add(4)
        self.assertEqual(len(buffer), 4)

        x = buffer.sample(3)
        self.assertEqual(x, [3, 1, 2])

        buffer.add(5)
        self.assertEqual(len(buffer), 4)

        x = buffer.sample(4)
        self.assertEqual(x, [5, 3, 2, 4])

        # spam the crap out of it
        for i in range(100000):
            buffer.add(i)

        x = buffer.sample(3)
        self.assertEqual(x, [99998, 99999, 99997])
