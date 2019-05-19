#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Let's test the combinators in a real world application!

@author: lbo
"""

from combinators import *


def Parens():
    return (Operator('(') + Term() + Operator(')')) >> (lambda l: l[1])

def Variable():
    return Last(Whitespace() + Regex('\w+'))

def Atom():
    """An atom is a variable or a float or a parentheses term."""
    return (Variable() | Parens() | Float())

def Operator(set):
    """An operator or parenthesis."""
    return Last(Skip(Whitespace()) + OneOf(set))

class Product(Parser):

    def parse(self, st):
        initial = st.index()

        left, st = Atom().parse(st)
        print('p', left, st)
        if left is None:
            st.reset(initial)
            return None, st

        op, st = Operator('*/').parse(st)
        print('p', op, st)
        if op is None:
            return left, st

        right, st = Product().parse(st)
        print('p', right, st)
        if right is None:
            st.reset(initial)
            return None, st
        return ((left, op, right), st)

class Term(Parser):

    def parse(self, st):
        initial = st.index()

        left, st = Product().parse(st)
        print('t', left, st)
        if left is None:
            st.reset(initial)
            return None, st

        op, st = Operator('+-').parse(st)
        print('t', op, st)
        if op is None:
            return left, st

        right, st = Term().parse(st)
        print(right, st)
        if right is None:
            st.reset(initial)
            return None, st

        return (left, op, right), st

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