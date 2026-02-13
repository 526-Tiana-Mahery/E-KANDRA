# backend/app/main.py
"""
Point d'entrée principal de l'API FastAPI
- Crée l'application FastAPI
- Configure les métadonnées (titre, description, version)
- Inclut les différents routers (auth, teams, projects, tasks...)
- Ajoute un endpoint racine pour tester le serveur
"""

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api import auth  # On importe le router auth
# À importer plus tard :
# from .api import teams, projects, tasks

# ───────────────────────────────────────────────
# Création de l'application FastAPI
# ───────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API de gestion collaborative de tâches en mode Kanban (MVP)",
    version="0.1.0",
    docs_url="/docs",          # Swagger UI : /docs
    redoc_url="/redoc",        # Documentation alternative
    openapi_url="/openapi.json"
)

# ───────────────────────────────────────────────
# Middleware CORS (important pour que Dash puisse appeler l'API)
# ───────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production (ex: ["http://localhost:8050"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────────────────────────────────────────────
# Inclusion des routers (endpoints groupés)
# ───────────────────────────────────────────────
app.include_router(auth.router)

# À décommenter quand on créera ces fichiers :
# app.include_router(teams.router)
# app.include_router(projects.router)
# app.include_router(tasks.router)

# ───────────────────────────────────────────────
# Endpoint racine pour tester que l'API tourne
# ───────────────────────────────────────────────
@app.get("/", tags=["root"])
async def root():
    return {
        "message": f"Bienvenue sur {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "status": "healthy",
        "version": app.version
    }

# ───────────────────────────────────────────────
# Gestionnaire d'exception global simple (optionnel pour MVP)
# ───────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Une erreur interne est survenue"}
    )
