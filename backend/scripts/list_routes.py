import json
import os
import sys

# Ensure current working directory is on sys.path (run_in_terminal doesn't add it)
sys.path.insert(0, os.getcwd())

from app.api.main import app

routes = []
for r in app.router.routes:
    methods = getattr(r, "methods", None)
    try:
        path = r.path
    except Exception:
        path = str(r)
    routes.append({"path": path, "methods": list(methods) if methods else []})

print(json.dumps(sorted(routes, key=lambda x: x["path"]), indent=2, ensure_ascii=False))
