#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 24 23:46:48 2019

@author: lbo
"""

from pcombinators import *

separator = Whitespace() + OneOf(",") + Whitespace()
string = Skip(String('"')) + NoneInSet('"') + Skip(String('"'))
integer = Last(Integer() + Skip((Peek(NoneInSet('.')) | EndOfInput())))
value = integer | Float() | Last(string)
line = Flatten(Repeat(OptimisticSequence(value, Skip(separator)), -1)).then_skip((String('\n') | EndOfInput()))

file = Repeat(line, -1)