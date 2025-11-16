"""ASGI config for running the project with Uvicorn."""
from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobsearch.settings")

application = get_asgi_application()
