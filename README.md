# capacity-task Solution
Note: The Bash commands below are for macOS. These may differ slightly on other systems in the usual ways.

## Setup
1. Clone the repository.
2. Install [Python 3.14.2](https://www.python.org/downloads/release/python-3142/).
3. Navigate to the project root.
4. Create a Python virtual environment: `python3.14 -m venv .venv`.
5. Activate the environment: `source .venv/bin/activate`.
6. Install the dependencies: `python3.14 -m pip install -r requirements.txt`.

## Run
Ensure the virtual environment has been activated. Then run the following as desired:

### API (and DB)
`fastapi dev app/api/main.py`

This will start the server at http://127.0.0.1:8000. If you'd like, you can test the endpoint in the documentation at http://127.0.0.1:8000/docs.

### Tests
`pytest`

This will run the endpoint tests.
