import unittest
import numpy as np
from PyExpUtils.results.voting import RankedCandidate, ScoredCandidate, buildBallot, condorcet, confidenceRanking, firstPastPost, instantRunoff, scoreRanking

def fakeElection1():
    return [
        buildBallot([
            # name, rank, score
            RankedCandidate(3, 0, 63),
            RankedCandidate(4, 1, 44),
            RankedCandidate(5, 2, 32),
            RankedCandidate(0, 2, 20),
            RankedCandidate(8, 3, np.nan),
        ]),
        buildBallot([
            RankedCandidate(4, 0, 63),
            RankedCandidate(5, 0, 59),
            RankedCandidate(0, 1, 20),
            RankedCandidate(3, 2, 18),
            RankedCandidate(8, 3, np.nan),
        ]),
        buildBallot([
            RankedCandidate(5, 0, 32),
            RankedCandidate(4, 1, 28),
            RankedCandidate(3, 2, 25),
            RankedCandidate(0, 2, 20),
            RankedCandidate(8, 3, np.nan),
        ]),
        buildBallot([
            RankedCandidate(0, 0, 66),
            RankedCandidate(3, 1, 34),
            RankedCandidate(4, 1, 33),
            RankedCandidate(5, 2, 32),
            RankedCandidate(8, 3, np.nan),
        ]),
    ]

def fakeElection2():
    return [
        buildBallot([
            RankedCandidate(3, 0, 63),
            RankedCandidate(4, 1, 44),
            RankedCandidate(5, 2, 32),
            RankedCandidate(0, 3, 20),
            RankedCandidate(8, 4, np.nan),
        ]),
        buildBallot([
            RankedCandidate(4, 0, 63),
            RankedCandidate(5, 0, 59),
            RankedCandidate(0, 1, 20),
            RankedCandidate(3, 2, 18),
            RankedCandidate(8, 3, np.nan),
        ]),
        buildBallot([
            RankedCandidate(5, 0, 32),
            RankedCandidate(4, 1, 28),
            RankedCandidate(3, 2, 25),
            RankedCandidate(0, 2, 20),
            RankedCandidate(8, 3, np.nan),
        ]),
        buildBallot([
            RankedCandidate(0, 0, 66),
            RankedCandidate(3, 1, 34),
            RankedCandidate(4, 1, 33),
            RankedCandidate(5, 2, 32),
            RankedCandidate(8, 3, np.nan),
        ]),
    ]

class TestVoting(unittest.TestCase):
    def test_confidenceRanking(self):
        scores = [
            ScoredCandidate(0, 20, 2),
            ScoredCandidate(3, 25, 1),
            ScoredCandidate(4, 63, 5),
            ScoredCandidate(5, 32, 8),
            ScoredCandidate(8, np.nan, np.nan),
        ]

        expected = [
            RankedCandidate(4, 0, 63),
            RankedCandidate(5, 1, 32),
            RankedCandidate(3, 1, 25),
            RankedCandidate(0, 2, 20),
        ]

        got = confidenceRanking(scores, stderrs=1, prefer='big')
        self.assertEqual(expected, got)

        expected = [
            RankedCandidate(0, 0, 20),
            RankedCandidate(3, 1, 25),
            RankedCandidate(5, 1, 32),
            RankedCandidate(4, 2, 63),
        ]

        got = confidenceRanking(scores, stderrs=1, prefer='small')
        self.assertEqual(expected, got)

    def test_scoreRanking(self):
        scores = [
            ScoredCandidate(0, 20, 2),
            ScoredCandidate(3, 25, 1),
            ScoredCandidate(4, 63, 5),
            ScoredCandidate(5, 32, 8),
            ScoredCandidate(8, np.nan, np.nan),
        ]

        expected = [
            RankedCandidate(4, 0, 63),
            RankedCandidate(5, 1, 32),
            RankedCandidate(3, 2, 25),
            RankedCandidate(0, 3, 20),
        ]

        got = scoreRanking(scores, prefer='big')
        self.assertEqual(expected, got)

    def test_instantRunoff(self):
        ballots = fakeElection1()
        winner = instantRunoff(ballots)
        self.assertEqual(winner, 4)

        ballots = fakeElection2()
        winner = instantRunoff(ballots)
        self.assertEqual(winner, 3)

    def test_firstPastPost(self):
        ballots = fakeElection1()
        winner = firstPastPost(ballots)
        self.assertEqual(winner, 5)

        ballots = fakeElection2()
        winner = firstPastPost(ballots)
        self.assertEqual(winner, 5)

    def test_condorcet(self):
        ballots = fakeElection1()
        winner = condorcet(ballots)
        self.assertEqual(winner, 4)

        ballots = fakeElection2()
        winner = condorcet(ballots)
        self.assertEqual(winner, 4)
