#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 25 23:58:21 2019

@author: lbo
"""

import io
import unittest

import pcombinators.state as st
import pcombinators.tests.csv as csv

def line(l):
    return csv.line.parse(st.ps(l))[0]

def value(v):
    return csv.value.parse(st.ps(v))[0]

def file(f):
    return csv.file.parse(st.ps(f))[0]

class CSVTest(unittest.TestCase):

    def test_values(self):
        self.assertEqual(1, value('1'))
        self.assertEqual(12, value('12,'))
        self.assertEqual(1.23, value('1.23'))
        self.assertEqual('abc', value('"abc"'))

    def test_line(self):
        self.assertEqual([1], line('1,'))
        self.assertEqual([1], line('1'))
        self.assertEqual([1,2,3,4,5], line('1, 2,3,   4,5\n'))
        self.assertEqual(["a,b", "c", 22], line('"a,b","c", 22\n'))

    def test_file(self):
        csv_in = '"title1", "title2", "title3"\n\n1, 2, "aaa"\n"12", 4, "bbb"\n'
        want = [['title1', 'title2', 'title3'], [], [1, 2, 'aaa'], ['12', 4, 'bbb']]
        self.assertEqual(want, file(csv_in))
        self.assertEqual(want, csv.file.parse(st.ParseFileState(io.StringIO(csv_in)))[0])

if __name__ == '__main__':
    st.ParseFileState.COLLECT_LOWER_LIMIT = 0
    unittest.main()
