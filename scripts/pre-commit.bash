#!/usr/bin/env bash

if [ -z "$1" ]
then
    # "No argument supplied"
    
    echo "Running pre-commit hook"
    
    cd logomaker/tests
	python functional_tests_logomaker.py

else

    echo 'checking whether to commit or not'

	if [ "$1" == "0" ]; then
	    echo "Commit hook passed!"
	    echo 'Code should be committed...'
	else
    	echo "non-zero functional test failures: "
		echo $1
	    echo "do NOT commit code"
    	echo "Failed!" 
    	set -e
fi

fi



# $? stores exit value of the last command
#if [ $? -ne 0 ]; then
# echo "Tests must pass before commit!"
# exit 1
#fi