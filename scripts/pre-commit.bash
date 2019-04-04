#!/usr/bin/env bash

echo "Running pre-commit hook"

echo $1

if [ -$1 "$var" ]
then
      echo "\$var is empty"
else
      echo "\$var is NOT empty"
fi

cd logomaker/tests
python functional_tests_logomaker.py


# $? stores exit value of the last command
#if [ $? -ne 0 ]; then
# echo "Tests must pass before commit!"
# exit 1
#fi