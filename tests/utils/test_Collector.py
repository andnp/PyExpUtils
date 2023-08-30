from PyExpUtils.collection.Collector import Collector
from PyExpUtils.collection.Sampler import Window, Subsample
import unittest

class TestCollector(unittest.TestCase):
    def test_collect(self):
        collector = Collector()
        collector.setIdx(0)

        for i in range(10):
            collector.collect('data', i * 2)
            collector.next_frame()

        got = collector.get('data', 0)
        expected = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
        self.assertEqual(got, expected)

    def test_evaluate(self):
        collector = Collector(idx=0)

        for i in range(5):
            ev = lambda: i
            collector.evaluate('data', ev)
            collector.next_frame()

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
        collector.next_frame()
        collector.collect('a', 1)
        collector.next_frame()
        collector.collect('a', 5)
        collector.next_frame()
        collector.collect('a', 3)
        collector.next_frame()

        self.assertEqual(collector.get('a', 0), [2.0])

        collector.collect('a', 4)
        collector.next_frame()
        collector.collect('a', 5)
        collector.next_frame()

        self.assertEqual(collector.get('a', 0), [2.0, 4.0])

    def test_subsample(self):
        collector = Collector(
            config={
                'a': Subsample(3),
            },
            idx=0,
        )

        collector.collect('a', 0)
        collector.next_frame()
        collector.collect('a', 1)
        collector.next_frame()
        collector.collect('a', 2)
        collector.next_frame()

        self.assertEqual(collector.get('a', 0), [0])

        collector.collect('a', 3)
        collector.next_frame()

        self.assertEqual(collector.get('a', 0), [0, 3])
