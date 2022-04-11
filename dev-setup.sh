pipenv --python 3.10
pipenv install --dev

pipenv run pre-commit install -t pre-commit -t commit-msg
