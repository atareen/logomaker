#!/usr/bin/env bash

echo "Running pre-commit hook"

echo $1

if [ -z "$1" ]
then
    # "No argument supplied"
    cd logomaker/tests
	python functional_tests_logomaker.py

else

if [ "$1" == "0" ]; then
	echo $1
    echo "Commit hook passed!"
    echo 'Code should be committed...'
else
    echo "non-zero functional test failures"
	echo $1
    echo "do NOT commit code"
    echo "Failed!" && exit 1
fi


fi



# $? stores exit value of the last command
#if [ $? -ne 0 ]; then
# echo "Tests must pass before commit!"
# exit 1
#fi