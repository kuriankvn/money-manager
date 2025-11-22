# money-manager

## useful pip commands
- list all outdated packages
    - pip list --outdated
- upgrade all outdated packages
    - pip list --outdated --format=json | jq -r '.[].name' | xargs -n1 pip install -U
- uninstall all packages
    - pip freeze | xargs pip uninstall -y

## useful tree commands
- tree
- tree -L 1
- tree -a
- tree -a -L 1

## remove local venv
- deactivate
- rm -rf .venv

## create local venv
- python3 -m venv .venv
- source .venv/bin/activate
- pip uninstall -y setuptools wheel
- pip list --outdated --format=json | jq -r '.[].name' | xargs -n1 pip install -U
- pip install -r requirements.txt

## run in dev edit mode
- install dev dependencies: `pip install -e ".[dev]"`
- run tests: `pytest`
- run application: `money-manager`
- remove dependencies: `pip uninstall -y money-manager && pip freeze | xargs pip uninstall -y`

## run in release edit mode
- install release dependencies: `pip install -e .`
- run application: `money-manager`
- remove dependencies: `pip uninstall -y money-manager && pip freeze | xargs pip uninstall -y`

## run in release mode
- install release dependencies: `pip install .`
- run application: `money-manager`
- remove dependencies: `pip uninstall -y money-manager && pip freeze | xargs pip uninstall -y`

## packaging application
### using pip
- create wheel: `pip wheel .`
- create and install wheel: `pip install .`
- remove dependencies: `pip uninstall -y money-manager && pip freeze | xargs pip uninstall -y`
### using build
- install build: `pip install build~=1.3.0`
- create wheel: `python3 -m build`
- install wheel: `pip install dist/money_manager-0.1.0-py3-none-any.whl`
- remove dependencies: `pip uninstall -y money-manager && pip freeze | xargs pip uninstall -y`