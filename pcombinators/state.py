#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 21:41:32 2019

@author: lbo
"""

import io

def ps(s):
    return ParseState(s)

class _State:
    """Generic parsing state representation."""

    _holds = [] # List of indices that are still marked as needed. Ascending

    def next(self):
        pass

    def peek(self):
        raise NotImplementedError()

    def index(self):
        raise NotImplementedError()

    def len(self):
        raise NotImplementedError()

    # Holds are a simple garbage collection mechanism by which parsers should
    # indicate which parts of state they may still backtrack to.
    class ParserHold:
        def __init__(self, i):
            self.total_index = i
        total_index = 0

    def _maybe_collect(self):
        pass

    def hold(self):
        self._holds.append(self.index())
        return self.ParserHold(self.index())

    def release(self, hold):
        self._holds.pop(hold.total_index)
        self._maybe_collect()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def finished(self):
        return self.index() == self.len()

    def remaining(self):
        raise NotImplementedError()

    class ParseException(Exception):
        pass

    def error(self, msg):
        raise ParseException(msg)

    def reset(self):
        raise NotImplementedError('use holds!')

class ParseFileState(_State):
    """A lazy parsing state implementation, reading from stream."""
    _fobj = None
    _buf = [] # List of characters.

    _index = 0 # Index in current _buf
    _total_offset = 0 # Index of first _buf entry in stream since start

    def __init__(self, f):
        if type(f) is str:
            self._fobj = open(f, 'r')
        elif isinstance(f, io.IOBase):
            self._fobj = f
        else:
            raise NotImplementedError('unknown input source {}'.format(f))

    def __del__(self):
        if self._fobj:
            self._fobj.close()
    def _maybe_collect(self):
        # No holds left, forget everything up to now.
        if len(self._holds) == 0:
            self._buf = self._buf[self._index:]
        else: # Find oldest hold and update buffer.
            assert sorted(self._holds) == self._holds
            to_clean = self._holds[0]-self._total_offset
            self._buf = self._buf[:to_clean]
            self._total_offset += to_clean
            self._index -= to_clean
            self._holds.pop(0)

    def index(self):
        return self._total_offset + self._index

    PREFILL = 256

    def fill_buffer(self, min=0):
        if len(self._buf)-self._index <= min:
            self._buf.extend(self._fobj.read(self.PREFILL))

    def peek(self):
        self.fill_buffer()
        return self._buf[self._index]

    def next(self):
        self.fill_buffer()
        self._index += 1
        return self._buf[self._index-1]

    def remaining(self):
        print('warning: remaining() on ParseFileState is only accurate to up to {} characters lookahead and expensive'.format(self.PREFIL))
        self.fill_buffer(self.PREFILL)
        return self._buf[self._index:]

    def len(self):
        print('warning: len() is inaccurate on ParseFileState, returning only past and present state')
        return self._total_offset + len(self._buf)

class ParseState(_State):
    """Encapsulates state as the parser goes through input supplied as string."""

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

    def len(self):
        return len(self._input)

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
