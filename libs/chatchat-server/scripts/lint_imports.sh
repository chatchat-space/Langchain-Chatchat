#!/bin/bash

set -eu

# Initialize a variable to keep track of errors
errors=0

# make sure not importing from chatchat
git --no-pager grep '^from chatchat\.' . && errors=$((errors+1))

# Decide on an exit status based on the errors
if [ "$errors" -gt 0 ]; then
    exit 1
else
    exit 0
fi
