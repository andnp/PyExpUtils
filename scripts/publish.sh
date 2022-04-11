#!/bin/bash

git config credential.helper "store --file=.git/credentials"
echo "https://${GH_TOKEN}:@github.com" > .git/credentials

git config user.email "andnpatterson@gmail.com"
git config user.name "github-action"

git fetch --all --tags

git checkout -f main

# sync package dependencies
pipenv-setup sync --dev --pipfile

# bump the version
cz bump --no-verify --yes --check-consistency

git push
git push --tags
