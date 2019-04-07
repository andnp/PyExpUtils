import unittest
from PyExpUtils.utils.fp import Maybe

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
