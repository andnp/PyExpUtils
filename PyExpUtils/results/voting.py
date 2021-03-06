from PyExpUtils.utils.dict import pick
from copy import deepcopy
import numpy as np
from PyExpUtils.models.ExperimentDescription import ExperimentDescription
from PyExpUtils.results.results import ResultList, Reducer, whereParametersEqual
from PyExpUtils.utils.types import T
from typing import Dict, List, NamedTuple, Tuple, Union

Name = Union[int, str]

class ScoredCandidate(NamedTuple):
    # meta-parameter permutation index for experiment description
    name: Name
    # the "score" of this meta-parameter
    score: float
    # the stderr of the point value
    stderr: float

class RankedCandidate(NamedTuple):
    name: Name
    rank: int
    score: float = 0

def scoreMetaparameters(results: ResultList, exp: ExperimentDescription, reducer: Reducer = np.mean):
    # gotta cache the results
    all_results = list(results)

    all_scores: List[ScoredCandidate] = []
    for i in range(exp.numPermutations()):
        params = pick(exp.getPermutation(i), exp.getKeys())
        results = whereParametersEqual(all_results, params)
        results = list(results)

        # if data is missing, then mark the score as nan
        # different ranking methods might handle these nans differently so defer to them
        if len(results) == 0:
            all_scores.append(ScoredCandidate(i, np.nan, np.nan))
            continue

        # there should only be one result
        r = results[0]

        point = reducer(r.mean())
        stderr = reducer(r.stderr())

        all_scores.append(ScoredCandidate(i, point, stderr))

    return all_scores

def confidenceInterval(scored: ScoredCandidate, c: float):
    lo = scored.score - c * scored.stderr
    hi = scored.score + c * scored.stderr

    return (lo, hi)

def inRange(a: Tuple[float, float], b: Tuple[float, float]):
    if a[0] <= b[1] and a[0] >= b[0]:
        return True

    if a[1] <= b[1] and a[1] >= b[0]:
        return True

    return False

def confidenceRanking(scores: List[ScoredCandidate], stderrs: float = 2.0, prefer: str = 'big'):
    if prefer == 'big':
        ordered = sorted(scores, key=lambda x: x.score, reverse=True)
    else:
        ordered = sorted(scores, key=lambda x: x.score, reverse=False)

    rank = 0
    last_range = confidenceInterval(ordered[0], stderrs)

    ranks: List[RankedCandidate] = []
    for score in ordered:
        rang = confidenceInterval(score, stderrs)
        if not inRange(rang, last_range):
            rank += 1
            last_range = rang

        ranks.append(RankedCandidate(score.name, rank, score.score))

    return ranks

def scoreRanking(scores: List[ScoredCandidate], prefer: str = 'big'):
    if prefer == 'big':
        ordered = sorted(scores, key=lambda x: x.score, reverse=True)
    else:
        ordered = sorted(scores, key=lambda x: x.score, reverse=False)

    rank = 0
    ranks: List[RankedCandidate] = []
    for score in ordered:
        ranks.append(RankedCandidate(score.name, rank, score.score))
        rank += 1

    return ranks

RankedBallot = Dict[Name, RankedCandidate]
def buildBallot(candidates: List[RankedCandidate]) -> RankedBallot:
    ballot: RankedBallot = {}
    for candidate in candidates:
        ballot[candidate.name] = candidate

    return ballot

def countVotes(ballots: List[RankedBallot]):
    votes: Dict[Name, int] = {}

    for ballot in ballots:
        for name in ballot:
            v = votes.get(name, 0)

            if ballot[name].rank == 0:
                v += 1

            votes[name] = v

    return votes

def firstPastPost(ballots: List[RankedBallot]) -> Name:
    votes = countVotes(ballots)

    vals = list(votes.values())
    ma: int = np.max(vals)

    return findKey(votes, ma)

def instantRunoff(ballots: List[RankedBallot]) -> Name:
    # the code is simpler if we modify in place
    # so create a copy so that we don't mess with the sender's object
    ballots = deepcopy(ballots)

    votes = countVotes(ballots)

    # check if we have a majority leader
    vals = list(votes.values())
    ma: int = np.max(vals)

    # if we have a majority leader, return that candidate
    if ma > np.ceil(len(ballots) / 2):
        return findKey(votes, ma)

    # if everyone is equal, then we have a tie.
    # in this case, return the first candidate
    if np.sum(vals == ma) == len(vals):
        return findKey(votes, ma)

    # otherwise, redistribute the ballots from the last place candidate
    mi: int = np.min(vals)

    # if there's only one loser, this is easy
    if np.sum(vals == mi) == 1:
        loser = findKey(votes, mi)

    # otherwise, let's grab the lowest total ranked candidate among the losers
    else:
        mi_votes: Dict[Name, int] = {}
        for name in findAllKeys(votes, mi):
            s = 0
            for ballot in ballots:
                s += ballot[name].rank

            mi_votes[name] = s

        mi_vals = list(mi_votes.values())
        max_val: int = np.max(mi_vals)  # highest rank here means worst candidate

        # technically there can again be a tie, but at this point we can safely
        # ignore that and break the tie arbitrarily
        loser = findKey(mi_votes, max_val)

    # now remove the loser from all ballots
    for ballot in ballots:
        # if this ballot voted for the loser *and* there are no other rank 0 votes
        # then bump all ranks up one
        if ballot[loser].rank == 0 and len(getCandidatesByRank(ballot, 0)) == 1:
            for name in ballot:
                ballot[name] = RankedCandidate(name, np.max((0, ballot[name].rank - 1)), ballot[name].score)

        del ballot[loser]

    # run the vote again with the modified ballots
    return instantRunoff(ballots)

def condorcet(ballots: List[RankedBallot]) -> Name:
    # the code is simpler if we modify in place
    # so create a copy so that we don't mess with the sender's object
    ballots = deepcopy(ballots)

    names = list(ballots[0].keys())
    n = len(names)

    vote_matrices = np.zeros((len(ballots), n, n))
    for i, ballot in enumerate(ballots):
        for j, a in enumerate(names):
            for k, b in enumerate(names):
                # candidates can't compete with themselves
                if a == b:
                    continue

                if ballot[a].rank > ballot[b].rank:
                    vote_matrices[i, k, j] = 1

                elif ballot[b].rank > ballot[a].rank:
                    vote_matrices[i, j, k] = 1

    sum_matrix = vote_matrices.sum(axis=0)
    totals = sum_matrix + sum_matrix.T
    wins = np.sum((sum_matrix - (totals / 2)) > 0, axis=1)
    ma: int = np.max(wins)

    # if we have a condorcet winner, then return them
    # they win if they won against everyone except themselves
    if ma == n - 1:
        idx = np.argmax(wins)
        return names[int(idx)]

    # otherwise, delete the worst candidate and try again
    idx = np.argmin(wins)

    loser = names[int(idx)]
    for ballot in ballots:
        del ballot[loser]

    return condorcet(ballots)

# ---------------------
# Local utility methods
# ---------------------
def getCandidatesByRank(ballot: RankedBallot, rank: int):
    out: List[RankedCandidate] = []

    for name in ballot:
        if ballot[name].rank == rank:
            out.append(ballot[name])

    return out

def findKey(obj: Dict[Name, T], val: T) -> Name:
    for key in obj:
        if obj[key] == val:
            return key

    raise Exception('uh-oh')

def findAllKeys(obj: Dict[Name, T], val: T) -> List[Name]:
    ret: List[Name] = []
    for key in obj:
        if obj[key] == val:
            ret.append(key)

    return ret
