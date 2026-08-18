"""Convenience module for the FastAPI app used in tests.

The test suite imports ``app`` from ``app.api.v1.app``.  The actual
application factory lives in :mod:`app.api.main`.  Importing the
singleton created there keeps the behaviour identical to a normal
application start‑up while providing a convenient import path for
tests and any other modules that need to use the shared FastAPI
instance.
"""

from app.api.main import app

__all__ = ["app"]
