# HireHub — Job Hiring & Recruitment Portal

A full-stack recruitment platform built with **Python 3.12, Flask, MongoDB, Bootstrap 5, and Chart.js**.

---

## Features

| Area | Details |
|------|---------|
| **Roles** | Candidate, Recruiter, Admin |
| **Auth** | Register, login, logout, session, role-based decorators, password hashing |
| **Jobs** | Post, edit, close, search, filter (keyword / skill / location / salary / experience / mode / type), pagination |
| **Applications** | Apply, withdraw, status workflow, duplicate prevention, closed-job guard |
| **Interviews** | Schedule, update, cancel, candidate notifications |
| **Resume** | Upload (PDF/DOC/DOCX ≤5 MB), replace, download (authorised), delete |
| **Matching** | Rule-based skill/experience/location/salary scoring (no ML) |
| **Recommendations** | Top-N open jobs sorted by match score |
| **Notifications** | In-app, unread badge, mark read / mark all read |
| **Analytics** | Chart.js charts — skills, locations, status, monthly trends |
| **Reports** | Candidate / job / application reports with CSV export |
| **Audit Logs** | Every key action recorded, admin-visible |
| **REST API** | Full JSON API under `/api/` with consistent response envelope |

---

## Quick Start

### 1 — Prerequisites

- Python 3.10+ (3.12 recommended) from [python.org](https://www.python.org/downloads/)
- MongoDB 6+ running locally or a MongoDB Atlas URI
- Git (optional)

### 2 — Clone & set up

```powershell
# Windows PowerShell
cd c:\Hirehub
python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 3 — Configure environment

```powershell
copy .env.example .env
```

Edit `.env`:

```
MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=hirehub
SECRET_KEY=change-this-to-a-random-secret
UPLOAD_FOLDER=app/uploads/resumes
MAX_CONTENT_LENGTH=5242880
FLASK_ENV=development
FLASK_DEBUG=True
```

### 4 — Create indexes

```powershell
python scripts/create_indexes.py
```

### 5 — (Optional) Seed demo data

```powershell
python scripts/seed_data.py
# or to wipe first:
python scripts/seed_data.py --drop
```

Demo credentials (all passwords are `Password123`):
| Role | Email |
|------|-------|
| Admin | admin@hirehub.example.com |
| Recruiter | rahul.sharma@technova.example.com |
| Candidate | aditya.kumar@mail.example.com |

### 6 — Run

```powershell
python run.py
```

Open: http://localhost:5000

---

## Project Structure

```
hirehub/
├── run.py                      # Entry point
├── requirements.txt
├── .env / .env.example
│
├── app/
│   ├── __init__.py             # Application factory
│   ├── config.py               # Dev / Prod / Testing configs
│   ├── extensions.py           # MongoDB connection
│   │
│   ├── models/                 # Domain objects (OOP, inheritance)
│   ├── repositories/           # MongoDB CRUD layer
│   ├── services/               # Business logic
│   ├── routes/
│   │   ├── web/                # Jinja2 HTML routes
│   │   └── api/                # REST JSON routes (/api/*)
│   ├── schemas/                # Document shape helpers
│   ├── utils/                  # Decorators, validators, helpers
│   ├── exceptions/             # Custom exception classes
│   ├── middleware/             # Audit logger
│   ├── templates/              # Jinja2 HTML (Bootstrap 5)
│   ├── static/                 # CSS, JS, images
│   └── uploads/resumes/        # User resume files (git-ignored)
│
├── tests/                      # pytest test suite
├── scripts/
│   ├── seed_data.py
│   └── create_indexes.py
└── docs/
    ├── architecture.md
    ├── api.md
    └── database.md
```

---

## Running Tests

```powershell
# Requires a running MongoDB instance (uses hirehub_test DB)
python -m pytest tests/ -v
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Web framework | Flask 3 |
| Database | MongoDB via PyMongo |
| Templates | Jinja2 |
| Frontend | Bootstrap 5.3, Chart.js 4, Bootstrap Icons |
| Auth | Werkzeug password hashing, Flask session |
| Testing | pytest, pytest-flask |
| Seed data | Faker-compatible fictional data |

---

## Known Limitations / Not Yet Tested

- The application has **not been run end-to-end** in this environment due to missing Python runtime (Windows Store stub). All code is written and reviewed but must be verified by running locally.
- Email sending is **not implemented** (notifications are in-app only).
- Resume MIME-type validation checks extension only; deep MIME sniffing is not performed.
- The `experience` and `education` JSON fields on the edit profile form require valid JSON input from the user.
