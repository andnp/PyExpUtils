from PyExpUtils.utils.Collector import Collector, Window, Subsample
import unittest

class TestCollector(unittest.TestCase):
    def test_collect(self):
        collector = Collector()
        collector.setIdx(0)

        for i in range(10):
            collector.collect('data', i * 2)

        got = collector.get('data', 0)
        expected = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
        self.assertEqual(got, expected)

    def test_collectRuns(self):
        collector = Collector()

        for r in range(3):
            collector.setIdx(r)
            for i in range(5):
                collector.collect('data', (i + r) * 2)

        got = collector.get('data')
        expected = [
            [0, 2, 4, 6, 8],
            [2, 4, 6, 8, 10],
            [4, 6, 8, 10, 12],
        ]

        self.assertEqual(got, expected)

    def test_fillRest(self):
        collector = Collector()

        for r in range(2):
            collector.setIdx(r)
            for i in range(3):
                collector.collect('data', (i + r) * 2)

            collector.fillRest('data', 7)

        got = collector.get('data')
        expected = [
            [0, 2, 4, 4, 4, 4, 4],
            [2, 4, 6, 6, 6, 6, 6],
        ]

        self.assertEqual(got, expected)

    def test_concat(self):
        collector = Collector(idx=0)

        data1 = [1, 2, 3]
        data2 = [4, 5, 6]

        collector.concat('data', data1)
        collector.concat('data', data2)

        got = collector.get('data', 0)
        expected = [1, 2, 3, 4, 5, 6]

        self.assertEqual(got, expected)

    def test_evaluate(self):
        collector = Collector(idx=0)

        for i in range(5):
            ev = lambda: i
            collector.evaluate('data', ev)

        expected = [0, 1, 2, 3, 4]
        got = collector.get('data', 0)

        self.assertEqual(got, expected)

    def test_window(self):
        collector = Collector(
            config={
                'a': Window(3),
            },
            idx=0,
        )

        collector.collect('a', 0)
        collector.collect('a', 1)
        collector.collect('a', 5)
        collector.collect('a', 3)

        self.assertEqual(collector.get('a', 0), [2.0])

        collector.collect('a', 4)
        collector.collect('a', 5)

        self.assertEqual(collector.get('a', 0), [2.0, 4.0])

    def test_subsample(self):
        collector = Collector(
            config={
                'a': Subsample(3),
            },
            idx=0,
        )

        collector.collect('a', 0)
        collector.collect('a', 1)
        collector.collect('a', 2)

        self.assertEqual(collector.get('a', 0), [0])

        collector.collect('a', 3)

        self.assertEqual(collector.get('a', 0), [0, 3])

    def test_window_repeat(self):
        collector = Collector(
            config={
                'a': Window(9),
            },
            idx=0,
        )

        # nothing happens if below window size
        collector.repeat('a', 1, 4)
        self.assertEqual(collector.get('a', 0), [])

        collector.repeat('a', 2, 3)
        self.assertEqual(collector.get('a', 0), [])

        # adds one value if goes over window size
        collector.repeat('a', 4, 4)
        self.assertEqual(collector.get('a', 0), [2.0])

        # adds multiple values if much larger than window size
        collector.repeat('a', 4, 21)
        self.assertEqual(collector.get('a', 0), [2.0, 4.0, 4.0])

    def test_subsample_repeat(self):
        collector = Collector(
            config={
                'a': Subsample(9),
            },
            idx=0,
        )

        # only the first element is added
        collector.repeat('a', 1, 4)
        self.assertEqual(collector.get('a', 0), [1])

        collector.repeat('a', 2, 3)
        self.assertEqual(collector.get('a', 0), [1])

        # when over size, second element is added
        collector.repeat('a', 4, 4)
        self.assertEqual(collector.get('a', 0), [1, 4])

        # adds multiple values if much larger than window size
        collector.repeat('a', 6, 21)
        self.assertEqual(collector.get('a', 0), [1, 4, 6, 6])

    def test_downsample(self):
        collector = Collector(idx=0)

        for r in range(10):
            collector.setIdx(r)
            for idx in range(15):
                collector.collect('data', r * idx)

        # downsample to only 5 values in each run
        collector.downsample('data', num=5, method='window')

        for i in range(10):
            expected = [i * j for j in range(1, 15, 3)]
            got = collector.get('data', i)

            self.assertEqual(got, expected)
