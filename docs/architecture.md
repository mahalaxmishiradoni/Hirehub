# HireHub — Architecture

## Overview

HireHub uses a layered architecture with strict separation of concerns:

```
HTTP Request
     │
     ▼
┌─────────────┐
│   Routes    │  Thin — handle HTTP only (parse input, call service, render/return)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Services   │  Business logic — validation, orchestration, event firing
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  Repositories    │  Database operations only — no business logic
└──────┬───────────┘
       │
       ▼
┌─────────────┐
│   MongoDB   │
└─────────────┘
```

---

## Application Factory

`app/__init__.py` uses the **Flask Application Factory** pattern:

```python
def create_app(config=None) -> Flask:
    app = Flask(__name__, ...)
    app.config.from_object(cfg)
    mongo.init_app(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    return app
```

Benefits:
- Multiple configs (dev / prod / test) without code changes
- Test isolation — each test session creates a fresh app instance
- Avoids circular imports by deferring blueprint registration

---

## Blueprint Structure

Routes are split into two namespaces:

| Namespace | Prefix | Purpose |
|-----------|--------|---------|
| Web blueprints | `/`, `/candidate/`, `/recruiter/`, `/admin/`, `/jobs/`, `/dashboard/` | Jinja2 HTML pages |
| API blueprints | `/api/auth/`, `/api/jobs/`, `/api/applications/`, etc. | JSON REST API |

Each blueprint is a separate file in `app/routes/web/` or `app/routes/api/`.

---

## OOP Design

### Inheritance Hierarchy

```
User  (base class)
 ├── Candidate
 ├── Recruiter
 └── Admin
```

Each subclass:
- calls `super().__init__()` with role constant
- overrides `from_dict()` and `to_dict()`
- adds role-specific properties (`skill_set`, `total_experience`, etc.)

### Key OOP features used

| Feature | Where |
|---------|-------|
| Classes & constructors | All model classes |
| Instance variables | All models |
| Class variables | `User.VALID_ROLES`, `Job.WORK_MODES`, `Application.TRANSITIONS` |
| Class methods | `User.from_dict()`, `Job.from_dict()`, etc. |
| Static methods | `User.hash_password()`, `User.verify_password()`, `MatchingService.rank_jobs()` |
| Properties | `User.email`, `Candidate.skill_set`, `Job.is_open` |
| Inheritance | `Candidate`, `Recruiter`, `Admin` extend `User` |
| Method overriding | `from_dict()`, `to_dict()` in each subclass |
| Abstraction | `BaseRepository` (ABC) defines interface; subclasses implement it |
| Encapsulation | `User._email`, `User._password_hash` (private) |
| Composition | `ApplicationService` uses `JobRepository`, `CandidateRepository`, `NotificationService` |

---

## Repository Pattern

`BaseRepository` is an abstract class (ABC):

```python
class BaseRepository(ABC):
    collection_name: str = ""

    @abstractmethod
    def find_by_id(self, doc_id): ...

    @abstractmethod
    def find_all(self, filters, page, per_page): ...

    # Concrete helpers: insert, update_by_id, delete_by_id, count, _paginate
```

Each concrete repository (`UserRepository`, `JobRepository`, etc.) extends `BaseRepository`, declares `collection_name`, and implements the abstract methods.

---

## Service Layer

Services are injected into routes as module-level instances:

```python
_job_svc = JobService()

@job_bp.route("/<job_id>")
def job_detail(job_id):
    job = _job_svc.get_job(job_id)   # service call only
    return render_template("jobs/detail.html", job=job)
```

Services compose multiple repositories and other services:

```python
class ApplicationService:
    def __init__(self):
        self._apps = ApplicationRepository()
        self._jobs = JobRepository()
        self._candidates = CandidateRepository()
        self._notif = NotificationService()
```

---

## Authentication & Authorisation

- Passwords hashed with `werkzeug.security.generate_password_hash` (PBKDF2-SHA256)
- Sessions stored server-side via Flask's signed cookie session
- Session holds: `user_id`, `email`, `name`, `role`, `profile_id`, `company_id`
- Cookie flags: `HttpOnly=True`, `SameSite=Lax`, `Secure=True` (production only)

### Decorators

```python
@login_required          # checks session["user_id"]
@role_required("ADMIN")  # checks session["role"]
@candidate_required      # shortcut for role_required("CANDIDATE")
@recruiter_required      # shortcut for role_required("RECRUITER")
@admin_required          # shortcut for role_required("ADMIN")
```

All decorators return JSON (401/403) for `/api/*` routes, HTML redirects for web routes.

---

## Error Handling

Centralised in `app/__init__.py`:

```
AppException subclass  →  caught by @app.errorhandler(AppException)
                       →  JSON response for /api/* requests
                       →  HTML error page for web requests
```

Custom exceptions map to HTTP codes:
- `UserAlreadyExistsError` → 409
- `InvalidCredentialsError` → 401
- `UnauthorizedError` → 403
- `JobNotFoundError` → 404
- `DuplicateApplicationError` → 409
- `ValidationError` → 422

---

## Matching Algorithm

`MatchingService.calculate_match(candidate, job)` uses weighted rules:

| Signal | Weight |
|--------|--------|
| Skill overlap | 50 pts |
| Experience range | 20 pts |
| Location / remote | 15 pts |
| Salary range | 10 pts |
| Work mode | 5 pts |
| **Total** | **100 pts** |

No machine learning. Pure rule-based scoring.

---

## File Upload Security

1. Extension whitelist: `.pdf`, `.doc`, `.docx`
2. File size limit: 5 MB (configurable via `MAX_CONTENT_LENGTH`)
3. `werkzeug.utils.secure_filename` sanitises the original name
4. UUID-based stored filename prevents path traversal and collisions
5. Downloads are authorised — candidates can only download their own resume; recruiters can download any

---

## Audit Logging

Every key action is written to `audit_logs` via `AuditLogger.log()`:

```python
AuditLogger.log(user_id, "JOB_CREATED", "jobs", job_id, metadata)
```

Failures in audit logging are silently swallowed (try/except pass) so they never break core flows.
