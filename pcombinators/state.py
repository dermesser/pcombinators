#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 21:41:32 2019

@author: lbo
"""

import io

def ps(s):
    """Wrap a string in a ParseState, making it suitable for parsing."""
    return ParseState(s)

class _State:
    """Generic parsing state representation."""

    def next(self):
        pass

    def advance(self, n):
        for i in range(0, n):
            self.next()

    def peek(self):
        raise NotImplementedError()

    def index(self):
        raise NotImplementedError()

    def len(self):
        raise NotImplementedError()

    # Holds are a simple garbage collection mechanism by which parsers should
    # indicate which parts of state they may still backtrack to.
    class ParserHold:
        pass

    def _maybe_collect(self):
        pass

    # Generic hold implementation based on hooks in base classes
    # (_maybe_collect(), _reset_index())

    def hold(self):
        self._holds.append(self.index())
        hold = _State.ParserHold()
        hold.total_index = self.index()
        return hold

    def release(self, hold):
        """Release a hold. Generally called when a parser was successful."""
        assert hold.total_index >= 0, 'BUG: double reset/release'
        assert self._holds[-1] == hold.total_index, 'BUG: releasing bad ordered hold'
        self._holds.pop()
        self._maybe_collect()
        hold.total_index = -1

    def reset(self, hold):
        """Release hold and reset index to its position."""
        # Reset is only allowed when this hold is the latest hold or later.
        # It is possible that a caller accidentally released a hold that it
        # now wants to reset to.
        assert hold.total_index >= 0, 'BUG: double reset/release'
        assert self._holds[-1] == hold.total_index, 'BUG: reset/release in bad order'
        self._reset_index(hold.total_index)
        self._holds.pop()
        hold.total_index = -2

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def finished(self):
        return self.index() == self.len()

    def remaining(self, nmin):
        raise NotImplementedError()

    class ParseException(Exception):
        pass

    def error(self, msg):
        raise ParseException(msg)


class ParseFileState(_State):
    """A lazy parsing state implementation, reading from stream."""
    _index = 0 # Index in current _buf
    _total_offset = 0 # Index of first _buf entry in stream since start
    _fobj = None

    def __repr__(self):
        return 'PFS(ix={}, to={}, buf="{}")'.format(self._index, self._total_offset, ''.join(self._buf))

    def __init__(self, f):
        self._stream_finished = False
        self._holds = []
        self._buf = []
        self._index = 0
        self._total_offset = 0
        if type(f) is str:
            self._fobj = open(f, 'r')
        elif isinstance(f, io.IOBase):
            self._fobj = f
        else:
            raise NotImplementedError('unknown input source {}'.format(f))

    def __del__(self):
        if self._fobj:
            self._fobj.close()

    # For efficiency reasons, only check for collectable buffer space when
    # the buffer is longer than this limit.
    COLLECT_LOWER_LIMIT = 1024

    def _maybe_collect(self):
        if len(self._buf) < self.COLLECT_LOWER_LIMIT:
            return
        # No holds left, forget everything up to now.
        if len(self._holds) == 0:
            # This copies the entire buffer; however, we assume that it is small
            # as it is only filled incrementally from the stream. Still, it's quadratic;
            # this should be mitigated somewhat by the COLLECT_LOWER_LIMIT.
            self._buf = self._buf[self._index:]
            self._total_offset += self._index
            self._index = 0
            return
        elif self._holds[0]-self._total_offset > 0:
            # Find oldest hold and update buffer to hold everything from the oldest hold onwards.
            to_clean = self._holds[0]-self._total_offset
            self._buf = self._buf[to_clean:]
            self._total_offset += to_clean
            self._index -= to_clean

    def _reset_index(self, i):
        assert i >= self._total_offset and i <= self._total_offset + self._index
        self._index = i - self._total_offset

    def index(self):
        return self._total_offset + self._index

    PREFILL = 256

    def fill_buffer(self, min=0):
        if len(self._buf)-self._index <= min:
            new = self._fobj.read(self.PREFILL)
            self._buf.extend(new)
            if len(new) == 0:
                self._stream_finished = True

    def peek(self):
        self.fill_buffer()
        if self.finished():
            return None
        return self._buf[self._index]

    def next(self):
        self.fill_buffer()
        if self.finished():
            return None
        self._index += 1
        return self._buf[self._index-1]

    def advance(self, n):
        self.fill_buffer(self._index + n)
        self._index += n

    def remaining(self, nmin=-1):
        self.fill_buffer(self.PREFILL if nmin == -1 else nmin)
        if nmin == -1:
            return ''.join(self._buf[self._index:])
        return ''.join(self._buf[self._index:self._index+nmin])

    def len(self):
        print('warning: len() is inaccurate on ParseFileState, returning only past and present state')
        return self._total_offset + len(self._buf)

    def finished(self):
        return self._stream_finished and self._index == len(self._buf)

class ParseState(_State):
    """Encapsulates state as the parser goes through input supplied as string."""


    def __init__(self, s):
        """Create a ParseState object from str s, representing the input to be parsed."""
        self._holds = []
        self._input = s
        self._index = 0

    def __repr__(self):
        if self._index < len(self._input):
            return 'ParseState({}< {} >{})'.format(
                    self._input[0:self._index], self._input[self._index], self._input[self._index+1:])
        else:
            return 'ParseState({}<>)'.format(self._input)

    # We override hold/release/reset here because ParseState holds the entire
    # input in memory all the time. Thus we only need to use holds for resets,
    # but not for garbage collection.

    def hold(self):
        hold = _State.ParserHold()
        hold.total_index = self.index()
        return hold

    def release(self, hold):
        """Release a hold. Generally called when a parser was successful."""
        assert hold.total_index >= 0, 'double release'
        hold.total_index = -1

    def reset(self, hold):
        """Release hold and reset index to its position."""
        assert hold.total_index >= 0, 'double reset'
        self._index = hold.total_index
        hold.total_index = -2

    def next(self):
        if self.finished():
            return None
        self._index += 1
        return self._input[self._index-1]

    def advance(self, n):
        self._index += n

    def peek(self):
        if self._index < len(self._input):
            return self._input[self._index]
        return None

    def index(self):
        return self._index

    def len(self):
        return len(self._input)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def finished(self):
        return self._index == len(self._input)

    def remaining(self, nmin=-1):
        if self.finished():
            return ''
        if nmin == -1:
            return self._input[self._index:]
        return self._input[self._index:self._index+nmin]