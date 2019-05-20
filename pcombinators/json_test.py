#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example on how to write a JSON parser.

@author: lbo
"""

from combinators import *
from primitives import *

def JString():
    return Last(Skip(String('"')) + NoneInSet('"') + Skip(String('"')))

def List():
    wrapl = lambda l: [l] #if isinstance(l, list) else l
    entry = (Skip(Whitespace()) + (Value()))
    midentry = entry + Skip(String(','))
    return (
            Skip(String('[')) +
            Repeat(midentry, -1) +
            entry +
            Skip(String(']'))) >> wrapl # Wrap list inside another list to protect it from flattening.

def Dict():
    wrapl = lambda l: [l]
    separator = Skip((Whitespace() + String(":") + Whitespace()))
    entry = (JString() + separator + (Value() >> wrapl)) >> (lambda l: tuple(l))
    midentry = entry + Skip(String(',') + Whitespace())
    dct = Skip(String("{")) + Repeat(midentry, -1) + entry + Skip(String("}"))
    fulldict = dct >> dict
    return fulldict

class Value(Parser):

    def parse(self, st):
        return Last(Skip(Whitespace()) + (Dict() | List() | JString() | Float()) + Skip(Whitespace())).parse(st)