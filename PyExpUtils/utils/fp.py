import functools

def memoize(f, cache={}):
    def cacheKey(*args, **kwargs):
        s = ''
        for arg in args:
            s = s + '__' + str(arg)
        for arg in kwargs:
            s = s + '__' + str(arg) + '-' + str(kwargs[arg])
        return s

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        nonlocal cache
        nonlocal cacheKey
        key = cacheKey(*args, **kwargs)
        if key in cache:
            return cache[key]
        ret = f(*args, **kwargs)
        cache[key] = ret
        return ret

    return wrapped

class memoize_method:
    def __init__(self, f):
        self.func = f

    def __call__(self, *args, **kwargs):
        # get the "self" argument from the class method
        obj = args[0]

        name = self.func.__name__

        try:
            cache = obj.__memoized_funcs
        except:
            cache = obj.__memoized_funcs = {}

        try:
            f = cache[name]
        except:
            f = cache[name] = memoize(self.func)

        return f(*args, **kwargs)

    def __get__(self, instance, owner):
        return functools.partial(self.__call__, instance)

def once(f):
    called = False
    ret = None
    def wrapped(*args, **kwargs):
        nonlocal called
        nonlocal ret
        if not called:
            ret = f(*args, **kwargs)
            called = True

        return ret

    return wrapped

class Maybe:
    def __init__(self, v):
        self._v = v

    @staticmethod
    def none():
        return Maybe(None)

    @staticmethod
    def some(v):
        return Maybe(v)

    def empty(self):
        return self._v is None

    def map(self, f):
        if self.empty():
            return self

        v = f(self._v)
        return Maybe.some(v)

    def flatMap(self, f):
        if self.empty():
            return self

        return f(self._v)

    def match(self, d):
        if self.empty() and 'none' in d:
            v = d['none']()
            return Maybe.some(v)

        elif not self.empty() and 'some' in d:
            v = d['some'](self._v)
            return Maybe.some(v)

        return self

    def orElse(self, v):
        if self.empty():
            return v

        return self._v

    def insist(self):
        if self.empty():
            raise AssertionError('Expected Maybe to be non-empty')

        return self._v
