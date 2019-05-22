#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser combinators losely inspired by Haskell's monadic parsers.

The monad here is the result tuple (result, ParseState), which is returned
by all Parser's parse() method.
"""

class Parser:
    """Super class for all parsers. Implements operator overloading for easier
    chaining of parsers."""
    type = None

    def parse(self, st):
        """Call parse() on any class inheriting from this one. It will consume
        the ParseState st and return the parse result (depending on the parsers used).
        """
        return (None, st)

    def __add__(self, other):
        """Chain parsers, only match if all match in sequence."""
        return AtomicSequence(self, other)

    def __mul__(self, times):
        """Repeat a parser exactly `times`."""
        return StrictRepeat(self, times)

    def __rmul__(self, times):
        """Repeat a parser exactly `times`."""
        return self.__mul__(times)

    def __or__(self, other):
        """Chain parsers as alternatives (first-match)."""
        return FirstAlternative(self, other)

    def __rshift__(self, fn):
        """Transform the result of a parser using an unary function.

        Example:
            Regex('[a-z]+') >> (lambda s: s[0])

            consumes all lower case characters but results in only the first.

            Regex('\d+') >> int >> (lambda i: i*2)

            consume digits and convert them to an integer, multiplying it by two..
        """
        return _Transform(self, fn)

    def then(self, next):
        """Consume part of the input, discarding it, and return the result
        parsed by the supplied next parser."""
        return Last(AtomicSequence(self, next))

# Combinators

class _Transform(Parser):
    _inner = None
    _transform = lambda x: x

    def __init__(self, inner, tf):
        self._inner = inner
        self._transform = tf

    def parse(self, st):
        initial = st.index()
        r, st2 = self._inner.parse(st)
        if r is None:
            st.reset(initial)
            return None, st
        try:
            return self._transform(r), st2
        except Exception as e:
            st.reset(initial)
            raise Exception('{} (at {} (col {}))'.format(e, st, st.index()))

class _Sequence(Parser):
    _parsers = []
    _atomic = None

    def __init__(self, *parsers):
        self._parsers = parsers
        self._flatten()

    def _flatten(self):
        if len(self._parsers) == 0:
            return
        result = []
        for (i, p) in enumerate(self._parsers):
            if isinstance(p, type(self)):
                p._flatten()
                result.extend(p._parsers)
            else:
                result.append(p)
        self._parsers = result

    def parse(self, st):
        results = []
        initial = st.index()
        for p in self._parsers:
            before = st.index()
            result, st2 = p.parse(st)
            if result is None:
                if self._atomic:
                    st.reset(initial)
                    return None, st
                st.reset(before)
                break
            if result is not SKIP_MARKER:
                results.append(result)
            st = st2
        return results, st2


class AtomicSequence(_Sequence):
    """Execute a series of parsers after each other. All must succeed. Result
    is a merged list of results of the parsers.

    This means that if your parser returns a list and you want to not merge it with the results of other
    parsers in the repetition, you should wrap the list inside another list. E.g.:

    (List() >> (lambda l: [l])) + Skip(String("<separator>")) + (List() >> (lambda l: [l]))"""
    _atomic = True

class OptimisticSequence(_Sequence):
    """Execute a series of parsers after each other, as far as possible
    (until the first parser fails). Result is a merged list of results of the parsers.

    This means that if your parser returns a list and you want to not merge it with the results of other
    parsers in the repetition, you should wrap the list inside another list. E.g.:

    (List() >> (lambda l: [l])) + Skip(String("<separator>")) + (List() >> (lambda l: [l]))"""
    _atomic = False

class _Repeat(Parser):
    _parser = None
    _times = 0
    _strict = None

    def __init__(self, parser, repeat):
        self._parser = parser
        self._times = repeat

    def parse(self, st):
        results = []
        initial = st.index()
        i = 0

        while i < self._times or self._times < 0:
            r, st2 = self._parser.parse(st)
            if r == None:
                if self._strict:
                    st.reset(initial)
                    return None, st
                if len(results) == 0:
                    return SKIP_MARKER, st2
                return results, st2
            if r is not SKIP_MARKER:
                results.append(r)
            st = st2
            i += 1
        return results, st

class StrictRepeat(_Repeat):
    """Expect exactly `repeat` matches of a parser. Result is list of results of the parsers."""
    _strict = True

class Repeat(_Repeat):
    """Expect up to `repeat` matches of a parser. -1 means indefinitely many matches.
    Result is a merged list of results of the parsers."""
    _strict = False

def Maybe(p):
    return Repeat(p, 1)

class _Alternative(Parser):
    """Attempt a series of parsers and return the result of the first one matching."""
    _parsers = []
    _longest = None

    def __init__(self, *parsers):
        self._parsers = parsers

class FirstAlternative(_Alternative):
    """Attempt parsers until one matches. Result is result of that parser."""

    def parse(self, st):
        initial = st.index()
        for p in self._parsers:
            r, st2 = p.parse(st)
            if r is not None:
                return r, st2
            st.reset(initial)
        return None, st

class LongestAlternative(_Alternative):
    """Attempt all parsers and return the longest match. Result is result of best parser."""

    def parse(self, st):
        matches = []
        initial = st.index()
        for p in self._parsers:
            r, st2 = p.parse(st)
            if r is None:
                st.reset(initial)
                continue
            matches.append((st2.index() - initial, r))
            st = st2
            st.reset(initial)

        if len(matches) == 0:
            st.reset(initial)
            return None, st
        # Stable sort!
        matches.sort(key=lambda t: t[0])
        # Return first element that had longest match.
        matches.reverse()
        best = matches[0]
        for r in matches[1:]:
            if r[0] < best[0]:
                break
            best = r
        st.reset(initial + best[0])
        return best[1], st

# Some combinators can be implemented directly.

def Last(p):
    """Return the last result from the list of results of p. Result is scalar."""
    return p >> (lambda l: l[-1] if isinstance(l, list) else l)

SKIP_MARKER = []

def Skip(p):
    """Omit the result of parser p, and replace it with []. Result is []."""
    return p >> (lambda r: SKIP_MARKER)

def ConcatenateResults(p):
    """Concatenate string results into a single string. Result is string."""
    return p >> (lambda l: ''.join(l) if l and len(l) > 0 else None)

def Flatten(p):
    """Flatten the list result of a parser p (merge inner lists). Result is list."""
    def flatten(l):
        r = []
        if type(l) is not list:
            return l
        for e in l:
            if type(e) is list:
                r.extend(e)
            else:
                r.append(e)
        return r
    return p >> flatten