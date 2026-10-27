# Student Database CRUD Application

**EWB Courses — AI/ML vs Future Al Agents**

** Python Back-End Development Implementation**

A REST API for managing student records, built with **Python**, **FastAPI** and **SQLite**. It demonstrates the four core database operations—Create, Read, Update and Delete (CRUD), and includes input validation, filtering, automated tests and interactive API documentation.

## Features

- **Create:** Add student records.
- **Read:** List students, filter records, or retrieve a student by ID.
- **Update:** Replace a record with `PUT` or update selected fields with `PATCH`.
- **Delete:** Remove a student record.
- **SQLite storage:** Save records locally so they remain available after the API server stops and restarts.
- **Validation and error handling:** Validate incoming data and handle missing records and duplicate email addresses.
- **Filtering:** Filter student records by name, course, and date-of-birth range.
- **Interactive homepage:** A project landing page with links to the API documentation and a health-check button.
- **Swagger UI:** Explore and test API endpoints at `/docs`.
- **Automated tests:** Run the included test suite with `pytest`.

## Technology Stack

- Python 3.10 or newer
- FastAPI — API framework
- SQLite — local database, accessed through Python's built-in `sqlite3` module
- Pydantic — request-data validation
- Uvicorn — ASGI server
- pytest — automated testing

## Getting Started

### 1. Download and extract the project

Extract the ZIP file, then open a terminal in the `ewb_student_crud` project directory—the directory containing `requirements.txt`.

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the API server

```bash
python -m uvicorn app.main:app --reload
```

Keep the terminal open while using the application. To stop the server, press `Ctrl+C` in that terminal.

### 5. Open the application

| Page | Local URL | Purpose |
|---|---|---|
| Homepage | `http://127.0.0.1:8000/` | Project landing page and health-check button |
| API documentation | `http://127.0.0.1:8000/docs` | Interactive Swagger UI for testing endpoints |
| Health check | `http://127.0.0.1:8000/health` | Check the API's health response |

The `students.db` SQLite database is created automatically when the application initializes. The database file is stored locally; it is not required in the GitHub repository.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/students` | Create a student record |
| `GET` | `/students` | List student records; supports filters |
| `GET` | `/students/{student_id}` | Retrieve one student by ID |
| `PUT` | `/students/{student_id}` | Replace a student's editable details |
| `PATCH` | `/students/{student_id}` | Update selected student fields |
| `DELETE` | `/students/{student_id}` | Delete a student record |
| `GET` | `/health` | Check the API health endpoint |

### Student fields

- **Required:** `name`, `date_of_birth`, and at least one contact method: `email` or `phone`.
- **Optional:** `email`, `phone`, `course`, `address`, and `enrollment_date`.
- **ID:** Generated automatically by the database.
- **Date format:** Use `YYYY-MM-DD` (for example, `2005-06-15`).

Use fictional or dummy records for demonstrations. Do not submit real student personal information to a public repository or public demo.

### Example create request

Send this JSON body to `POST /students`:

```json
{
  "name": "Aarav Sharma",
  "date_of_birth": "2005-06-15",
  "email": "aarav@example.com",
  "phone": "9876543210",
  "course": "BCA",
  "address": "Kolkata, West Bengal",
  "enrollment_date": "2024-08-01"
}
```

The example uses fictional data. The API response includes the created record and its generated ID.

### Test an endpoint in Swagger UI

1. Open `http://127.0.0.1:8000/docs`.
2. Expand an endpoint, such as `POST /students`.
3. Click **Try it out**.
4. Enter the required parameters or JSON body.
5. Click **Execute** and inspect the response and status code.

You can also use the request examples in `sample_requests.http` with a compatible editor extension or HTTP client.

### Filter examples

Use these examples with `GET /students`:

| Query | Purpose |
|---|---|
| `/students?name=Aarav` | Find names containing `Aarav` |
| `/students?course=BCA` | Find courses containing `BCA` |
| `/students?born_after=2005-01-01` | Filter by date-of-birth lower bound |
| `/students?born_before=2007-01-01` | Filter by date-of-birth upper bound |

## Run the Tests

With the virtual environment activated and dependencies installed, run:

```bash
python -m pytest -q
```

The included tests use a temporary database, so they should not add test records to the normal `students.db` file.

## Project Structure

```text
ewb_student_crud/
├── app/
│   ├── __init__.py
│   ├── database.py
│   └── main.py
├── tests/
│   └── test_main.py
├── screenshots/
│   ├── homepage.png
│   ├── api_documentation.png
│   ├── create_student.png
│   ├── read_student.png
│   ├── update_student.png
│   └── delete_student.png
├── .gitignore
├── README.md
├── requirements.txt
└── sample_requests.http
```

The local `students.db` file may also appear after the application has run. It should be excluded from version control.

## Database Persistence and GitHub Safety

SQLite stores records in the local `students.db` file. On the same computer and with the same database path, records should still be available after stopping and restarting the server. This is local persistence; an online hosting platform may require additional persistent-storage configuration.

## Project Scope

This Project requires a FastAPI + SQLite application with all four CRUD operations, student record fields, input validation, missing-record handling, persistent data retrieval, a readable README, dependency information, and sample requests or screenshots where available.