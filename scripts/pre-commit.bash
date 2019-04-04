#!/usr/bin/env bash

echo "Running pre-commit hook"

cd logomaker/tests
python functional_tests_logomaker.py


# $? stores exit value of the last command
if [ $? -ne 0 ]; then
 echo "Tests must pass before commit!"
 exit 1
fi