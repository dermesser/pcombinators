#!/bin/bash

set -e

export PYTHONPATH=.

if [ -e .coverage ]; then
    rm .coverage
fi

for F in pcombinators/tests/test_*; do
    coverage run --append "${F}"
done

coverage html
