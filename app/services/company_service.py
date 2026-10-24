"""
Company service — company profile management.
"""
from app.repositories.company_repository import CompanyRepository
from app.utils.helpers import serialize_doc
from app.exceptions.app_exceptions import CompanyNotFoundError, UnauthorizedError


class CompanyService:
    """Business logic for company profiles."""

    def __init__(self) -> None:
        self._companies = CompanyRepository()

    def get_company(self, company_id: str) -> dict:
        doc = self._companies.find_by_id(company_id)
        if not doc:
            raise CompanyNotFoundError()
        return serialize_doc(doc)

    def get_company_by_recruiter(self, recruiter_user_id: str) -> dict:
        doc = self._companies.find_by_recruiter_id(recruiter_user_id)
        if not doc:
            raise CompanyNotFoundError()
        return serialize_doc(doc)

    def update_company(self, company_id: str, recruiter_user_id: str, data: dict) -> dict:
        doc = self._companies.find_by_id(company_id)
        if not doc:
            raise CompanyNotFoundError()
        if str(doc.get("recruiter_id")) != str(recruiter_user_id):
            raise UnauthorizedError()

        allowed = ["name", "description", "website", "location", "industry", "size", "logo_url"]
        update = {k: v for k, v in data.items() if k in allowed}
        self._companies.update_by_id(company_id, update)
        return self.get_company(company_id)

    def verify_company(self, company_id: str) -> dict:
        doc = self._companies.find_by_id(company_id)
        if not doc:
            raise CompanyNotFoundError()
        self._companies.set_verified(company_id, True)
        return self.get_company(company_id)

    def list_all(self, page: int = 1, per_page: int = 20) -> dict:
        result = self._companies.find_all(page=page, per_page=per_page)
        result["items"] = [serialize_doc(c) for c in result["items"]]
        return result
