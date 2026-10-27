"""FastAPI routes for managing student records."""

from contextlib import asynccontextmanager
from datetime import date
import sqlite3
from typing import Any

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field, ValidationError, model_validator

from app.database import get_connection, init_db
from fastapi.responses import HTMLResponse

@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="EWB Student Database API",
    description=(
        "A simple student-record management API built with Python, FastAPI and SQLite. "
        "Use the interactive /docs page to try the CRUD endpoints."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


class StudentCreate(BaseModel):
    """Required and optional fields for creating a student."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100, examples=["Aarav Sharma"])
    date_of_birth: date = Field(examples=["2005-06-15"])
    email: EmailStr | None = Field(default=None, examples=["aarav@example.com"])
    phone: str | None = Field(default=None, max_length=30, examples=["9876543210"])
    course: str | None = Field(default=None, max_length=100, examples=["BCA"])
    address: str | None = Field(default=None, max_length=250, examples=["Kolkata, West Bengal"])
    enrollment_date: date | None = Field(default=None, examples=["2024-08-01"])

    @model_validator(mode="after")
    def validate_student_details(self):
        if not self.email and not self.phone:
            raise ValueError("Provide at least one contact detail: email or phone.")
        if self.date_of_birth > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        if self.enrollment_date and self.enrollment_date > date.today():
            raise ValueError("Enrollment date cannot be in the future.")
        return self


class StudentUpdate(BaseModel):
    """Optional fields for a partial update (PATCH)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    date_of_birth: date | None = None
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    course: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=250)
    enrollment_date: date | None = None


class StudentResponse(BaseModel):
    """Public response schema for a stored student record."""

    model_config = ConfigDict(from_attributes=True)

    student_id: int
    name: str
    date_of_birth: date
    email: str | None = None
    phone: str | None = None
    course: str | None = None
    address: str | None = None
    enrollment_date: date | None = None
    created_at: str


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def date_values_to_strings(values: dict[str, Any]) -> dict[str, Any]:
    """Convert Python date values to ISO strings for SQLite."""
    return {
        key: value.isoformat() if isinstance(value, date) else value
        for key, value in values.items()
    }


def get_student_or_404(connection: sqlite3.Connection, student_id: int) -> sqlite3.Row:
    row = connection.execute(
        "SELECT * FROM students WHERE student_id = ?", (student_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Student not found.")
    return row


def handle_duplicate_email(error: sqlite3.IntegrityError) -> None:
    if "students.email" in str(error).lower() or "unique constraint failed: students.email" in str(error).lower():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email address already exists.",
        ) from error
    raise HTTPException(status_code=409, detail="The record conflicts with existing data.") from error



@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#07111f">
<title>EWB | Student Database API</title>

<style>
:root {
    --bg: #07111f;
    --panel: rgba(14, 31, 52, 0.84);
    --border: rgba(91, 200, 255, 0.19);
    --blue: #35caff;
    --lime: #c5ff35;
    --text: #f4f8ff;
    --muted: #9aabc3;
}

* { box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
    margin: 0;
    min-height: 100vh;
    color: var(--text);
    font-family: Inter, "Segoe UI", Arial, sans-serif;
    background:
        radial-gradient(ellipse at 12% 8%, #103865 0, transparent 38%),
        radial-gradient(ellipse at 95% 45%, #092c40 0, transparent 35%),
        var(--bg);
    overflow-x: hidden;
}

body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: .18;
    background-image: radial-gradient(#75cfff 0.7px, transparent 0.7px);
    background-size: 27px 27px;
    mask-image: linear-gradient(to bottom, black, transparent 85%);
}

a { color: inherit; text-decoration: none; }
button { font: inherit; }

.container {
    width: min(1120px, calc(100% - 40px));
    margin: auto;
    position: relative;
}

header {
    min-height: 82px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    border-bottom: 1px solid rgba(255,255,255,.07);
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-mark {
    width: 46px;
    height: 46px;
    display: grid;
    place-items: center;
    border-radius: 14px;
    font-weight: 900;
    letter-spacing: -2px;
    font-size: 19px;
    color: #07111f;
    background: linear-gradient(135deg, var(--lime), var(--blue));
    box-shadow: 0 0 26px #35caff20;
}

.brand-name { font-weight: 800; letter-spacing: .6px; }
.brand-sub { color: var(--muted); font-size: 11px; margin-top: 4px; }

.status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 9px 13px;
    border: 1px solid var(--border);
    border-radius: 30px;
    background: #0c2034;
    color: #cce7f8;
    font-size: 12px;
}

.dot {
    width: 8px;
    height: 8px;
    background: var(--lime);
    border-radius: 50%;
    box-shadow: 0 0 12px var(--lime);
}

.hero {
    display: grid;
    grid-template-columns: 1.2fr .8fr;
    gap: 55px;
    align-items: center;
    padding: 86px 0 68px;
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 9px;
    color: var(--blue);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1.8px;
    text-transform: uppercase;
}

.eyebrow::before {
    content: "";
    width: 24px;
    height: 2px;
    background: var(--lime);
    box-shadow: 0 0 12px var(--lime);
}

h1 {
    font-size: clamp(39px, 5.4vw, 68px);
    line-height: 1.06;
    letter-spacing: -2.6px;
    margin: 22px 0;
}

.gradient-text {
    color: var(--blue);
    background: linear-gradient(95deg, var(--blue), #8dbeff 60%, var(--lime));
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.lead {
    max-width: 560px;
    line-height: 1.8;
    color: #aebed2;
    font-size: 15px;
}

.actions {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 29px;
}

.btn {
    border: 1px solid var(--border);
    display: inline-flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
    padding: 14px 19px;
    border-radius: 11px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 800;
    transition: transform .2s, box-shadow .2s, background .2s;
}

.btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 28px #0005;
}

.btn-primary {
    color: #07111f;
    background: linear-gradient(110deg, var(--lime), #a7ff66);
    border-color: transparent;
}

.btn-secondary {
    color: var(--text);
    background: rgba(255,255,255,.035);
}

.microcopy {
    color: #71859f;
    font-size: 11px;
    margin-top: 18px;
}

.visual {
    position: relative;
    padding: 28px;
    border: 1px solid rgba(81,198,255,.3);
    border-radius: 22px;
    background: linear-gradient(145deg, #102944e8, #091725ef);
    box-shadow: 0 0 65px #087bc51a, inset 0 1px #ffffff10;
    animation: float 5s ease-in-out infinite;
}

.visual::before {
    content: "";
    position: absolute;
    z-index: -1;
    inset: -1px;
    border-radius: inherit;
    background: linear-gradient(130deg, #35caff45, transparent 48%, #c5ff3520);
    filter: blur(22px);
}

.window-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #ffffff12;
    padding-bottom: 17px;
    margin-bottom: 19px;
}

.window-title { font-weight: 700; font-size: 13px; }

.window-dots { display: flex; gap: 5px; }
.window-dots span {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #42617c;
}
.window-dots span:first-child { background: #ff7777; }
.window-dots span:nth-child(2) { background: #ffd568; }
.window-dots span:nth-child(3) { background: #9de77a; }

.api-line {
    display: flex;
    gap: 12px;
    align-items: center;
    margin: 12px 0;
    padding: 12px;
    border: 1px solid #ffffff0a;
    background: #ffffff04;
    border-radius: 9px;
    transition: border-color .2s, transform .2s;
}
.api-line:hover {
    border-color: #35caff70;
    transform: translateX(4px);
}

.method {
    min-width: 57px;
    text-align: center;
    font-size: 10px;
    font-weight: 900;
    padding: 6px 5px;
    border-radius: 5px;
}
.get { color: #73caff; background: #1684d51c; }
.post { color: #baff71; background: #8ae33119; }
.patch { color: #e4bdff; background: #b87cff1b; }
.delete { color: #ff9999; background: #ff77771b; }

.path { font-family: Consolas, monospace; font-size: 12px; }
.path-note { color: #7e91a9; font-size: 11px; margin-top: 4px; }

.visual-footer {
    border-top: 1px solid #ffffff12;
    padding-top: 16px;
    margin-top: 18px;
    font-size: 11px;
    color: #8ea7be;
}

.section-heading { margin-bottom: 24px; }
.section-heading h2 { font-size: 25px; margin: 10px 0; }
.section-heading p { font-size: 13px; line-height: 1.7; color: var(--muted); }

.features {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 17px;
    padding-bottom: 75px;
}

.feature {
    padding: 23px;
    border: 1px solid var(--border);
    border-radius: 15px;
    background: linear-gradient(145deg, #102339b8, #0a1826c9);
    transition: border-color .2s, transform .2s, background .2s;
}
.feature:hover {
    transform: translateY(-5px);
    border-color: #35caff88;
    background: #112a41;
}

.feature-icon {
    width: 43px;
    height: 43px;
    display: grid;
    place-items: center;
    border: 1px solid #35caff30;
    background: #35caff0e;
    border-radius: 12px;
    color: var(--blue);
    font-size: 20px;
    font-weight: 900;
}
.feature h3 { font-size: 15px; margin: 18px 0 8px; }
.feature p { color: var(--muted); font-size: 12px; line-height: 1.8; }

.bottom-panel {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 22px;
    padding: 27px;
    margin-bottom: 55px;
    border: 1px solid var(--border);
    border-radius: 17px;
    background: linear-gradient(110deg, #102c44, #102036);
}
.bottom-panel h2 { margin: 0 0 8px; font-size: 20px; }
.bottom-panel p { margin: 0; color: var(--muted); font-size: 12px; line-height: 1.7; }

#healthResult {
    margin-top: 12px;
    min-height: 18px;
    font-size: 12px;
    color: var(--muted);
}

footer {
    border-top: 1px solid #ffffff10;
    padding: 24px 0;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    color: #71849d;
    font-size: 11px;
}

footer strong { color: #b5c8dc; }

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-7px); }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: .01ms !important;
        transition-duration: .01ms !important;
        scroll-behavior: auto !important;
    }
}

@media (max-width: 760px) {
    .hero { grid-template-columns: 1fr; gap: 35px; padding: 58px 0; }
    h1 { letter-spacing: -1.7px; }
    .visual { padding: 19px; }
    .features { grid-template-columns: 1fr; padding-bottom: 45px; }
    header { min-height: 72px; }
    .status { font-size: 10px; padding: 8px; }
    .bottom-panel { padding: 21px; }
}
</style>
</head>

<body>
<div class="container">

<header>
    <a class="brand" href="/" aria-label="EWB Student Database homepage">
        <div class="brand-mark">EWB</div>
        <div>
            <div class="brand-name">STUDENT DATABASE</div>
            <div class="brand-sub">PYTHON BACKEND DEVELOPMENT</div>
        </div>
    </a>
    <div class="status"><span class="dot"></span> API SERVER RUNNING</div>
</header>

<main>
<section class="hero">
    <div>
        <div class="eyebrow">EWB Internship Project</div>
        <h1>Student records.<br><span class="gradient-text">Made simpler.</span></h1>

        <p class="lead">
            A student record management API built with Python, FastAPI
            and SQLite. Explore the endpoints, manage student records,
            and see the backend in action.
        </p>

        <div class="actions">
            <a class="btn btn-primary" href="/docs">
                Explore API Docs <span aria-hidden="true">↗</span>
            </a>
            <button class="btn btn-secondary" id="checkHealth" type="button">
                <span aria-hidden="true">◉</span> Check API Health
            </button>
        </div>

        <div id="healthResult" role="status" aria-live="polite">
            Ready to test the API connection.
        </div>

        <p class="microcopy">
            FASTAPI · SQLITE · CRUD OPERATIONS · INTERACTIVE DOCUMENTATION
        </p>
    </div>

    <div class="visual">
        <div class="window-top">
            <div class="window-title">▣ API Explorer</div>
            <div class="window-dots"><span></span><span></span><span></span></div>
        </div>

        <div class="api-line">
            <span class="method post">POST</span>
            <div><div class="path">/students</div><div class="path-note">Create a student</div></div>
        </div>
        <div class="api-line">
            <span class="method get">GET</span>
            <div><div class="path">/students</div><div class="path-note">List student records</div></div>
        </div>
        <div class="api-line">
            <span class="method patch">PATCH</span>
            <div><div class="path">/students/{id}</div><div class="path-note">Update student details</div></div>
        </div>
        <div class="api-line">
            <span class="method delete">DELETE</span>
            <div><div class="path">/students/{id}</div><div class="path-note">Delete a student record</div></div>
        </div>

        <div class="visual-footer">
            <span style="color:var(--lime)">●</span>
            Designed for clear API testing and demonstration
        </div>
    </div>
</section>

<section id="features">
    <div class="section-heading">
        <div class="eyebrow">Core capabilities</div>
        <h2>Everything you need to get started.</h2>
        <p>Explore the four fundamental operations of a student database.</p>
    </div>

    <div class="features">
        <article class="feature">
            <div class="feature-icon">＋</div>
            <h3>Create Records</h3>
            <p>Add a student with validated information and save the record in the database.</p>
        </article>
        <article class="feature">
            <div class="feature-icon">⌕</div>
            <h3>Read & Search</h3>
            <p>Retrieve student details, list records and explore available filters.</p>
        </article>
        <article class="feature">
            <div class="feature-icon">↻</div>
            <h3>Update & Delete</h3>
            <p>Modify existing records or remove entries using the documented endpoints.</p>
        </article>
    </div>
</section>

<section class="bottom-panel">
    <div>
        <h2>Ready to explore the API?</h2>
        <p>Open the interactive documentation to send requests and inspect responses.</p>
    </div>
    <a class="btn btn-primary" href="/docs">Launch Swagger UI ↗</a>
</section>
</main>

<footer>
    <span><strong>EWB Student Database API</strong> · Internship Project</span>
    <button class="btn btn-secondary" id="copyUrl" type="button">
        Copy Base URL
    </button>
</footer>

</div>

<script>
const healthButton = document.getElementById("checkHealth");
const healthResult = document.getElementById("healthResult");

healthButton.addEventListener("click", async () => {
    healthButton.disabled = true;
    healthButton.textContent = "Checking connection...";
    healthResult.textContent = "Contacting the API health endpoint...";

    try {
        const response = await fetch("/health", { cache: "no-store" });

        if (!response.ok) {
            throw new Error("HTTP " + response.status);
        }

        healthResult.textContent = "✓ API is responding successfully.";
        healthResult.style.color = "#c5ff35";
    } catch (error) {
        healthResult.textContent =
            "Connection check failed. Make sure the API server is running.";
        healthResult.style.color = "#ff9999";
    } finally {
        healthButton.disabled = false;
        healthButton.innerHTML = '<span aria-hidden="true">◉</span> Check API Health';
    }
});

document.getElementById("copyUrl").addEventListener("click", async () => {
    const button = document.getElementById("copyUrl");

    try {
        await navigator.clipboard.writeText(window.location.origin);
        button.textContent = "Copied ✓";
    } catch (error) {
        button.textContent = "Copy unavailable";
    }

    setTimeout(() => {
        button.textContent = "Copy Base URL";
    }, 2000);
});
</script>
</body>
</html>
"""


@app.get("/health", tags=["General"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, tags=["Students"])
def create_student(student: StudentCreate) -> dict[str, Any]:
    values = date_values_to_strings(student.model_dump())
    fields = ", ".join(values.keys())
    placeholders = ", ".join("?" for _ in values)
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                f"INSERT INTO students ({fields}) VALUES ({placeholders})",
                tuple(values.values()),
            )
            row = connection.execute(
                "SELECT * FROM students WHERE student_id = ?", (cursor.lastrowid,)
            ).fetchone()
            return row_to_dict(row)
    except sqlite3.IntegrityError as error:
        handle_duplicate_email(error)


@app.get("/students", response_model=list[StudentResponse], tags=["Students"])
def list_students(
    name: str | None = Query(default=None, description="Filter by part of a student's name"),
    course: str | None = Query(default=None, description="Filter by course"),
    born_after: date | None = Query(default=None, description="Only students born after this date"),
    born_before: date | None = Query(default=None, description="Only students born before this date"),
) -> list[dict[str, Any]]:
    conditions: list[str] = []
    parameters: list[Any] = []

    if name:
        conditions.append("name LIKE ? COLLATE NOCASE")
        parameters.append(f"%{name.strip()}%")
    if course:
        conditions.append("course LIKE ? COLLATE NOCASE")
        parameters.append(f"%{course.strip()}%")
    if born_after:
        conditions.append("date_of_birth > ?")
        parameters.append(born_after.isoformat())
    if born_before:
        conditions.append("date_of_birth < ?")
        parameters.append(born_before.isoformat())

    sql = "SELECT * FROM students"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY student_id"

    with get_connection() as connection:
        rows = connection.execute(sql, parameters).fetchall()
        return [row_to_dict(row) for row in rows]


@app.get("/students/{student_id}", response_model=StudentResponse, tags=["Students"])
def get_student(student_id: int) -> dict[str, Any]:
    with get_connection() as connection:
        return row_to_dict(get_student_or_404(connection, student_id))


@app.put("/students/{student_id}", response_model=StudentResponse, tags=["Students"])
def replace_student(student_id: int, student: StudentCreate) -> dict[str, Any]:
    """Replace all editable fields of an existing student record."""
    values = date_values_to_strings(student.model_dump())
    assignments = ", ".join(f"{field} = ?" for field in values)
    try:
        with get_connection() as connection:
            get_student_or_404(connection, student_id)
            connection.execute(
                f"UPDATE students SET {assignments} WHERE student_id = ?",
                (*values.values(), student_id),
            )
            row = connection.execute(
                "SELECT * FROM students WHERE student_id = ?", (student_id,)
            ).fetchone()
            return row_to_dict(row)
    except sqlite3.IntegrityError as error:
        handle_duplicate_email(error)


@app.patch("/students/{student_id}", response_model=StudentResponse, tags=["Students"])
def update_student(student_id: int, changes: StudentUpdate) -> dict[str, Any]:
    """Update only the submitted fields while preserving the rest."""
    updates = date_values_to_strings(changes.model_dump(exclude_unset=True))
    with get_connection() as connection:
        current_row = get_student_or_404(connection, student_id)
        current = row_to_dict(current_row)
        updated = {key: current[key] for key in StudentCreate.model_fields}
        updated.update(updates)

        try:
            # Revalidate the merged record so partial changes cannot leave it invalid.
            validated = StudentCreate(**updated)
        except ValidationError as error:
            raise HTTPException(status_code=422, detail=error.errors()) from error

        values = date_values_to_strings(validated.model_dump())
        assignments = ", ".join(f"{field} = ?" for field in values)
        try:
            connection.execute(
                f"UPDATE students SET {assignments} WHERE student_id = ?",
                (*values.values(), student_id),
            )
        except sqlite3.IntegrityError as error:
            handle_duplicate_email(error)

        row = connection.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
        return row_to_dict(row)


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Students"])
def delete_student(student_id: int) -> None:
    with get_connection() as connection:
        get_student_or_404(connection, student_id)
        connection.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    return None
