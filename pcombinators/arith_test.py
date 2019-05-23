#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Let's test the combinators in a real world application!

@author: lbo
"""

from pcombinators.state import ParseState
from pcombinators.combinators import *
from pcombinators.primitives import *

skip_whitespace = Skip(Whitespace())

def Parens():
    """Parentheses contain a term."""
    return (Operator('(') + Term() + Operator(')')) >> (lambda l: l[1])

def Variable():
    """A variable consists of several letters."""
    return Regex('[a-zA-Z]+[0-9]*')

def Atom():
    """An atom is a variable or a float or a parentheses term."""
    return Skip(Whitespace()).then((Variable() | Parens() | Float()))

def Operator(set):
    """An operator or parenthesis."""
    return OneOf(set)

def operator_result_to_tuple(l):
    if len(l) == 1:
        return l[0]
    elif len(l) == 2 and len(l[1]) == 2:
        return (l[0], l[1][0], l[1][1])
    else:
        # Parse failed if not either 1 or 3.
        raise Exception("Parse failed: Missing operand")

class Power():

    def parse(self, st):
        p = OptimisticSequence(Atom(), Operator('^') + Power()) >> operator_result_to_tuple
        return p.parse(st)

class Product(Parser):

    def parse(self, st):
        # Try to parse an atom, a product operator, and another product.
        p = OptimisticSequence(Power(), skip_whitespace, Operator('*/') + skip_whitespace + Product()) >> operator_result_to_tuple
        return p.parse(st)

class Term(Parser):

    def parse(self, st):
        # Try to parse a product, then a sum operator, then another term.
        # OptimisticSequence will just return a product if there is no sum operator.
        p = OptimisticSequence(Product(), skip_whitespace, Operator('+-') + skip_whitespace + Term()) >> operator_result_to_tuple
        return p.parse(st)

def pretty_print(tpl):
    # tpl is a (left, op, right) tuple or a scalar.
    if not isinstance(tpl, tuple):
        return str(tpl)
    assert len(tpl) == 3
    return '({} {} {})'.format(pretty_print(tpl[0]), tpl[1], pretty_print(tpl[2]))

def parse_and_print(expr):
    """Parse an expression string and return a string of the parsing result."""
    parsed, st = Term().parse(ParseState(expr))
    if parsed is None:
        print('Parse error :(', st)
        return
    return pretty_print(parsed)