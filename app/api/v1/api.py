"""
Main API Router — combines all endpoint routers
File: app/api/v1/api.py
"""

from fastapi import APIRouter

api_router = APIRouter()

_routers = [
    ("app.api.v1.endpoints.auth",          "/auth",          ["Authentication"]),
    ("app.api.v1.endpoints.users",         "/users",         ["Users"]),
    ("app.api.v1.endpoints.clients",       "/clients",       ["Clients"]),
    ("app.api.v1.endpoints.tickets",       "/tickets",       ["Tickets"]),
    ("app.api.v1.endpoints.reminders",     "/reminders",     ["Reminders"]),
    ("app.api.v1.endpoints.documents",     "/documents",     ["Documents"]),
    ("app.api.v1.endpoints.notifications", "/notifications", ["Notifications"]),
    ("app.api.v1.endpoints.financial",     "/financial",     ["Financial"]),
    ("app.api.v1.endpoints.analytics",     "/analytics",     ["Analytics"]),
    ("app.api.v1.endpoints.dashboard",     "/dashboard",     ["Dashboard"]),
    ("app.api.v1.endpoints.lawyers",       "/lawyers",       ["Lawyers"]),
    ("app.api.v1.endpoints.cases",          "/cases",         ["Cases"]),
    ("app.api.v1.endpoints.llm",           "/llm",           ["AI Assistant"]),
]

for module_path, prefix, tags in _routers:
    try:
        import importlib
        module = importlib.import_module(module_path)
        api_router.include_router(
            module.router,
            prefix=prefix,
            tags=tags,
            # redirect_slashes removed — not supported in this FastAPI version
            # Handled at app level: FastAPI(redirect_slashes=False) in main.py
        )
        print(f"  ✅ Loaded: {prefix}")
    except Exception as e:
        print(f"  ⚠️  Skipped {prefix}: {e}")