"""
Unit tests for candidate profile normalisation.

These tests exercise _normalise_list_of_dicts and _normalise_profile
directly — no Flask app context or MongoDB connection required.

Run with:
    python -m pytest tests/test_profile_normalisation.py -v
"""
import pytest
from app.services.candidate_service import _normalise_list_of_dicts, _normalise_profile


# ─── _normalise_list_of_dicts ──────────────────────────────────────────────────

class TestNormaliseListOfDicts:
    """Each element of the list must become a dict after normalisation."""

    def test_all_dicts_unchanged(self):
        """Well-formed input passes through unmodified."""
        inp = [
            {"title": "Software Engineer", "company": "Acme", "years": 3},
            {"title": "Lead Developer", "company": "Beta Corp", "years": 2},
        ]
        assert _normalise_list_of_dicts(inp) == inp

    def test_plain_string_wrapped_in_dict(self):
        """A bare string becomes {"value": <string>}."""
        result = _normalise_list_of_dicts(["3 years backend experience"])
        assert result == [{"value": "3 years backend experience"}]

    def test_mixed_list_preserves_dicts_and_wraps_strings(self):
        """Mixed input: dicts kept, strings wrapped, Nones dropped."""
        inp = [
            {"title": "SWE"},
            "some plain string",
            None,
            {"title": "Lead"},
        ]
        result = _normalise_list_of_dicts(inp)
        assert len(result) == 3
        assert result[0] == {"title": "SWE"}
        assert result[1] == {"value": "some plain string"}
        assert result[2] == {"title": "Lead"}

    def test_empty_list_returns_empty_list(self):
        assert _normalise_list_of_dicts([]) == []

    def test_none_items_dropped(self):
        result = _normalise_list_of_dicts([None, None])
        assert result == []

    def test_empty_string_dropped(self):
        result = _normalise_list_of_dicts(["", "   "])
        assert result == []

    def test_whitespace_only_string_dropped(self):
        result = _normalise_list_of_dicts(["   "])
        assert result == []

    def test_string_is_stripped_before_wrapping(self):
        result = _normalise_list_of_dicts(["  python developer  "])
        assert result == [{"value": "python developer"}]

    def test_integer_items_dropped(self):
        """Non-str, non-dict, non-None values are silently dropped."""
        result = _normalise_list_of_dicts([42, {"title": "OK"}, 3.14])
        assert result == [{"title": "OK"}]

    def test_list_of_all_bad_values_returns_empty(self):
        result = _normalise_list_of_dicts([None, "", 0, False])
        assert result == []


# ─── _normalise_profile ────────────────────────────────────────────────────────

class TestNormaliseProfile:
    """_normalise_profile coerces experience, education, and skills in-place."""

    def test_well_formed_profile_unchanged(self):
        profile = {
            "experience": [{"title": "Dev", "company": "Acme", "years": 2}],
            "education":  [{"degree": "B.Tech", "institution": "IIT", "year": "2020"}],
            "skills":     ["python", "flask"],
        }
        result = _normalise_profile(dict(profile))  # copy so original is unaffected
        assert result["experience"] == profile["experience"]
        assert result["education"]  == profile["education"]
        assert result["skills"]     == profile["skills"]

    def test_experience_string_entries_wrapped(self):
        profile = {"experience": ["3 years at Acme"], "education": [], "skills": []}
        result = _normalise_profile(profile)
        assert result["experience"] == [{"value": "3 years at Acme"}]

    def test_education_string_entries_wrapped(self):
        profile = {"experience": [], "education": ["B.Tech CSE 2020"], "skills": []}
        result = _normalise_profile(profile)
        assert result["education"] == [{"value": "B.Tech CSE 2020"}]

    def test_none_experience_becomes_empty_list(self):
        profile = {"experience": None, "education": None, "skills": []}
        result = _normalise_profile(profile)
        assert result["experience"] == []
        assert result["education"]  == []

    def test_none_skills_becomes_empty_list(self):
        profile = {"experience": [], "education": [], "skills": None}
        result = _normalise_profile(profile)
        assert result["skills"] == []

    def test_skills_non_list_becomes_empty_list(self):
        """A string stored in skills (wrong type) is coerced to []."""
        profile = {"experience": [], "education": [], "skills": "python,sql"}
        result = _normalise_profile(profile)
        assert result["skills"] == []

    def test_mixed_experience_list(self):
        profile = {
            "experience": [
                {"title": "Dev", "company": "X", "years": 1},
                "freelance work",
                None,
            ],
            "education": [],
            "skills": [],
        }
        result = _normalise_profile(profile)
        assert len(result["experience"]) == 2
        assert result["experience"][0] == {"title": "Dev", "company": "X", "years": 1}
        assert result["experience"][1] == {"value": "freelance work"}

    def test_empty_profile_all_fields(self):
        profile = {"experience": [], "education": [], "skills": []}
        result = _normalise_profile(profile)
        assert result == {"experience": [], "education": [], "skills": []}

    def test_missing_keys_not_created(self):
        """_normalise_profile should not add keys that do not exist in the profile."""
        profile = {}
        result = _normalise_profile(profile)
        # experience and education default to [] because raw is None
        assert result.get("experience") == []
        assert result.get("education")  == []
        # skills: None → []
        assert result.get("skills") == []

    def test_returns_same_dict_object(self):
        """Mutation is in-place; the same dict is returned."""
        profile = {"experience": [], "education": [], "skills": []}
        result = _normalise_profile(profile)
        assert result is profile


# ─── Integration-style: simulate the full read path ───────────────────────────

class TestNormalisationEndToEnd:
    """
    Simulates what happens when a bad document is read from MongoDB,
    run through serialize_doc, and then _normalise_profile.
    """

    def test_string_experience_does_not_crash_template_access(self):
        """
        After normalisation every item must support .get() — the operation
        the template performs.  If any item is still a string, dict.get()
        would raise AttributeError in Python (UndefinedError in Jinja2).
        """
        raw_from_db = {
            "name": "Alice",
            "email": "alice@example.com",
            "phone": "9876543210",
            "location": "Bangalore",
            "skills": ["python"],
            "experience": ["3 years", {"title": "Dev", "company": "Acme", "years": 2}],
            "education": ["B.Tech 2020", {"degree": "M.Tech", "institution": "NIT", "year": "2022"}],
            "expected_salary": 15,
            "notice_period": "30 days",
            "resume_id": None,
            "saved_jobs": [],
        }
        profile = _normalise_profile(dict(raw_from_db))

        # Every experience item must respond to .get() without raising
        for exp in profile["experience"]:
            assert isinstance(exp, dict), f"Expected dict, got {type(exp)}: {exp!r}"
            _ = exp.get("title", exp.get("value", ""))  # template expression

        # Every education item must respond to .get() without raising
        for edu in profile["education"]:
            assert isinstance(edu, dict), f"Expected dict, got {type(edu)}: {edu!r}"
            _ = edu.get("degree", edu.get("value", ""))  # template expression

    def test_empty_profile_renders_without_error(self):
        """A brand-new candidate with no experience or education is safe."""
        raw_from_db = {
            "name": "Bob",
            "email": "bob@example.com",
            "phone": "",
            "location": "",
            "skills": [],
            "experience": [],
            "education": [],
            "expected_salary": None,
            "notice_period": None,
            "resume_id": None,
            "saved_jobs": [],
        }
        profile = _normalise_profile(dict(raw_from_db))
        assert profile["experience"] == []
        assert profile["education"]  == []
        assert profile["skills"]     == []

    def test_fully_populated_profile_unchanged(self):
        """A correctly structured profile is not mutated."""
        raw_from_db = {
            "experience": [
                {"title": "Backend Dev", "company": "TechCorp", "years": 3, "description": "Flask APIs"},
                {"title": "Intern",      "company": "StartupX",  "years": 1, "description": ""},
            ],
            "education": [
                {"degree": "B.Tech CSE", "institution": "IIT Delhi",  "year": "2019"},
                {"degree": "M.Tech",     "institution": "IIT Bombay", "year": "2021"},
            ],
            "skills": ["python", "django", "postgresql"],
        }
        original_exp = list(raw_from_db["experience"])
        original_edu = list(raw_from_db["education"])

        profile = _normalise_profile(dict(raw_from_db))
        assert profile["experience"] == original_exp
        assert profile["education"]  == original_edu
