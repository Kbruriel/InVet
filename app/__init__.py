# Extend module search path to include backend/app
import os
import pkgutil

# Resolve backend/app relative to this file
backend_app_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')
backend_app_path = os.path.normpath(backend_app_path)

# Extend the package __path__ to include the backend app directory
__path__ = pkgutil.extend_path([__path__[0], backend_app_path], __name__)
