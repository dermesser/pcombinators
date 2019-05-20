#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 19 21:15:30 2019

@author: lbo
"""

import re

from pcombinators.combinators import (
        Parser,
        ConcatenateResults,
        OptimisticSequence,
        Maybe,
        Last,
        Repeat,
        Skip)

# Parsers

class String(Parser):
    """Consume a fixed string. Result is the string."""
    _s = ''

    def __init__(self, s):
        self._s = s

    def parse(self, st):
        initial = st.index()
        s = self._s
        i = 0
        while i < len(s) and not st.finished() and s[i] == st.peek():
            st.next()
            i += 1
        if i == len(s):
            return (self._s, st)
        st.reset(initial)
        return (None, st)

class OneOf(Parser):
    """Parse characters in the given set. Result is string or None, if none were parsed."""
    _set = None

    def __init__(self, s):
        """
        Example:
            CharSet('abcd')
            CharSet('0123456789')
        """
        self._set = set(s)

    def parse(self, st):
        if not st.finished() and st.peek() in self._set:
            return st.next(), st
        else:
            return None, st

class Regex(Parser):
    """Parse a string using a regular expression. The result is either the
    string or a tuple with all matched groups. Result is string."""
    _rx = None

    def __init__(self, rx):
        if not isinstance(rx, re.Pattern):
            rx = re.compile(rx)
        self._rx = rx

    def parse(self, st):
        start = st.index()
        match = re.match(self._rx, st.remaining())
        if match is None:
            return None, st
        begin, end = match.span()
        result = match.group(0)
        if len(match.groups()) > 1:
            result = list(match.groups())
        elif len(match.groups()) > 0:
            result = match.group(1)
        st.reset(start+end)
        return result, st

def Nothing():
    """Matches the empty string, and always succeeds."""
    return String('')

def CharSet(s):
    """Matches arbitrarily many characters from the set s (which can be a string).
    Result is string."""
    return ConcatenateResults(Repeat(OneOf(s), -1))

# See section below for optimized versions of the following parsers.

def CanonicalInteger():
    """Return a parser that parses integers and results in an integer. Result is int."""
    return Last(Whitespace() + (ConcatenateResults(Maybe(String('-')) + CharSet('0123456789')) >> int))

def CanonicalFloat():
    """Return a parser that parses floats and results in floats. Result is float."""
    def c(l):
        """Convert parts of a number into a float."""
        if l and len(l) > 0:
            return float(''.join(l))
        return None
    number = OptimisticSequence(
            Repeat(OneOf('-'), 1) + CharSet('0123456789'),
            Repeat(OneOf('.'), 1) + CharSet('0123456789'))
    return (Skip(Whitespace()) + number) >> c

def NonEmptyString():
    """Return a parser that parses a string until the first whitespace,
    skipping whitespace before. Result is string."""
    return Last(Whitespace() + Regex('\w+'))

def Whitespace():
    """Parse whitespace (space, newline, tab). Result is string."""
    return CharSet(' \n\r\t') | Nothing()

# Optimized parsers

class Float():
    """Parses a float like [-]ddd[.ddd].

    Float parses floats with more manual code, making it up to 40% faster than
    CanonicalFloat."""
    _digits = CharSet('0123456789')

    def parse(self, st):
        initial = st.index()
        multiplier = 1
        minus, st = String('-').parse(st)
        if minus is not None:
            multiplier = -1
        big, st = self._digits.parse(st)
        if big is None:
            st.reset(initial)
            return None, st
        small = ''
        dot, st = String('.').parse(st)
        if dot is not None:
            small, st = self._digits.parse(st)
            if small is not None:
                return float(big + '.' + small) * multiplier, st
        return float(big) * multiplier, st

class Integer():
    """Parser for integers of form [-]dddd[...]. Result is int.

    This parser is up to twice as fast as CanonicalInteger and thus implemented
    manually."""
    _digits = CharSet('0123456789')

    def parse(self, st):
        initial = st.index()
        multiplier = 1
        minus, st = String('-').parse(st)
        if minus is not None:
            multiplier = -1
        digits, st = self._digits.parse(st)
        if digits is not None:
            return int(digits)*multiplier, st
        st.reset(initial)
        return None, st