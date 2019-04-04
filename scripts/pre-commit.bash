#!/usr/bin/env bash

echo "Running pre-commit hook"

if [ $# -eq 0 ]
  then
  
    cd logomaker/tests
	python functional_tests_logomaker.py
	
fi

echo "printing number of functional test failures:"

# magic line to ensure that we're always inside the root of our application,
# no matter from which directory we'll run script
#cd "${0%/*}/.."

# echo $1 # prints out first argument to bash script

if [ $# -ne 0 ]
then

if [ "$1" == "0" ]; then
	echo $1
    echo "no failures"
    echo 'Code should be committed...'
else
    echo "non-zero functional test failures"
	echo $1
    echo "do NOT commit code"
    #echo "Failed!" && exit 1
    exit 1
fi

fi

# $? stores exit value of the last command
if [ $? -ne 0 ]; then
 echo "Tests must pass before commit!"
 exit 1
fi