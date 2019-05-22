#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 21:41:32 2019

@author: lbo
"""

def ps(s):
    return ParseState(s)

class ParseState:
    """Encapsulates state as the parser goes through input."""

    _input = ''
    _index = 0

    def __init__(self, s):
        """Create a ParseState object from str s, representing the input to be parsed."""
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

    class ParseException(Exception):
        pass

    def error(self, msg):
        raise ParseException(msg)
