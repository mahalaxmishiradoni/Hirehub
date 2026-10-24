"""
Rule-based job matching service.
Calculates a match score between a candidate profile and a job.
"""
from typing import List


class MatchingService:
    """
    Computes match scores between candidates and jobs using weighted rules.
    Does not use machine learning.
    """

    # Scoring weights (must sum to 100)
    WEIGHT_SKILLS = 50
    WEIGHT_EXPERIENCE = 20
    WEIGHT_LOCATION = 15
    WEIGHT_SALARY = 10
    WEIGHT_WORK_MODE = 5

    @staticmethod
    def calculate_match(candidate: dict, job: dict) -> dict:
        """
        Return a dict with overall score and breakdowns.

        Parameters
        ----------
        candidate : dict
            Candidate profile document (from MongoDB / serialised).
        job : dict
            Job document (from MongoDB / serialised).
        """
        score = 0
        breakdown = {}

        # --- Skills ---
        candidate_skills = {s.lower().strip() for s in candidate.get("skills", [])}
        job_skills = {s.lower().strip() for s in job.get("skills", [])}

        if job_skills:
            matched = candidate_skills & job_skills
            missing = job_skills - candidate_skills
            skill_score = int((len(matched) / len(job_skills)) * MatchingService.WEIGHT_SKILLS)
        else:
            matched = set()
            missing = set()
            skill_score = MatchingService.WEIGHT_SKILLS  # No skills required → full marks

        score += skill_score
        breakdown["skills"] = {
            "score": skill_score,
            "max": MatchingService.WEIGHT_SKILLS,
            "matched": sorted(matched),
            "missing": sorted(missing),
        }

        # --- Experience ---
        candidate_exp = 0
        for exp in candidate.get("experience", []):
            try:
                candidate_exp += int(exp.get("years", 0))
            except (ValueError, TypeError):
                pass

        exp_min = int(job.get("experience_min", 0))
        exp_max = int(job.get("experience_max", 0)) or 99

        if candidate_exp >= exp_min:
            exp_score = MatchingService.WEIGHT_EXPERIENCE
        elif exp_min > 0:
            exp_score = int((candidate_exp / exp_min) * MatchingService.WEIGHT_EXPERIENCE)
        else:
            exp_score = MatchingService.WEIGHT_EXPERIENCE

        score += exp_score
        breakdown["experience"] = {
            "score": exp_score,
            "max": MatchingService.WEIGHT_EXPERIENCE,
            "candidate_years": candidate_exp,
            "required_min": exp_min,
            "required_max": exp_max,
        }

        # --- Location ---
        c_loc = (candidate.get("location") or "").lower().strip()
        j_loc = (job.get("location") or "").lower().strip()
        job_mode = (job.get("work_mode") or "").upper()

        if job_mode == "REMOTE":
            loc_score = MatchingService.WEIGHT_LOCATION
        elif c_loc and j_loc and (c_loc in j_loc or j_loc in c_loc):
            loc_score = MatchingService.WEIGHT_LOCATION
        else:
            loc_score = 0

        score += loc_score
        breakdown["location"] = {"score": loc_score, "max": MatchingService.WEIGHT_LOCATION}

        # --- Salary ---
        expected = candidate.get("expected_salary")
        sal_min = job.get("salary_min", 0)
        sal_max = job.get("salary_max", 0)

        if expected is None or sal_max == 0:
            sal_score = MatchingService.WEIGHT_SALARY  # Unknown → full marks
        elif sal_min <= float(expected) <= sal_max:
            sal_score = MatchingService.WEIGHT_SALARY
        else:
            sal_score = 0

        score += sal_score
        breakdown["salary"] = {"score": sal_score, "max": MatchingService.WEIGHT_SALARY}

        # --- Work Mode Preference ---
        # We don't store candidate work mode preference explicitly; default full marks
        wm_score = MatchingService.WEIGHT_WORK_MODE
        score += wm_score
        breakdown["work_mode"] = {"score": wm_score, "max": MatchingService.WEIGHT_WORK_MODE}

        return {
            "score": min(score, 100),
            "breakdown": breakdown,
            "matched_skills": sorted(matched),
            "missing_skills": sorted(missing),
        }

    @staticmethod
    def rank_jobs(candidate: dict, jobs: List[dict]) -> List[dict]:
        """Return jobs sorted by match score descending."""
        scored = []
        for job in jobs:
            match = MatchingService.calculate_match(candidate, job)
            job_copy = dict(job)
            job_copy["match_score"] = match["score"]
            job_copy["matched_skills"] = match["matched_skills"]
            job_copy["missing_skills"] = match["missing_skills"]
            scored.append(job_copy)
        scored.sort(key=lambda x: x["match_score"], reverse=True)
        return scored
