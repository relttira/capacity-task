# capacity-task Solution
Note: The Bash commands below are for macOS. These may differ slightly on other systems.

## Setup
1. Clone the repository.
2. Install [Python 3.14.2](https://www.python.org/downloads/release/python-3142/).
3. Navigate to the project root.
4. Create a Python virtual environment: `python3.14 -m venv .venv`.
5. Activate the environment: `source .venv/bin/activate`.
6. Install the dependencies: `python3.14 -m pip install -r requirements.txt`.

## Run
### API and DB
`fastapi dev app/api/main.py`

### Pytest Tests
`pytest`
