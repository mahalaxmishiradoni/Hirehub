"""
Tests for the rule-based MatchingService.
"""
import pytest
from app.services.matching_service import MatchingService


CANDIDATE_FULL = {
    "skills": ["python", "sql", "mongodb", "flask"],
    "experience": [{"years": 3}],
    "location": "bangalore",
    "expected_salary": 15.0,
}

CANDIDATE_PARTIAL = {
    "skills": ["python", "sql"],
    "experience": [{"years": 1}],
    "location": "mumbai",
    "expected_salary": 25.0,
}

CANDIDATE_EMPTY = {
    "skills": [],
    "experience": [],
    "location": "",
    "expected_salary": None,
}

JOB = {
    "skills": ["python", "sql", "mongodb", "aws"],
    "experience_min": 2,
    "experience_max": 6,
    "location": "bangalore",
    "work_mode": "HYBRID",
    "salary_min": 10.0,
    "salary_max": 25.0,
}

JOB_NO_SKILLS = {
    "skills": [],
    "experience_min": 0,
    "experience_max": 10,
    "location": "remote",
    "work_mode": "REMOTE",
    "salary_min": 0,
    "salary_max": 0,
}


class TestMatchScore:
    def test_full_match_scores_high(self):
        result = MatchingService.calculate_match(CANDIDATE_FULL, JOB)
        assert result["score"] >= 70
        assert "python" in result["matched_skills"]
        assert "aws" in result["missing_skills"]

    def test_partial_match_scores_lower(self):
        result = MatchingService.calculate_match(CANDIDATE_PARTIAL, JOB)
        full_result = MatchingService.calculate_match(CANDIDATE_FULL, JOB)
        assert result["score"] < full_result["score"]

    def test_empty_candidate_has_low_skill_score(self):
        result = MatchingService.calculate_match(CANDIDATE_EMPTY, JOB)
        assert result["breakdown"]["skills"]["score"] == 0
        assert result["score"] >= 0  # non-negative

    def test_job_no_skills_gives_full_skill_score(self):
        result = MatchingService.calculate_match(CANDIDATE_FULL, JOB_NO_SKILLS)
        assert result["breakdown"]["skills"]["score"] == MatchingService.WEIGHT_SKILLS

    def test_matched_skills_correct(self):
        result = MatchingService.calculate_match(CANDIDATE_FULL, JOB)
        matched = set(result["matched_skills"])
        assert matched == {"python", "sql", "mongodb"}

    def test_missing_skills_correct(self):
        result = MatchingService.calculate_match(CANDIDATE_FULL, JOB)
        missing = set(result["missing_skills"])
        assert missing == {"aws"}

    def test_remote_job_gives_full_location_score(self):
        result = MatchingService.calculate_match(CANDIDATE_PARTIAL, JOB_NO_SKILLS)
        assert result["breakdown"]["location"]["score"] == MatchingService.WEIGHT_LOCATION

    def test_location_mismatch_scores_zero(self):
        result = MatchingService.calculate_match(CANDIDATE_PARTIAL, JOB)
        assert result["breakdown"]["location"]["score"] == 0

    def test_score_capped_at_100(self):
        result = MatchingService.calculate_match(CANDIDATE_FULL, JOB)
        assert result["score"] <= 100

    def test_score_non_negative(self):
        result = MatchingService.calculate_match(CANDIDATE_EMPTY, JOB)
        assert result["score"] >= 0

    def test_experience_below_minimum_penalised(self):
        low_exp = {**CANDIDATE_EMPTY, "skills": [], "experience": [{"years": 0}]}
        result = MatchingService.calculate_match(low_exp, JOB)
        assert result["breakdown"]["experience"]["score"] == 0

    def test_salary_within_range_full_marks(self):
        result = MatchingService.calculate_match(CANDIDATE_FULL, JOB)
        assert result["breakdown"]["salary"]["score"] == MatchingService.WEIGHT_SALARY

    def test_salary_outside_range_zero(self):
        expensive = {**CANDIDATE_FULL, "expected_salary": 100.0}
        result = MatchingService.calculate_match(expensive, JOB)
        assert result["breakdown"]["salary"]["score"] == 0


class TestRankJobs:
    def test_rank_jobs_sorted_descending(self):
        jobs = [JOB, JOB_NO_SKILLS]
        ranked = MatchingService.rank_jobs(CANDIDATE_FULL, jobs)
        assert ranked[0]["match_score"] >= ranked[1]["match_score"]

    def test_rank_jobs_adds_match_score_field(self):
        ranked = MatchingService.rank_jobs(CANDIDATE_FULL, [JOB])
        assert "match_score" in ranked[0]
        assert "matched_skills" in ranked[0]
        assert "missing_skills" in ranked[0]

    def test_rank_empty_jobs_list(self):
        ranked = MatchingService.rank_jobs(CANDIDATE_FULL, [])
        assert ranked == []
