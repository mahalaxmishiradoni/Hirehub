# HireHub — Database Reference

Database: **MongoDB**  
Default database name: `hirehub`  
Test database name: `hirehub_test`

---

## Collections

### users

Every registered user regardless of role.

| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | Auto-generated |
| `name` | string | |
| `email` | string | Unique, lowercase |
| `phone` | string | |
| `password_hash` | string | Werkzeug PBKDF2-SHA256 — never plain text |
| `role` | string | `CANDIDATE`, `RECRUITER`, `ADMIN` |
| `is_active` | bool | `false` = deactivated by admin |
| `created_at` | datetime | UTC |
| `updated_at` | datetime | UTC |

**Indexes:** `email` (unique), `role`, `is_active`

---

### candidates

One document per candidate — extended profile.

| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | |
| `user_id` | ObjectId | FK → users |
| `name` | string | Denormalised for fast reads |
| `email` | string | |
| `phone` | string | |
| `location` | string | |
| `skills` | array[string] | Lowercase |
| `education` | array[object] | `{degree, institution, year}` |
| `experience` | array[object] | `{title, company, years, description}` |
| `expected_salary` | number | LPA |
| `notice_period` | string | e.g. `"30 days"` |
| `resume_id` | ObjectId\|null | FK → resumes |
| `saved_jobs` | array[ObjectId] | FK → jobs |
| `created_at` | datetime | |
| `updated_at` | datetime | |

**Indexes:** `user_id` (unique), `skills`, `location`

---

### recruiters

| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | |
| `user_id` | ObjectId | FK → users (unique) |
| `name` | string | |
| `email` | string | |
| `phone` | string | |
| `company_id` | ObjectId | FK → companies |
| `created_at` | datetime | |
| `updated_at` | datetime | |

**Indexes:** `user_id` (unique), `company_id`

---

### companies

| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | |
| `name` | string | |
| `description` | string | |
| `website` | string | |
| `location` | string | |
| `industry` | string | |
| `size` | string | e.g. `"51-200"` |
| `logo_url` | string | |
| `is_verified` | bool | Set by admin |
| `recruiter_id` | ObjectId | Primary recruiter |
| `created_at` | datetime | |
| `updated_at` | datetime | |

**Indexes:** `name`, `is_verified`

---

### jobs

| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | |
| `company_id` | ObjectId | FK → companies |
| `recruiter_id` | ObjectId | FK → users |
| `title` | string | |
| `description` | string | |
| `skills` | array[string] | Lowercase |
| `experience_min` | int | Years |
| `experience_max` | int | Years |
| `location` | string | |
| `work_mode` | string | `REMOTE`, `HYBRID`, `ONSITE` |
| `employment_type` | string | `FULL_TIME`, `PART_TIME`, `INTERNSHIP`, `CONTRACT` |
| `salary_min` | float | LPA |
| `salary_max` | float | LPA |
| `posted_date` | datetime | |
| `deadline` | datetime\|null | |
| `status` | string | `OPEN`, `CLOSED`, `EXPIRED` |
| `created_at` | datetime | |
| `updated_at` | datetime | |

**Indexes:** text index on `title`+`description`, `skills`, `location`, `status`, `recruiter_id`, `company_id`, `posted_date` (desc), `work_mode`, `employment_type`

---

### applications

| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | |
| `candidate_id` | ObjectId | FK → candidates |
| `job_id` | ObjectId | FK → jobs |
| `status` | string | See workflow below |
| `applied_at` | datetime | |
| `updated_at` | datetime | |
| `recruiter_notes` | string | |
| `interview_id` | ObjectId\|null | FK → interviews |

**Status workflow:**
```
APPLIED → UNDER_REVIEW → SHORTLISTED → INTERVIEW_SCHEDULED → SELECTED
                                     ↘ REJECTED
Any active → WITHDRAWN
```

**Indexes:** `(candidate_id, job_id)` unique compound, `candidate_id`, `job_id`, `status`, `applied_at` (desc)

---

### interviews

| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | |
| `application_id` | ObjectId | FK → applications |
| `candidate_id` | ObjectId | FK → candidates |
| `recruiter_id` | ObjectId | FK → users |
| `date` | string | `YYYY-MM-DD` |
| `time` | string | `HH:MM` |
| `type` | string | `ONLINE`, `PHONE`, `IN_PERSON` |
| `meeting_link` | string | |
| `status` | string | `SCHEDULED`, `COMPLETED`, `CANCELLED` |
| `feedback` | string | Recruiter's post-interview notes |
| `created_at` | datetime | |
| `updated_at` | datetime | |

**Indexes:** `application_id`, `candidate_id`, `recruiter_id`, `date`

---

### resumes

| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | |
| `candidate_id` | ObjectId | FK → candidates |
| `original_filename` | string | User-provided name (display only) |
| `stored_filename` | string | UUID-based, safe for filesystem |
| `file_size` | int | Bytes |
| `uploaded_at` | datetime | |

**Indexes:** `candidate_id`

---

### notifications

| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | |
| `user_id` | ObjectId | FK → users |
| `title` | string | |
| `message` | string | |
| `type` | string | e.g. `APPLICATION_SUBMITTED` |
| `resource_id` | ObjectId\|null | Related document |
| `is_read` | bool | |
| `created_at` | datetime | |

**Indexes:** `user_id`, `is_read`, `created_at` (desc)

---

### audit_logs

| Field | Type | Notes |
|-------|------|-------|
| `_id` | ObjectId | |
| `user_id` | ObjectId | Who performed the action |
| `action` | string | See action constants |
| `resource` | string | Collection name |
| `resource_id` | ObjectId\|null | Affected document |
| `metadata` | object | Extra context — never contains passwords |
| `timestamp` | datetime | UTC |

**Action constants:** `USER_REGISTERED`, `USER_LOGIN`, `USER_LOGOUT`, `JOB_CREATED`, `JOB_UPDATED`, `JOB_CLOSED`, `APPLICATION_SUBMITTED`, `APPLICATION_SHORTLISTED`, `APPLICATION_REJECTED`, `INTERVIEW_SCHEDULED`, `RESUME_UPLOADED`, `USER_DEACTIVATED`

**Indexes:** `user_id`, `action`, `timestamp` (desc)

---

## Aggregation Pipelines Used

| Service method | Pipeline purpose |
|----------------|-----------------|
| `jobs_by_skill` | `$unwind skills → $group → $sort` |
| `jobs_by_location` | `$group by location → $sort` |
| `applications_by_status` | `$group by status → $sort` |
| `applications_by_job` | `$group → $lookup jobs → $project` |
| `monthly_applications` | `$match year → $group by $month` |
| `monthly_registrations` | `$match year → $group by month + role` |
| `applications_by_company` | `$lookup jobs → $lookup companies → $group` |
| `recruiter_stats` | Multiple `count_documents` calls |
| `candidate_stats` | `$match → $group by status` |
| `admin_overview` | Multiple `count_documents` calls |

---

## Indexing Strategy

- Unique compound index on `(candidate_id, job_id)` in `applications` prevents duplicate submissions at the database level.
- Text index on `jobs.title + jobs.description` enables full-text keyword search.
- `skills` array index supports `$elemMatch` skill filtering queries.
- All foreign-key fields are indexed to keep lookup times O(log n).
