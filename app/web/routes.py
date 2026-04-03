"""
Web routes for Riada Law Platform.
Handles rendering of all HTML templates and dynamic ID routing.
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.document import Document
from app.models.user import User  # This imports the database model
from app.api.v1.endpoints.documents import _d  # Import the formatter

web_router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")

# ─── Auth Routes ──────────────────────────────────────────────────────────────

@web_router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url="/login", status_code=303)

@web_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("pages/auth/login.html", {"request": request})

@web_router.get("/register", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("pages/auth/register.html", {"request": request})

@web_router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="access_token")
    return response

# ─── Dashboard ────────────────────────────────────────────────────────────────

@web_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("pages/dashboard.html", 
                                     {"request": request, "active_page": "dashboard"})

# ─── User Management (Staff/Admin) ──────────────────────────────────────────

@web_router.get("/users", response_class=HTMLResponse)
async def users_list_page(request: Request):
    return templates.TemplateResponse("pages/users/list.html", 
                                     {"request": request, "active_page": "users"})

@web_router.get("/users/create", response_class=HTMLResponse)
async def user_create_page(request: Request):
    # This triggers {% if not user_edit %} in form.html
    return templates.TemplateResponse("pages/users/form.html", 
                                     {"request": request, "active_page": "users", "user_edit": False})

@web_router.get("/users/{user_id}", response_class=HTMLResponse)
async def user_detail_page(request: Request, user_id: int):
    return templates.TemplateResponse("pages/users/user_detail.html", 
                                     {"request": request, "user_id": user_id, "active_page": "users"})

@web_router.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def user_edit_page(request: Request, user_id: int):
    # This triggers {% if user_edit %} in form.html and allows fetching the specific ID
    return templates.TemplateResponse("pages/users/form.html", 
                                     {"request": request, "user_id": user_id, "active_page": "users", "user_edit": True})

# ─── Client Management ────────────────────────────────────────────────────────

@web_router.get("/clients", response_class=HTMLResponse)
async def clients_list_page(request: Request):
    return templates.TemplateResponse("pages/clients/list.html", 
                                     {"request": request, "active_page": "clients"})

@web_router.get("/clients/create", response_class=HTMLResponse)
async def client_create_page(request: Request):
    # This triggers {% if not client %} in form - Copy.html
    return templates.TemplateResponse("pages/clients/form - Copy.html", 
                                     {"request": request, "active_page": "clients", "client": None})

@web_router.get("/clients/{client_id}", response_class=HTMLResponse)
async def client_detail_page(request: Request, client_id: int):
    return templates.TemplateResponse("pages/clients/detail.html", 
                                     {"request": request, "client_id": client_id, "active_page": "clients"})

@web_router.get("/clients/{client_id}/edit", response_class=HTMLResponse)
async def client_edit_page(request: Request, client_id: int):
    # This triggers {% if client %} in form - Copy.html and provides the ID for the PUT request
    return templates.TemplateResponse("pages/clients/form - Copy.html", 
                                     {"request": request, "active_page": "clients", "client": {"id": client_id}})

# ─── My Profile ───────────────────────────────────────────────────────────────

@web_router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    return templates.TemplateResponse("pages/users/profile.html", 
                                     {"request": request, "active_page": "profile"})

# ─── Other Services ───────────────────────────────────────────────────────────

@web_router.get("/tickets", response_class=HTMLResponse)
async def tickets_list_page(request: Request):
    return templates.TemplateResponse("pages/tickets/list.html", 
                                     {"request": request, "active_page": "tickets"})
# app/web/routes.py

@web_router.get("/documents", response_class=HTMLResponse)
async def documents_list_page(request: Request):
    # This renders the list.html template
    return templates.TemplateResponse("pages/documents/list.html", {
        "request": request, 
        "active_page": "documents"
    })

@web_router.get("/documents/upload", response_class=HTMLResponse)
async def document_upload_page(request: Request):
    return templates.TemplateResponse("pages/documents/upload.html", {
        "request": request, 
        "active_page": "documents"
    })

@web_router.get("/documents/{doc_id}", response_class=HTMLResponse)
async def document_viewer_page(request: Request, doc_id: int):
    # This renders the viewer.html template
    return templates.TemplateResponse("pages/documents/viewer.html", {
        "request": request,
        "doc_id": doc_id,
        "active_page": "documents"
    })

@web_router.get("/assistant", response_class=HTMLResponse)
async def assistant_page(request: Request):
    return templates.TemplateResponse("pages/chat/assistant.html", 
                                     {"request": request, "active_page": "assistant"})