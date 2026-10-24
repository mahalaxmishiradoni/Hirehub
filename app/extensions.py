"""
Flask extensions and MongoDB connection management.
"""
from pymongo import MongoClient
from pymongo.database import Database
from flask import Flask, current_app
from typing import Optional


class MongoDB:
    """MongoDB connection manager using PyMongo."""

    def __init__(self) -> None:
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None

    def init_app(self, app: Flask) -> None:
        """Initialize MongoDB with Flask app."""
        uri = app.config["MONGO_URI"]
        db_name = app.config["MONGO_DATABASE"]
        self._client = MongoClient(uri)
        self._db = self._client[db_name]
        app.extensions["mongodb"] = self

        @app.teardown_appcontext
        def close_connection(exception):  # noqa
            pass  # MongoClient handles pooling; no per-request teardown needed

    @property
    def db(self) -> Database:
        """Return the database instance."""
        if self._db is None:
            raise RuntimeError("MongoDB not initialised. Call init_app() first.")
        return self._db

    def get_collection(self, name: str):
        """Return a collection by name."""
        return self.db[name]


mongo = MongoDB()


def get_db() -> Database:
    """Convenience helper to get the DB from the current app context."""
    return current_app.extensions["mongodb"].db
