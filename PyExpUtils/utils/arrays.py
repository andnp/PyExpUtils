from itertools import tee, filterfalse

def fillRest(arr, val, length):
    for i in range(len(arr), length):
        arr.append(val)

    return arr

def first(listOrGen):
    if type(listOrGen) == list:
        return listOrGen[0]

    return next(listOrGen)

def last(l):
    return l[len(l) - 1]

def partition(gen, pred):
    t1, t2 = tee(gen)

    return filter(pred, t2), filterfalse(pred, t1)
