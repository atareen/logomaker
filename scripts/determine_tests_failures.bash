echo "printing number of functional test failures:"

# magic line to ensure that we're always inside the root of our application,
# no matter from which directory we'll run script
cd "${0%/*}/.."

# echo $1 # prints out first argument to bash script


if [ "$1" == "0" ]; then
    echo "no failures"
else
    echo "non-zero functional test failures"
    echo "not committing code"
    set -e
    exit 1
fi

echo 'Code should be committed...'
