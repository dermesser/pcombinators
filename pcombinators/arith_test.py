#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Let's test the combinators in a real world application!

@author: lbo
"""

from combinators import *


def Parens():
    """Parentheses contain a term."""
    return (Operator('(') + Term() + Operator(')')) >> (lambda l: l[1])

def Variable():
    """A variable consists of several letters."""
    return Last(Whitespace() + Regex('[a-zA-Z]+[0-9]*'))

def Atom():
    """An atom is a variable or a float or a parentheses term."""
    return (Variable() | Parens() | Float())

def Operator(set):
    """An operator or parenthesis."""
    return Last(Skip(Whitespace()) + OneOf(set))

def Power():
    return (
            OptimisticSequence(Last(Atom()), Operator('^'), Last(Atom())) >>
            (lambda l: (l[0], l[1], l[2]) if len(l) == 3 else l[0])
            )

class Product(Parser):

    def parse(self, st):
        # Try to parse an atom, a product operator, and another product.
        p = OptimisticSequence(Power(), Operator('*/'), Product())
        to_tuple = p >> (lambda l: (l[0], l[1], l[2]) if len(l) == 3 else l[0])
        return to_tuple.parse(st)

class Term(Parser):

    def parse(self, st):
        # Try to parse a product, then a sum operator, then another term.
        # OptimisticSequence will just return a product if there is no sum operator.
        p = OptimisticSequence(Product(), Operator('+-'), Term())
        to_tuple = p >> (lambda l: (l[0], l[1], l[2]) if len(l) == 3 else l[0])
        return to_tuple.parse(st)

def pretty_print(tpl):
    # tpl is a (left, op, right) tuple or a scalar.
    if not isinstance(tpl, tuple):
        return str(tpl)
    assert len(tpl) == 3
    return '({} {} {})'.format(pretty_print(tpl[0]), tpl[1], pretty_print(tpl[2]))

def parse_and_print(expr):
    """Parse an expression string and return a string of the parsing result."""
    parsed, st = Term().parse(ps(expr))
    if parsed is None:
        print('Parse error :(', st)
        return
    print(pretty_print(parsed))