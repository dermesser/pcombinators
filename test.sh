#!/bin/bash

set -e

export PYTHONPATH=.

for F in pcombinators/tests/test_*; do
    coverage run ${F}
done

coverage html
