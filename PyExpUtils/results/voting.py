from PyExpUtils.utils.dict import pick
from copy import deepcopy
import numpy as np
from PyExpUtils.models.ExperimentDescription import ExperimentDescription
from PyExpUtils.results.results import ResultList, Reducer, whereParametersEqual
from PyExpUtils.utils.types import T
from PyExpUtils.utils.jit import try2jit
from typing import Dict, List, NamedTuple, Tuple, Union, cast

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

def scoreMetaparameters(results: ResultList, exp: ExperimentDescription, reducer: Reducer = lambda x: float(np.mean(x))):
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

def filterNans(scores: List[ScoredCandidate]):
    return list(filter(lambda s: not np.isnan(s.score), scores))

def confidenceRanking(scores: List[ScoredCandidate], stderrs: float = 2.0, prefer: str = 'big'):
    # this method just ignores null results
    scores = filterNans(scores)

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
    # this method just ignores null results
    scores = filterNans(scores)

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

def highScore(ballots: List[RankedBallot], prefer: str = 'big') -> Name:
    names = list(ballots[0].keys())

    scores = np.zeros(len(names))

    for i, name in enumerate(names):
        for ballot in ballots:
            scores[i] += ballot[name].score

    if prefer == 'big':
        idx = np.argmax(scores)
    else:
        idx = np.argmin(scores)

    # numpy types are getting worse
    i = cast(int, idx)

    return names[i]

def firstPastPost(ballots: List[RankedBallot]) -> Name:
    votes = countVotes(ballots)

    return dictMax(votes)[1]

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
                ballot[name] = RankedCandidate(name, max(0, ballot[name].rank - 1), ballot[name].score)

        del ballot[loser]

    # run the vote again with the modified ballots
    return instantRunoff(ballots)

@try2jit
def computeVoteMatrix(ranks: np.ndarray):
    n = len(ranks)
    matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i == j:
                continue

            # a loses to b
            if ranks[i] > ranks[j]:
                matrix[j, i] = 1

            # b loses to a
            elif ranks[j] > ranks[i]:
                matrix[i, j] = 1

    return matrix

@try2jit
def copelandScore(sum_matrix: np.ndarray):
    scores = np.zeros(sum_matrix.shape[0])

    for i in range(len(scores)):
        for j in range(len(scores)):
            if i == j:
                continue

            if sum_matrix[i, j] > sum_matrix[j, i]:
                scores[i] += 1

            elif sum_matrix[i, j] == sum_matrix[j, i]:
                scores[i] += 0.5

    return scores

def sumMatrix(ballots: List[RankedBallot], names: List[Name]) -> np.ndarray:
    n = len(names)

    sum_matrix = np.zeros((n, n))
    for ballot in ballots:
        # ensure we pass ranks in order *by name*
        ranks = np.array([ballot[name].rank for name in names])
        sum_matrix += computeVoteMatrix(ranks)

    return sum_matrix

def small(ballots: List[RankedBallot], prefer: str = 'big') -> Name:
    # the code is simpler if we modify in place
    # so create a copy so that we don't mess with the sender's object
    ballots = deepcopy(ballots)

    # order is arbitrary, but *must* be consistent
    names = list(ballots[0].keys())
    sum_matrix = sumMatrix(ballots, names)
    copeland_scores = copelandScore(sum_matrix)

    winners = argsMax(copeland_scores)
    winner_names = [names[idx] for idx in winners]

    # if we have a singular winner, we are done
    if len(winners) == 1:
        return winner_names[0]

    # we could end up with a tie, which needs to broken arbitrarily
    # we pick the highest (by default) score
    rest = [name for name in names if name not in winner_names]

    # there was a tie which could not be resolved
    if len(rest) == 0:
        return highScore(ballots, prefer=prefer)

    # otherwise, iterate over all of the worst performers and delete them
    # then try again
    for loser in rest:
        for ballot in ballots:
            del ballot[loser]

    return small(ballots)

def raynaud(ballots: List[RankedBallot]) -> Name:
    ballots = deepcopy(ballots)

    names = list(ballots[0].keys())

    if len(names) == 1:
        return names[0]

    sum_matrix = sumMatrix(ballots, names)

    ma = np.max(sum_matrix)
    _, col = np.where(sum_matrix == ma)

    loser = names[col[0]]
    for ballot in ballots:
        del ballot[loser]

    return raynaud(ballots)

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

def dictMax(d: Dict[Name, int]):
    vals = list(d.values())
    ma: int = np.max(vals)

    amax = findKey(d, ma)

    return ma, amax

def argsMax(arr: np.ndarray):
    ties: List[int] = []
    ma: float = -np.inf

    for i, a in enumerate(arr):
        if a > ma:
            ties = [i]
            ma = a
        elif a == ma:
            ties.append(i)

    return ties
