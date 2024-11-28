# Safe Route Calculation API

This API calculates the safest route between a start and an end location, using flood risk data from the UP NOAH dataset, which is pre-loaded via a remote database.

---

## Requirements

1. **Python**: Ensure Python 3.13 is installed.
   - To verify, run:
     ```bash
     python3.13 --version
     ```
   - If not installed, download and install it from the [official Python website](https://www.python.org/downloads/).

2. **Database Credentials**: Add a `db_env.py` file in the main directory containing the database credentials. This file should be formatted as follows:
   ```python
      DB_NAME = ""
      DB_USER = ""
      DB_PASSWORD = ""
      DB_HOST = ""
      DB_PORT = ""
      TABLE_NAME = ""
   ```

---

## Setup Instructions

1. Clone the repository or download the source code.

2. Navigate to the project directory.

3. Set up a virtual environment:
   ```bash
   python3.13 -m venv .venv
   ```

4. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

5. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the FastAPI Server

1. Start the development server:
   ```bash
   fastapi dev main.py
   ```

2. By default, the API will be available at:
   ```
   http://127.0.0.1:8000
   ```

3. Use the `/directions` endpoint to calculate the safest route. Example:
   ```
   http://127.0.0.1:8000/directions?start=<longitude,latitude>&end=<longitude,latitude>
   ```

   Replace `<longitude,latitude>` with the appropriate coordinates for the start and end locations.

   Example for Quezon City:
   ```
   http://127.0.0.1:8000/directions?start=121.0437,14.6760&end=121.0567,14.6517
   ```

---

## Running Tests with Pytest

1. Ensure the virtual environment is activated:
   ```bash
   source .venv/bin/activate
   ```

2. Run the test suite using `pytest`:
   ```bash
   pytest
   ```

3. View the test results in the terminal. Pytest will display detailed feedback about the tests.

---

## Notes

- The UP NOAH dataset is pre-loaded and does not require manual setup.
- Modify the `host` and `port` in the `fastapi` command if needed to match your environment.
- Ensure the `db_env.py` file is correctly configured for database access.
- Route requests with a location outside Quezon City could result to an incorrect route data since flood data is limited to Quezon City only.

---

For further assistance, refer to the FastAPI [documentation](https://fastapi.tiangolo.com/) or contact the project maintainer.
