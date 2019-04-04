echo "printing number of functional test failures:"

# magic line to ensure that we're always inside the root of our application,
# no matter from which directory we'll run script
cd "${0%/*}/.."

# echo $1 # prints out first argument to bash script


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