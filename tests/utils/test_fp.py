import unittest
from PyExpUtils.utils.fp import Maybe, memoize_method

class TestMaybe(unittest.TestCase):
    def test_map(self):
        boxed = 22
        def isEqual(v):
            self.assertEqual(v, boxed)

        def fail():
            self.fail()

        # some case
        maybe = Maybe.some(boxed)
        maybe.map(isEqual)

        # none case
        maybe = Maybe.none()
        maybe.map(fail)

    def test_orElse(self):
        boxed = 22

        # some case
        maybe = Maybe.some(boxed)
        got = maybe.orElse(boxed - 1)
        self.assertEqual(got, boxed)

        # none case
        maybe = Maybe.none()
        got = maybe.orElse(boxed - 1)
        self.assertEqual(got, boxed - 1)

    def test_insist(self):
        boxed = 22

        # some case
        maybe = Maybe.some(boxed)
        got = maybe.insist()
        self.assertEqual(got, boxed)

        # none case
        maybe = Maybe.none()
        with self.assertRaises(AssertionError):
            got = maybe.insist()

class RegressionTests(unittest.TestCase):
    def test_memoize(self):
        built = 0
        class Thing:
            def __init__(self):
                nonlocal built
                built += 1
                self.x = built

            @memoize_method
            def get(self):
                self.x += 1
                return self.x

        thing1 = Thing()
        self.assertEqual(thing1.get(), 2)
        self.assertEqual(thing1.get(), 2)

        thing2 = Thing()
        self.assertEqual(thing2.get(), 3)
