#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 23 22:34:33 2019

@author: lbo
"""

import time

def time_it(f):
    def f_(*args, **kwargs):
        before = time.time()
        r = f(*args, **kwargs)
        print(f, time.time()-before)
        return r
    return f_

def remove_unused_whitespace(s):
    acc = []
    lvl = 0
    ws = set(' \n\t\r')
    for c in s:
        if c == '"':
            lvl += 1 if lvl == 0 else -1
        if lvl == 0 and c in ws:
            continue
        acc.append(c)
    return ''.join(acc)
