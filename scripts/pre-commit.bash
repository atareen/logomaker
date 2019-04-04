#!/usr/bin/env bash


cd logomaker/tests
python functional_tests_logomaker.py

echo 'about to read error code file'

cd ../..

# check the output produces by running functional tests
error_code=$(<scripts/output_code.txt)
echo $error_code

#if [ "$1" == "0" ]; then
#	echo "Commit hook passed!"
#	echo 'Code should be committed...'
#else
#	echo "non-zero functional test failures: "
#	echo $1
#	echo "do NOT commit code"
#	false
#fi	

#$? stores exit value of the last command
if [ $error_code -ne 0 ]; then
echo "Tests must pass before commit!"
exit 1
fi