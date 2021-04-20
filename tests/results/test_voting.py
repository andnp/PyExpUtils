from typing import List, Tuple
import unittest
import numpy as np
import copy
from PyExpUtils.results.voting import RankedBallot, RankedCandidate, ScoredCandidate, buildBallot, raynaud, small, confidenceRanking, firstPastPost, instantRunoff, scoreRanking

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
            RankedCandidate(4, 2, 33),
            RankedCandidate(5, 2, 32),
            RankedCandidate(8, 3, np.nan),
        ]),
    ]

def buildByProportion(ballotPairs: List[Tuple[float, RankedBallot]], total: int):
    ballots: List[RankedBallot] = []

    for pair in ballotPairs:
        proportion, ballot = pair

        num = int(proportion * total)
        for _ in range(num):
            ballots.append(copy.deepcopy(ballot))

    return ballots

# taken from http://www.cs.angelo.edu/~rlegrand/rbvote/desc.html
def fakeElection3():
    return buildByProportion([

        (0.098, buildBallot([
            RankedCandidate('Abby', 0),
            RankedCandidate('Cora', 1),
            RankedCandidate('Erin', 2),
            RankedCandidate('Dave', 3),
            RankedCandidate('Brad', 4),
        ])),
        (0.064, buildBallot([
            RankedCandidate('Brad', 0),
            RankedCandidate('Abby', 1),
            RankedCandidate('Erin', 2),
            RankedCandidate('Cora', 3),
            RankedCandidate('Dave', 4),
        ])),
        (0.012, buildBallot([
            RankedCandidate('Brad', 0),
            RankedCandidate('Abby', 1),
            RankedCandidate('Erin', 2),
            RankedCandidate('Dave', 3),
            RankedCandidate('Cora', 4),
        ])),
        (0.098, buildBallot([
            RankedCandidate('Brad', 0),
            RankedCandidate('Erin', 1),
            RankedCandidate('Abby', 2),
            RankedCandidate('Cora', 3),
            RankedCandidate('Dave', 4),
        ])),
        (0.013, buildBallot([
            RankedCandidate('Brad', 0),
            RankedCandidate('Erin', 1),
            RankedCandidate('Abby', 2),
            RankedCandidate('Dave', 3),
            RankedCandidate('Cora', 4),
        ])),
        (0.125, buildBallot([
            RankedCandidate('Brad', 0),
            RankedCandidate('Erin', 1),
            RankedCandidate('Dave', 2),
            RankedCandidate('Abby', 3),
            RankedCandidate('Cora', 4),
        ])),
        (0.124, buildBallot([
            RankedCandidate('Cora', 0),
            RankedCandidate('Abby', 1),
            RankedCandidate('Erin', 2),
            RankedCandidate('Dave', 3),
            RankedCandidate('Brad', 4),
        ])),
        (0.076, buildBallot([
            RankedCandidate('Cora', 0),
            RankedCandidate('Erin', 1),
            RankedCandidate('Abby', 2),
            RankedCandidate('Dave', 3),
            RankedCandidate('Brad', 4),
        ])),
        (0.021, buildBallot([
            RankedCandidate('Dave', 0),
            RankedCandidate('Abby', 1),
            RankedCandidate('Brad', 2),
            RankedCandidate('Erin', 3),
            RankedCandidate('Cora', 4),
        ])),
        (0.030, buildBallot([
            RankedCandidate('Dave', 0),
            RankedCandidate('Brad', 1),
            RankedCandidate('Abby', 2),
            RankedCandidate('Erin', 3),
            RankedCandidate('Cora', 4),
        ])),
        (0.098, buildBallot([
            RankedCandidate('Dave', 0),
            RankedCandidate('Brad', 1),
            RankedCandidate('Erin', 2),
            RankedCandidate('Cora', 3),
            RankedCandidate('Abby', 4),
        ])),
        (0.139, buildBallot([
            RankedCandidate('Dave', 0),
            RankedCandidate('Cora', 1),
            RankedCandidate('Abby', 2),
            RankedCandidate('Brad', 3),
            RankedCandidate('Erin', 4),
        ])),
        (0.023, buildBallot([
            RankedCandidate('Dave', 0),
            RankedCandidate('Cora', 1),
            RankedCandidate('Brad', 2),
            RankedCandidate('Abby', 3),
            RankedCandidate('Erin', 4),
        ])),

    ], 1000)

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

        ballots = fakeElection3()
        winner = instantRunoff(ballots)
        self.assertEqual(winner, 'Brad')

    def test_firstPastPost(self):
        ballots = fakeElection1()
        winner = firstPastPost(ballots)
        self.assertEqual(winner, 5)

        ballots = fakeElection2()
        winner = firstPastPost(ballots)
        self.assertEqual(winner, 5)

        ballots = fakeElection3()
        winner = firstPastPost(ballots)
        self.assertEqual(winner, 'Brad')

    def test_small(self):
        ballots = fakeElection1()
        winner = small(ballots)
        self.assertEqual(winner, 4)

        ballots = fakeElection2()
        winner = small(ballots)
        self.assertEqual(winner, 4)

        ballots = fakeElection3()
        winner = small(ballots)
        self.assertEqual(winner, 'Brad')

    def test_raynaud(self):
        ballots = fakeElection1()
        winner = raynaud(ballots)
        self.assertEqual(winner, 4)

        ballots = fakeElection2()
        winner = raynaud(ballots)
        self.assertEqual(winner, 3)

        ballots = fakeElection3()
        winner = raynaud(ballots)
        self.assertEqual(winner, 'Abby')
