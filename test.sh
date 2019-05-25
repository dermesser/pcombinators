#!/bin/bash

export PYTHONPATH=.

python3 -m pcombinators.tests.test_arith
coverage run -m pcombinators.tests.test_arith
coverage html
