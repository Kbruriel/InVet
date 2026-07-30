"""Runtime tweaks for local backend commands.

This module is loaded automatically by Python when it is available on the
import path. We use it to silence a third-party deprecation warning that is
triggered during FastAPI/Starlette imports before pytest filters are applied.
"""

from __future__ import annotations

import warnings

_original_warn = warnings.warn


def _warn(message, category=None, stacklevel=1, source=None):  # type: ignore[no-untyped-def]
    if (
        category is PendingDeprecationWarning
        and "python_multipart" in str(message)
        and "starlette" in str(message)
    ):
        return None
    return _original_warn(
        message,
        category=category,
        stacklevel=stacklevel,
        source=source,
    )


warnings.warn = _warn
