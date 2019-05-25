#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 25 22:09:49 2019

@author: lbo
"""

import io
import unittest

import pcombinators.state as st
import pcombinators.tests.arith as arith

class TestArith(unittest.TestCase):

    def test_simple_addition(self):
        want = (1., '+', 2.)
        got = arith.parse('1 + 2')
        self.assertEqual(got, want)

    def test_simple_multiplication(self):
        want = ('a', '*', 'b')
        got = arith.parse('a* b')
        self.assertEqual(got, want)

    def test_parens(self):
        want = ('a', '^', (3., '-', 'e'))
        got = arith.parse('a ^ ( 3 - e)')
        self.assertEqual(got, want)

    def test_var(self):
        want = ('a')
        self.assertEqual(arith.parse('a'), want)

    def test_float(self):
        want = (1.23456789, '+', (-123.456, '*', 332.))
        got = arith.parse('1.23456789+-123.456*332')
        self.assertEqual(got, want)

    def test_fails(self):
        self.assertIsNone(arith.parse('1 + (a +)'))
        self.assertIsNone(arith.parse('1 +'))
        self.assertIsNone(arith.parse('1 *'))
        self.assertIsNone(arith.parse('1 -'))

    def test_complicated(self):
        complicated_haves = [
                '1 + 1', # easy for a start
                '3*4*(a - (b - (c - d) ) * 4)^a^c',
                'a^b^c+d^e^f',
                'a*b+c/d',
                'a + b^(c - d/e) * (3 - (4 + a) + 6^-1)',
        ]
        complicated_wants = [
                (1, '+', 1),
                (3.0,  '*',
                 (4.0, '*',
                  (('a', '-',
                    (('b', '-', ('c', '-', 'd')), '*', 4.0)
                   ), '^',
                    ('a', '^', 'c')))),
                (('a', '^', ('b', '^', 'c')), '+', ('d', '^', ('e', '^', 'f'))),
                (('a','*','b'),'+',('c','/','d')),
                ('a','+',(('b', '^', ('c', '-', ('d', '/', 'e'))), '*',(3.0, '-', ((4.0, '+', 'a'), '+', (6.0, '^', -1.0)))))
        ]
        for (i, (h, w)) in enumerate(zip(complicated_haves, complicated_wants)):
            self.assertEqual(arith.parse(h), w)
        # Assert that this parser also works with the ParseFileState class.
        for (i, (h, w)) in enumerate(zip(complicated_haves, complicated_wants)):
            h = h.replace(' ', '')
            self.assertEqual(arith.parse(st.ParseFileState(io.StringIO(h))), w)

if __name__ == '__main__':
    st.ParseFileState.COLLECT_LOWER_LIMIT = 0
    unittest.main()