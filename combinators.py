#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 19 11:20:01 2019

@author: lbo
"""

import re

class ParseState:
    """Encapsulates state as the parser goes through input."""

    _input = ''
    _index = 0

    def __init__(self, s):
        self._input = s

    def __repr__(self):
        if self._index < len(self._input):
            return 'ParseState({}< {} >{})'.format(
                    self._input[0:self._index], self._input[self._index], self._input[self._index+1:])
        else:
            return 'ParseState({}<>)'.format(self._input)

    def next(self):
        current = self.peek()
        self._index += 1
        return current

    def peek(self):
        return self._input[self._index]

    def index(self):
        return self._index

    def reset(self, ix):
        self._index = ix

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def finished(self):
        return self._index == len(self._input)
    
    def remaining(self):
        if self.finished():
            return ''
        return self._input[self._index:]
    
    def sub(self, start, length):
        assert self._index+start < self._index+start+length <= len(self._input)
        return ParseState(self._input[self._index+start:self._index+start+length])

class Parser:
    type = None
    
    def parse(self, st):
        return (None, st)
    
    def __add__(self, other):
        return AtomicSequence(self, other)
    
# Combinators
        
class _Sequence(Parser):
    _parsers = []
    _atomic = None
    
    def __init__(self, *parsers):
        self._parsers = parsers
    
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
            if isinstance(result, list):
                results.extend(result)
            else:
                results.append(result)
            st = st2
        return results, st2
    
class AtomicSequence(_Sequence):
    """Execute a series of parsers after each other. All must succeed."""
    _atomic = True

class OptimisticSequence(_Sequence):
    """Execute a series of parsers after each other, as far as possible."""
    _atomic = False

class Alternative(Parser):
    """Attempt a series of parsers and return the result of the first one matching."""
    _parsers = []
    
    def __init__(self, *parsers):
        self._parsers = parsers
    
    def parse(self, st):
        initial = st.index()
        for p in self._parsers:
            r, st2 = p.parse(st)
            if r is not None:
                return r, st2
            st.reset(initial)
        return None, st

# Parsers
    
class String(Parser):
    _s = ''
    
    def __init__(self, s):
        self._s = s
    
    def parse(self, st):
        initial = st.index()
        s = self._s
        while len(s) > 0 and not st.finished() and s[0] == st.peek():
            st.next()
            s = s[1:]
        if len(s) == 0:
            return (self._s, st)
        st.reset(initial)
        return (None, st)

class Regex(Parser):
    """Parse a string using a regular expression. The result is either the
    string or a tuple with all matched groups."""
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
        if len(match.groups()) > 0:
            result = list(match.groups())
        st.reset(start+end)
        return result, st