"""
Seed HireHub with realistic fictional data.

Inserts:
  - 1 admin
  - 10 recruiters  (each with a company)
  - 5  companies   (used by the first 5 recruiters)
  - 20 candidates
  - 30 jobs
  - 50 applications
  - 15 interviews

Usage:
    python scripts/seed_data.py
    python scripts/seed_data.py --drop   # drops all collections first
"""
import os
import sys
import argparse
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB  = os.environ.get("MONGO_DATABASE", "hirehub")

client = MongoClient(MONGO_URI)
db     = client[MONGO_DB]

DEFAULT_PASSWORD = generate_password_hash("Password123")

# ── Seed data pools ────────────────────────────────────────────────────────────

COMPANIES = [
    {"name": "TechNova Solutions",  "industry": "Technology",  "location": "Bangalore", "size": "201-500", "website": "https://technova.example.com"},
    {"name": "DataBridge Analytics","industry": "Data Science","location": "Hyderabad","size": "51-200",  "website": "https://databridge.example.com"},
    {"name": "CloudForge Inc",       "industry": "Cloud",       "location": "Pune",      "size": "501-1000","website": "https://cloudforge.example.com"},
    {"name": "FinEdge Corp",         "industry": "Fintech",     "location": "Mumbai",    "size": "201-500", "website": "https://finedge.example.com"},
    {"name": "HealthStack Systems",  "industry": "Healthcare",  "location": "Chennai",   "size": "51-200",  "website": "https://healthstack.example.com"},
]

RECRUITER_NAMES = [
    ("Rahul Sharma",  "rahul.sharma@technova.example.com",   "9812300001"),
    ("Priya Mehta",   "priya.mehta@databridge.example.com",  "9812300002"),
    ("Karan Verma",   "karan.verma@cloudforge.example.com",  "9812300003"),
    ("Sneha Gupta",   "sneha.gupta@finedge.example.com",     "9812300004"),
    ("Arjun Nair",    "arjun.nair@healthstack.example.com",  "9812300005"),
    ("Divya Pillai",  "divya.pillai@technova.example.com",   "9812300006"),
    ("Rohit Joshi",   "rohit.joshi@databridge.example.com",  "9812300007"),
    ("Anjali Singh",  "anjali.singh@cloudforge.example.com", "9812300008"),
    ("Vikram Das",    "vikram.das@finedge.example.com",      "9812300009"),
    ("Meera Iyer",    "meera.iyer@healthstack.example.com",  "9812300010"),
]

CANDIDATE_NAMES = [
    ("Aditya Kumar",  "aditya.kumar@mail.example.com",  "9900000001", ["python", "django", "postgresql"], "Bangalore", 3),
    ("Riya Patel",    "riya.patel@mail.example.com",    "9900000002", ["react", "javascript", "css"],    "Mumbai",    2),
    ("Siddharth Roy", "sid.roy@mail.example.com",       "9900000003", ["java", "spring", "mysql"],       "Pune",      4),
    ("Kavya Reddy",   "kavya.reddy@mail.example.com",   "9900000004", ["machine learning", "python", "tensorflow"], "Hyderabad", 2),
    ("Nikhil Jain",   "nikhil.jain@mail.example.com",   "9900000005", ["golang", "docker", "kubernetes"],"Bangalore", 5),
    ("Pooja Nair",    "pooja.nair@mail.example.com",    "9900000006", ["data analysis", "sql", "tableau"],"Chennai",   1),
    ("Amit Yadav",    "amit.yadav@mail.example.com",    "9900000007", ["nodejs", "express", "mongodb"],  "Delhi",     3),
    ("Shreya Kapoor", "shreya.kapoor@mail.example.com", "9900000008", ["flutter", "dart", "firebase"],   "Bangalore", 2),
    ("Rahul Tiwari",  "rahul.tiwari@mail.example.com",  "9900000009", ["devops", "aws", "terraform"],    "Hyderabad", 6),
    ("Nisha Bhatt",   "nisha.bhatt@mail.example.com",   "9900000010", ["python", "flask", "redis"],      "Mumbai",    2),
    ("Aryan Malhotra","aryan.malhotra@mail.example.com","9900000011", ["c++", "algorithms", "system design"],"Pune", 4),
    ("Simran Kaur",   "simran.kaur@mail.example.com",   "9900000012", ["ui/ux", "figma", "adobe xd"],    "Delhi",     3),
    ("Rohan Desai",   "rohan.desai@mail.example.com",   "9900000013", ["python", "data science", "pandas"],"Bangalore",1),
    ("Ananya Sharma", "ananya.sharma@mail.example.com", "9900000014", ["java", "microservices", "kafka"],"Chennai",   5),
    ("Kunal Ghosh",   "kunal.ghosh@mail.example.com",   "9900000015", ["angular", "typescript", "rxjs"], "Kolkata",   3),
    ("Tanvi More",    "tanvi.more@mail.example.com",    "9900000016", ["sql", "oracle", "data warehouse"],"Mumbai",   7),
    ("Dhruv Singhania","dhruv.s@mail.example.com",      "9900000017", ["python", "nlp", "bert"],         "Bangalore", 3),
    ("Mansi Trivedi", "mansi.trivedi@mail.example.com", "9900000018", ["product management", "agile", "jira"],"Pune", 4),
    ("Yash Agarwal",  "yash.agarwal@mail.example.com",  "9900000019", ["rust", "webassembly", "c"],      "Hyderabad", 2),
    ("Prachi Verma",  "prachi.verma@mail.example.com",  "9900000020", ["salesforce", "apex", "soql"],    "Mumbai",    5),
]

JOB_TEMPLATES = [
    {"title": "Python Backend Developer",    "skills": ["python", "django", "postgresql"], "exp_min": 2, "exp_max": 5, "sal_min": 10, "sal_max": 20, "mode": "HYBRID",  "type": "FULL_TIME"},
    {"title": "React Frontend Engineer",     "skills": ["react", "javascript", "css"],    "exp_min": 1, "exp_max": 4, "sal_min": 8,  "sal_max": 18, "mode": "REMOTE",  "type": "FULL_TIME"},
    {"title": "Full Stack Java Developer",   "skills": ["java", "spring", "mysql"],       "exp_min": 3, "exp_max": 7, "sal_min": 12, "sal_max": 25, "mode": "ONSITE",  "type": "FULL_TIME"},
    {"title": "Data Scientist",              "skills": ["python", "machine learning", "tensorflow"], "exp_min": 2, "exp_max": 6, "sal_min": 14, "sal_max": 28, "mode": "HYBRID", "type": "FULL_TIME"},
    {"title": "DevOps Engineer",             "skills": ["devops", "aws", "terraform", "docker"],     "exp_min": 3, "exp_max": 8, "sal_min": 15, "sal_max": 30, "mode": "HYBRID", "type": "FULL_TIME"},
    {"title": "Node.js Developer",           "skills": ["nodejs", "express", "mongodb"], "exp_min": 1, "exp_max": 4, "sal_min": 8,  "sal_max": 18, "mode": "REMOTE",  "type": "FULL_TIME"},
    {"title": "Mobile Developer (Flutter)",  "skills": ["flutter", "dart", "firebase"],  "exp_min": 1, "exp_max": 3, "sal_min": 7,  "sal_max": 15, "mode": "HYBRID",  "type": "FULL_TIME"},
    {"title": "Cloud Architect",             "skills": ["aws", "kubernetes", "terraform"],"exp_min": 5, "exp_max": 12,"sal_min": 25, "sal_max": 50, "mode": "REMOTE",  "type": "FULL_TIME"},
    {"title": "Data Analyst",                "skills": ["sql", "tableau", "data analysis"],"exp_min":1, "exp_max": 4, "sal_min": 6,  "sal_max": 14, "mode": "ONSITE",  "type": "FULL_TIME"},
    {"title": "NLP Engineer",                "skills": ["python", "nlp", "bert"],         "exp_min": 2, "exp_max": 5, "sal_min": 12, "sal_max": 24, "mode": "HYBRID",  "type": "FULL_TIME"},
    {"title": "Frontend Intern",             "skills": ["html", "css", "javascript"],     "exp_min": 0, "exp_max": 1, "sal_min": 2,  "sal_max": 5,  "mode": "HYBRID",  "type": "INTERNSHIP"},
    {"title": "Machine Learning Intern",     "skills": ["python", "machine learning"],    "exp_min": 0, "exp_max": 1, "sal_min": 3,  "sal_max": 6,  "mode": "REMOTE",  "type": "INTERNSHIP"},
    {"title": "Backend Contract Developer",  "skills": ["python", "flask", "redis"],      "exp_min": 2, "exp_max": 6, "sal_min": 9,  "sal_max": 18, "mode": "REMOTE",  "type": "CONTRACT"},
    {"title": "Angular Developer",           "skills": ["angular", "typescript", "rxjs"], "exp_min": 2, "exp_max": 5, "sal_min": 10, "sal_max": 20, "mode": "HYBRID",  "type": "FULL_TIME"},
    {"title": "Database Administrator",      "skills": ["oracle", "sql", "data warehouse"],"exp_min":4, "exp_max": 10,"sal_min": 16, "sal_max": 32, "mode": "ONSITE",  "type": "FULL_TIME"},
    {"title": "Golang Backend Engineer",     "skills": ["golang", "docker", "microservices"],"exp_min":3,"exp_max": 7,"sal_min": 18, "sal_max": 35, "mode": "REMOTE",  "type": "FULL_TIME"},
    {"title": "UI/UX Designer",              "skills": ["figma", "ui/ux", "adobe xd"],    "exp_min": 2, "exp_max": 5, "sal_min": 8,  "sal_max": 18, "mode": "HYBRID",  "type": "FULL_TIME"},
    {"title": "Kafka Streaming Engineer",    "skills": ["kafka", "java", "microservices"],"exp_min": 3, "exp_max": 8, "sal_min": 18, "sal_max": 36, "mode": "HYBRID",  "type": "FULL_TIME"},
    {"title": "Product Manager",             "skills": ["product management", "agile", "jira"],"exp_min":4,"exp_max":10,"sal_min":20,"sal_max":40,"mode":"HYBRID","type":"FULL_TIME"},
    {"title": "Rust Systems Engineer",       "skills": ["rust", "webassembly", "c"],      "exp_min": 3, "exp_max": 8, "sal_min": 20, "sal_max": 40, "mode": "REMOTE",  "type": "FULL_TIME"},
    {"title": "Python Data Engineer",        "skills": ["python", "spark", "airflow"],    "exp_min": 2, "exp_max": 6, "sal_min": 12, "sal_max": 24, "mode": "HYBRID",  "type": "FULL_TIME"},
    {"title": "Site Reliability Engineer",   "skills": ["devops", "kubernetes", "prometheus"],"exp_min":4,"exp_max":10,"sal_min":22,"sal_max":45,"mode":"REMOTE","type":"FULL_TIME"},
    {"title": "Part-time QA Engineer",       "skills": ["selenium", "pytest", "testing"], "exp_min": 1, "exp_max": 4, "sal_min": 5,  "sal_max": 10, "mode": "REMOTE",  "type": "PART_TIME"},
    {"title": "Salesforce Developer",        "skills": ["salesforce", "apex", "soql"],    "exp_min": 2, "exp_max": 6, "sal_min": 12, "sal_max": 24, "mode": "HYBRID",  "type": "FULL_TIME"},
    {"title": "Computer Vision Engineer",    "skills": ["python", "opencv", "tensorflow"],"exp_min": 2, "exp_max": 6, "sal_min": 14, "sal_max": 28, "mode": "HYBRID",  "type": "FULL_TIME"},
    {"title": "iOS Developer",               "skills": ["swift", "ios", "xcode"],         "exp_min": 2, "exp_max": 6, "sal_min": 12, "sal_max": 25, "mode": "ONSITE",  "type": "FULL_TIME"},
    {"title": "Android Developer",           "skills": ["kotlin", "android", "jetpack"],  "exp_min": 1, "exp_max": 5, "sal_min": 10, "sal_max": 22, "mode": "HYBRID",  "type": "FULL_TIME"},
    {"title": "Cybersecurity Analyst",       "skills": ["security", "penetration testing", "siem"],"exp_min":3,"exp_max":8,"sal_min":18,"sal_max":35,"mode":"ONSITE","type":"FULL_TIME"},
    {"title": "Business Intelligence Dev",   "skills": ["power bi", "sql", "data warehouse"],"exp_min":2,"exp_max":6,"sal_min":10,"sal_max":20,"mode":"HYBRID","type":"FULL_TIME"},
    {"title": "Tech Lead – Python",          "skills": ["python", "django", "system design", "leadership"],"exp_min":6,"exp_max":12,"sal_min":30,"sal_max":55,"mode":"HYBRID","type":"FULL_TIME"},
]

LOCATIONS = ["Bangalore", "Mumbai", "Hyderabad", "Pune", "Chennai", "Delhi", "Kolkata"]


def _ts(days_ago: int = 0) -> datetime:
    return datetime.utcnow() - timedelta(days=days_ago)


def seed():
    print(f"Seeding database: {MONGO_DB} at {MONGO_URI}\n")

    # ── Admin ──────────────────────────────────────────────────────────────
    admin_id = db.users.insert_one({
        "name": "HireHub Admin",
        "email": "admin@hirehub.example.com",
        "phone": "9000000000",
        "password_hash": DEFAULT_PASSWORD,
        "role": "ADMIN",
        "is_active": True,
        "created_at": _ts(60),
        "updated_at": _ts(60),
    }).inserted_id
    print(f"✓  Admin created  (email: admin@hirehub.example.com  password: Password123)")

    # ── Companies + Recruiters ─────────────────────────────────────────────
    company_ids   = []
    recruiter_ids = []   # user _id list

    for i, (name, email, phone) in enumerate(RECRUITER_NAMES):
        # Create or reuse company (first 5 recruiters each get their own; next 5 share)
        if i < len(COMPANIES):
            co_data = COMPANIES[i]
            co_id = db.companies.insert_one({
                **co_data,
                "description": f"{co_data['name']} is a leading company in {co_data['industry']}.",
                "logo_url": "",
                "is_verified": random.choice([True, True, False]),
                "recruiter_id": None,   # patched below
                "created_at": _ts(50 - i),
                "updated_at": _ts(50 - i),
            }).inserted_id
            company_ids.append(co_id)
        else:
            co_id = company_ids[i % len(COMPANIES)]

        # User
        u_id = db.users.insert_one({
            "name": name,
            "email": email,
            "phone": phone,
            "password_hash": DEFAULT_PASSWORD,
            "role": "RECRUITER",
            "is_active": True,
            "created_at": _ts(50 - i),
            "updated_at": _ts(50 - i),
        }).inserted_id

        # Recruiter profile
        rec_id = db.recruiters.insert_one({
            "user_id": u_id,
            "name": name,
            "email": email,
            "phone": phone,
            "company_id": co_id,
            "created_at": _ts(50 - i),
            "updated_at": _ts(50 - i),
        }).inserted_id

        # Patch company with recruiter_id if it's new
        if i < len(COMPANIES):
            db.companies.update_one({"_id": co_id}, {"$set": {"recruiter_id": u_id}})

        recruiter_ids.append(u_id)

    print(f"✓  {len(RECRUITER_NAMES)} recruiters and {len(COMPANIES)} companies created")

    # ── Candidates ─────────────────────────────────────────────────────────
    candidate_profile_ids = []

    for i, (name, email, phone, skills, location, exp_yrs) in enumerate(CANDIDATE_NAMES):
        u_id = db.users.insert_one({
            "name": name,
            "email": email,
            "phone": phone,
            "password_hash": DEFAULT_PASSWORD,
            "role": "CANDIDATE",
            "is_active": True,
            "created_at": _ts(40 - i),
            "updated_at": _ts(40 - i),
        }).inserted_id

        cand_id = db.candidates.insert_one({
            "user_id": u_id,
            "name": name,
            "email": email,
            "phone": phone,
            "location": location,
            "skills": skills,
            "education": [{"degree": "B.Tech", "institution": "Sample University", "year": str(2018 + random.randint(0, 4))}],
            "experience": [{"title": "Software Engineer", "company": "Previous Corp", "years": exp_yrs, "description": "Worked on backend/frontend systems."}],
            "expected_salary": random.randint(8, 30),
            "notice_period": random.choice(["Immediate", "15 days", "30 days", "60 days"]),
            "resume_id": None,
            "saved_jobs": [],
            "created_at": _ts(40 - i),
            "updated_at": _ts(40 - i),
        }).inserted_id

        candidate_profile_ids.append(cand_id)

        # Seed welcome notification
        db.notifications.insert_one({
            "user_id": u_id,
            "title": "Welcome to HireHub!",
            "message": f"Hi {name}, your account has been created successfully.",
            "type": "REGISTRATION",
            "resource_id": None,
            "is_read": random.choice([True, False]),
            "created_at": _ts(40 - i),
        })

    print(f"✓  {len(CANDIDATE_NAMES)} candidates created")

    # ── Jobs ───────────────────────────────────────────────────────────────
    job_ids = []
    for i, jt in enumerate(JOB_TEMPLATES):
        recruiter_user_id = recruiter_ids[i % len(recruiter_ids)]
        recruiter_doc     = db.recruiters.find_one({"user_id": recruiter_user_id})
        company_id        = recruiter_doc["company_id"] if recruiter_doc else company_ids[0]
        company_doc       = db.companies.find_one({"_id": company_id})
        location          = company_doc["location"] if company_doc else random.choice(LOCATIONS)

        posted = _ts(random.randint(1, 30))
        deadline = posted + timedelta(days=random.randint(20, 60))
        status = "OPEN" if random.random() > 0.15 else "CLOSED"

        job_id = db.jobs.insert_one({
            "company_id":      company_id,
            "recruiter_id":    recruiter_user_id,
            "title":           jt["title"],
            "description":     f"We are looking for a skilled {jt['title']} to join our team. "
                               f"You will work on cutting-edge projects using {', '.join(jt['skills'][:3])}.",
            "skills":          jt["skills"],
            "experience_min":  jt["exp_min"],
            "experience_max":  jt["exp_max"],
            "location":        location,
            "work_mode":       jt["mode"],
            "employment_type": jt["type"],
            "salary_min":      jt["sal_min"],
            "salary_max":      jt["sal_max"],
            "posted_date":     posted,
            "deadline":        deadline,
            "status":          status,
            "created_at":      posted,
            "updated_at":      posted,
        }).inserted_id
        job_ids.append(job_id)

    print(f"✓  {len(JOB_TEMPLATES)} jobs created")

    # ── Applications ───────────────────────────────────────────────────────
    open_job_ids = [j for j in job_ids if db.jobs.find_one({"_id": j, "status": "OPEN"})]
    app_ids      = []
    app_pairs    = set()   # (candidate_id, job_id) dedup
    attempts     = 0

    while len(app_ids) < 50 and attempts < 500:
        attempts += 1
        cand_prof = random.choice(candidate_profile_ids)
        job_id    = random.choice(open_job_ids)
        pair      = (str(cand_prof), str(job_id))
        if pair in app_pairs:
            continue
        app_pairs.add(pair)

        status = random.choices(
            ["APPLIED", "UNDER_REVIEW", "SHORTLISTED", "INTERVIEW_SCHEDULED", "SELECTED", "REJECTED"],
            weights=[30, 20, 20, 15, 5, 10],
        )[0]

        applied_at = _ts(random.randint(1, 25))
        app_id = db.applications.insert_one({
            "candidate_id":  cand_prof,
            "job_id":        job_id,
            "status":        status,
            "applied_at":    applied_at,
            "updated_at":    applied_at + timedelta(days=random.randint(0, 5)),
            "recruiter_notes": "Looks promising." if status in ("SHORTLISTED", "SELECTED") else "",
            "interview_id":  None,
        }).inserted_id
        app_ids.append((app_id, cand_prof, job_id, status))

        # Application notification to candidate
        cand_doc = db.candidates.find_one({"_id": cand_prof})
        job_doc  = db.jobs.find_one({"_id": job_id})
        if cand_doc and job_doc:
            cand_user = db.users.find_one({"_id": cand_doc["user_id"]})
            if cand_user:
                db.notifications.insert_one({
                    "user_id":     cand_user["_id"],
                    "title":       "Application Submitted",
                    "message":     f"Your application for '{job_doc['title']}' has been submitted.",
                    "type":        "APPLICATION_SUBMITTED",
                    "resource_id": app_id,
                    "is_read":     random.choice([True, False]),
                    "created_at":  applied_at,
                })

    print(f"✓  {len(app_ids)} applications created")

    # ── Interviews ─────────────────────────────────────────────────────────
    shortlisted_apps = [(a, c, j, s) for a, c, j, s in app_ids
                        if s in ("SHORTLISTED", "INTERVIEW_SCHEDULED", "SELECTED")]
    interview_apps   = random.sample(shortlisted_apps, min(15, len(shortlisted_apps)))
    interview_count  = 0

    for app_id, cand_prof, job_id, _ in interview_apps:
        job_doc      = db.jobs.find_one({"_id": job_id})
        recruiter_uid = job_doc["recruiter_id"] if job_doc else recruiter_ids[0]
        iv_date      = datetime.utcnow() + timedelta(days=random.randint(3, 30))
        iv_type      = random.choice(["ONLINE", "PHONE", "IN_PERSON"])
        iv_status    = random.choice(["SCHEDULED", "SCHEDULED", "COMPLETED"])

        iv_id = db.interviews.insert_one({
            "application_id": app_id,
            "candidate_id":   cand_prof,
            "recruiter_id":   recruiter_uid,
            "date":           iv_date.strftime("%Y-%m-%d"),
            "time":           f"{random.randint(9,17):02d}:00",
            "type":           iv_type,
            "meeting_link":   "https://meet.google.com/seed-link" if iv_type == "ONLINE" else "",
            "status":         iv_status,
            "feedback":       "Good technical skills." if iv_status == "COMPLETED" else "",
            "created_at":     _ts(random.randint(1, 10)),
            "updated_at":     _ts(random.randint(0, 5)),
        }).inserted_id

        # Update application with interview reference
        db.applications.update_one({"_id": app_id}, {
            "$set": {"interview_id": iv_id, "status": "INTERVIEW_SCHEDULED"}
        })
        interview_count += 1

    print(f"✓  {interview_count} interviews created")

    # ── Audit log entries ──────────────────────────────────────────────────
    db.audit_logs.insert_one({
        "user_id":     admin_id,
        "action":      "USER_REGISTERED",
        "resource":    "users",
        "resource_id": admin_id,
        "metadata":    {"role": "ADMIN"},
        "timestamp":   _ts(60),
    })
    print("✓  Sample audit log entry created")

    print(f"\nSeed complete. Login credentials for all seeded users: Password123")
    print(f"  Admin    : admin@hirehub.example.com")
    print(f"  Recruiter: {RECRUITER_NAMES[0][1]}")
    print(f"  Candidate: {CANDIDATE_NAMES[0][1]}")
    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed HireHub database")
    parser.add_argument("--drop", action="store_true", help="Drop all collections before seeding")
    args = parser.parse_args()

    if args.drop:
        for col in db.list_collection_names():
            db.drop_collection(col)
        print("All collections dropped.\n")

    seed()
