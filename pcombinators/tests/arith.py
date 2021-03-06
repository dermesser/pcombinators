#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Let's test the combinators in a real world application!

@author: lbo
"""

from pcombinators.state import ParseState
from pcombinators.combinators import *
from pcombinators.primitives import *

def Operator(set):
    """An operator or parenthesis."""
    return OneOf(set)

def Parens():
    """Parentheses contain a term."""
    return (Operator('(') + Term() + Operator(')')) >> (lambda l: l[1])

def Variable():
    """A variable consists of several letters."""
    return Regex('[a-zA-Z]+[0-9]*')

def Atom():
    """An atom is a variable or a float or a parentheses term."""
    return (Variable() | Parens() | Float())

def Product():
    return OptimisticSequence(Power(), Operator('*/') + Lazy(Product)) >> operator_result_to_tuple

class Power(Parser):
    ops = Operator('^')

    def __init__(self):
        self.p = OptimisticSequence(Lazy(Atom), self.ops + self) >> operator_result_to_tuple

    def parse(self, st):
        return self.p.parse(st)

class Term(Parser):
    ops = Operator('+-')

    def __init__(self):
        self.p = OptimisticSequence(Product(), self.ops + self) >> operator_result_to_tuple

    def parse(self, st):
        # Try to parse a product, then a sum operator, then another term.
        # OptimisticSequence will just return a product if there is no sum operator.
        return self.p.parse(st)


def operator_result_to_tuple(l):
    if len(l) == 1:
        return l[0]
    elif len(l) == 2 and len(l[1]) == 2:
        return (l[0], l[1][0], l[1][1])
    else:
        # Parse failed if not either 1 or 3.
        raise Exception("Parse failed: Missing operand")

def pretty_print(tpl):
    # tpl is a (left, op, right) tuple or a scalar.
    if not isinstance(tpl, tuple):
        return str(tpl)
    assert len(tpl) == 3
    return '({} {} {})'.format(pretty_print(tpl[0]), tpl[1], pretty_print(tpl[2]))

def parse(s):
    if type(s) is str:
        s = ParseState(s.replace(' ', ''))
    parsed, st = Term().then_skip(EndOfInput()).parse(s)
    if parsed is None:
        print('Parse error :(', st)
        return None
    return parsed

def parse_and_print(expr):
    """Parse an expression string and return a string of the parsing result."""
    return pretty_print(parse(expr))