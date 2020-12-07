from PyExpUtils.utils.Collector import Collector
import unittest
import numpy as np

class TestCollector(unittest.TestCase):
    def test_collect(self):
        collector = Collector()

        for i in range(10):
            collector.collect('data', i * 2)

        got = collector.run_data['data']
        expected = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
        self.assertEqual(got, expected)

    def test_collectRuns(self):
        collector = Collector()

        for r in range(3):
            for i in range(5):
                collector.collect('data', (i + r) * 2)

            collector.reset()

        got = collector.all_data['data']
        expected = [
            [0, 2, 4, 6, 8],
            [2, 4, 6, 8, 10],
            [4, 6, 8, 10, 12],
        ]

        self.assertEqual(got, expected)

    def test_getStats(self):
        collector = Collector()

        for r in range(3):
            for i in range(5):
                collector.collect('data', (i + r) * 2)

            collector.reset()

        got = collector.getStats('data')
        expected = (
            np.array([ 2.,  4.,  6.,  8., 10.]),
            np.array([1.15470054, 1.15470054, 1.15470054, 1.15470054, 1.15470054]),
            3,
        )

        self.assertEqual(type(got), tuple)

        self.assertTrue(np.allclose(got[0], expected[0]))
        self.assertTrue(np.allclose(got[1], expected[1]))
        self.assertTrue(got[2] == expected[2])

    def test_fillRest(self):
        collector = Collector()

        for r in range(2):
            for i in range(3):
                collector.collect('data', (i + r) * 2)

            collector.fillRest('data', 7)
            collector.reset()


        got = collector.all_data['data']
        expected = [
            [0, 2, 4, 4, 4, 4, 4],
            [2, 4, 6, 6, 6, 6, 6],
        ]

        self.assertEqual(got, expected)

    def test_setSampleRate(self):
        collector = Collector()

        collector.setSampleRate('data', 3)

        for i in range(14):
            collector.collect('data', i)

        got = collector.run_data['data']
        expected = [0, 3, 6, 9, 12]

        self.assertEqual(got, expected)

    def test_concat(self):
        collector = Collector()

        data1 = [1, 2, 3]
        data2 = [4, 5, 6]

        collector.concat('data', data1)
        collector.concat('data', data2)

        got = collector.run_data['data']
        expected = [1, 2, 3, 4, 5, 6]

        self.assertEqual(got, expected)

        collector = Collector()
        collector.setSampleRate('data', 3)

        collector.concat('data', data1)
        collector.concat('data', data2)

        got = collector.run_data['data']
        expected = [1, 4]

        self.assertEqual(got, expected)

    def test_evaluate(self):
        collector = Collector()

        for i in range(5):
            ev = lambda: i
            collector.evaluate('data', ev)

        expected = [0, 1, 2, 3, 4]
        got = collector.run_data['data']

        self.assertEqual(got, expected)

        collector = Collector()
        collector.setSampleRate('data', 2)

        for i in range(7):
            ev = lambda: i + 1
            collector.evaluate('data', ev)

        expected = [1, 3, 5, 7]
        got = collector.run_data['data']

        self.assertEqual(got, expected)
