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
