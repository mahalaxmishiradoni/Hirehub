# HireHub — REST API Reference

Base URL: `http://localhost:5000/api`

All endpoints return JSON in this envelope:

**Success**
```json
{ "success": true, "message": "...", "data": {} }
```

**Error**
```json
{ "success": false, "message": "...", "error_code": "ERROR_CODE" }
```

Authentication is session-based (cookie). Call `POST /api/auth/login` first.

---

## Authentication

### POST /api/auth/register

Register a new user.

**Body (Candidate)**
```json
{
  "name": "Alice Smith",
  "email": "alice@example.com",
  "phone": "9876543210",
  "password": "Password123",
  "confirm_password": "Password123",
  "role": "CANDIDATE"
}
```

**Body (Recruiter)** — add `company_name` and set `role` to `"RECRUITER"`.

**Response 201**
```json
{ "success": true, "message": "Registration successful.", "data": { "user_id": "...", "role": "CANDIDATE" } }
```

**Errors**
| Code | HTTP |
|------|------|
| `USER_ALREADY_EXISTS` | 409 |
| `VALIDATION_ERROR` | 422 |

---

### POST /api/auth/login

```json
{ "email": "alice@example.com", "password": "Password123" }
```

**Response 200** — sets session cookie.
```json
{ "success": true, "message": "Login successful.", "data": { "name": "Alice Smith", "role": "CANDIDATE", ... } }
```

**Errors** — `INVALID_CREDENTIALS` 401

---

### POST /api/auth/logout

Clears the session. No body required.

---

### GET /api/auth/me

Returns the current logged-in user. Requires authentication.

**Response 200**
```json
{ "success": true, "data": { "_id": "...", "name": "...", "email": "...", "role": "..." } }
```

---

## Jobs

### GET /api/jobs

List / search jobs. All parameters optional.

| Query param | Type | Example |
|-------------|------|---------|
| `keyword` | string | `python developer` |
| `skills` | comma-string | `python,flask` |
| `location` | string | `bangalore` |
| `work_mode` | enum | `REMOTE\|HYBRID\|ONSITE` |
| `employment_type` | enum | `FULL_TIME\|PART_TIME\|INTERNSHIP\|CONTRACT` |
| `salary_min` | number | `10` |
| `salary_max` | number | `30` |
| `experience_min` | number | `2` |
| `experience_max` | number | `8` |
| `page` | int | `1` |
| `per_page` | int | `10` |

**Response 200**
```json
{
  "success": true,
  "data": {
    "items": [ {...}, {...} ],
    "page": 1, "per_page": 10, "total": 42, "total_pages": 5,
    "has_prev": false, "has_next": true
  }
}
```

---

### GET /api/jobs/:id

Get a single job by MongoDB `_id`.

**Response 200** — job object with `company_name` enriched.
**Error** — `JOB_NOT_FOUND` 404

---

### POST /api/jobs *(Recruiter)*

Create a job. Requires `recruiter_required`.

**Body** — same fields as the job form (title, description, location, work_mode, employment_type, skills, experience_min/max, salary_min/max, deadline).

**Response 201** — created job object.
**Errors** — `VALIDATION_ERROR` 422, `UNAUTHORIZED` 403

---

### PUT /api/jobs/:id *(Recruiter, owner only)*

Update a job. Same body as POST.

---

### DELETE /api/jobs/:id *(Recruiter, owner only)*

Delete a job permanently.

---

### POST /api/jobs/:id/apply *(Candidate)*

Apply to a job.

**Response 201**
```json
{ "success": true, "message": "Application submitted successfully.", "data": { "status": "APPLIED", ... } }
```

**Errors**
| Code | HTTP |
|------|------|
| `JOB_NOT_FOUND` | 404 |
| `JOB_CLOSED` | 400 |
| `DUPLICATE_APPLICATION` | 409 |

---

## Candidates

### GET /api/candidates/:id *(Login required)*

Get a candidate profile by profile `_id`. Candidates can only read their own profile; recruiters and admins can read any.

### PUT /api/candidates/:id *(Candidate, owner only)*

Update own profile. Allowed fields: `name`, `phone`, `location`, `skills`, `education`, `experience`, `expected_salary`, `notice_period`.

---

## Recruiters

### GET /api/recruiters/:id *(Login required)*

Get recruiter profile.

### PUT /api/recruiters/:id *(Recruiter, owner only)*

Update recruiter profile (`name`, `phone`).

---

## Applications

### GET /api/applications *(Login required)*

- Candidate → their own applications
- Recruiter / Admin → all applications

Query: `page`, `per_page`

### GET /api/applications/:id *(Login required, ownership enforced)*

Single application with enriched job title.

### PUT /api/applications/:id/status *(Recruiter, job owner)*

Update application status.

**Body**
```json
{ "status": "SHORTLISTED", "recruiter_notes": "Strong Python background." }
```

Valid status transitions:
```
APPLIED → UNDER_REVIEW → SHORTLISTED → INTERVIEW_SCHEDULED → SELECTED
                                     ↘ REJECTED
Any (except terminal) → WITHDRAWN (candidate via web)
```

**Errors** — `INVALID_APPLICATION_STATUS` 400, `UNAUTHORIZED` 403

---

## Interviews

### POST /api/interviews *(Recruiter)*

Schedule an interview.

**Body**
```json
{
  "application_id": "...",
  "date": "2027-06-15",
  "time": "10:00",
  "type": "ONLINE",
  "meeting_link": "https://meet.google.com/abc"
}
```

Types: `ONLINE`, `PHONE`, `IN_PERSON`

**Response 201** — interview object with status `SCHEDULED`.

---

### GET /api/interviews *(Login required)*

- Candidate → their own interviews
- Recruiter → interviews they scheduled

---

### PUT /api/interviews/:id *(Recruiter, owner only)*

Update interview. Updatable fields: `date`, `time`, `type`, `meeting_link`, `status`, `feedback`.

---

## Resumes

### POST /api/resumes *(Candidate)*

Upload resume. Multipart form with field `resume`.

Allowed: `.pdf`, `.doc`, `.docx` · Max: 5 MB

**Response 201** — resume metadata object.

---

### GET /api/resumes/:id *(Login required, ownership enforced)*

Get resume metadata (not the file; use web route for download).

---

### DELETE /api/resumes/:id *(Candidate, owner only)*

Delete resume and file from disk.

---

## Analytics

### GET /api/analytics/candidate *(Login required)*

Candidate stats: `total_applications`, `by_status`, `shortlisted`, `selected`, `interviews`.

### GET /api/analytics/recruiter *(Login required)*

Recruiter stats: `total_jobs`, `active_jobs`, `total_applications`, `shortlisted`, `selected`, `interviews`.

### GET /api/analytics/admin *(Admin only)*

Full platform analytics including chart-ready data arrays.

---

## Admin

### GET /api/admin/users *(Admin)*

Paginated user list. Query: `role`, `page`, `per_page`.

### PUT /api/admin/users/:id/activate *(Admin)*
### PUT /api/admin/users/:id/deactivate *(Admin)*

### PUT /api/admin/companies/:id/verify *(Admin)*

### GET /api/admin/audit-logs *(Admin)*

Query: `action`, `page`, `per_page`.

---

## HTTP Status Codes Used

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 400 | Bad request / business rule violation |
| 401 | Not authenticated |
| 403 | Forbidden / not authorised |
| 404 | Resource not found |
| 409 | Conflict (duplicate) |
| 422 | Validation error |
| 500 | Internal server error |
