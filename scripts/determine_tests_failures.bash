echo "printing number of functional test failures:"

# magic line to ensure that we're always inside the root of our application,
# no matter from which directory we'll run script
cd "${0%/*}/.."

# echo $1 # prints out first argument to bash script

pwd
echo $1 > scripts/output.txt