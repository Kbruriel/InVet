"""Test package bootstrap."""

import os

os.environ.setdefault("INVET_ALLOW_SQLITE_FALLBACK", "1")
if not os.environ.get("SECRET_KEY"):
    os.environ["SECRET_KEY"] = (
        "test-secret-key-for-unit-tests-only-do-not-use-in-production"
    )
if not os.environ.get("ENVIRONMENT"):
    os.environ["ENVIRONMENT"] = "test"
