#!/bin/bash
set -e
source .venv/bin/activate

git config credential.helper "store --file=.git/credentials"
echo "https://${GH_TOKEN}:@github.com" > .git/credentials

git config user.email "andnpatterson@gmail.com"
git config user.name "github-action"

git fetch --all --tags

git checkout -f master

# bump the version
cz bump --no-verify --yes --check-consistency

# push to pypi repository
python -m build
python -m twine upload -u __token__ -p ${PYPI_TOKEN} --non-interactive dist/*

pip install uv
uv pip compile --extra=dev pyproject.toml -o requirements.txt
git add requirements.txt
git commit -m "ci: update requirements" || echo "No changes to commit"

git push
git push --tags
