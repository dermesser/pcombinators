#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 25 23:37:36 2019

@author: lbo
"""

import io
import unittest

import pcombinators.state as st
import pcombinators.tests.json as js

class JSONTest(unittest.TestCase):

    def test_atoms(self):
        self.assertEqual(1.0, js.json_result('1'))
        self.assertEqual('ab cd', js.json_result('"ab cd"'))

    def test_flat_structs(self):
        self.assertEqual([1.0, 2.0, 3.0], js.json_result('[1,   2,3]'))
        self.assertEqual({'a': 'c', 'b': 3.0}, js.json_result('{"a": "c", "b": 3.0}'))

    def test_nested_structs(self):
        self.assertEqual([{"a": [1, 2]}, 3], js.json_result('[{"a": [1,2]}, 3]'))
        self.assertEqual({"a": {"b": {"c": [1,2]}}}, js.json_result('{"a": {"b": {"c": [1,2]}}}'))
        
    def test_stream_parse(self):
        have = '{"id":1,"name":"Foo","price":123,"tags":["Bar","Eek"],"stock":{"warehouse":300,"retail":20}}'
        want = {"id":1,"name":"Foo","price":123,"tags":["Bar","Eek"],"stock":{"warehouse":300,"retail":20}}
        self.assertEqual(want, js.json_result(st.ParseFileState(io.StringIO(have))))

if __name__ == '__main__':
    st.ParseFileState.COLLECT_LOWER_LIMIT = 0
    unittest.main()