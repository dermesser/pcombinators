#!/bin/sh

for F in pcombinators/tests/test_*; do
    PYTHONPATH=. python3 ${F};
done
