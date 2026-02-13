# backend/app/api/projects.py
"""
Routes API pour les Projets
- Création d'un projet dans une équipe
- Liste des projets (filtrée par équipe ou par utilisateur)
- Détails et modification d'un projet
- Protection : authentification + vérification d'appartenance à l'équipe
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select, Session
from typing import List, Annotated, Optional

from .. import models, schemas
from ..dependencies import get_current_user, get_session
from ..models.user import User
from ..models.team import Team
from ..models.project import Project

router = APIRouter(prefix="/projects", tags=["projects"])


# ───────────────────────────────────────────────
# Créer un nouveau projet dans une équipe
# ───────────────────────────────────────────────
@router.post("/", response_model=schemas.project.ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_create: schemas.project.ProjectCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    # Vérifier que l'équipe existe et que l'utilisateur en est propriétaire (MVP)
    team = session.get(Team, project_create.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Équipe non trouvée")
    
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Seul le propriétaire de l'équipe peut créer un projet (pour le MVP)")
    
    db_project = Project(
        **project_create.dict(),
        created_by=current_user.id
    )
    
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    
    return db_project


# ───────────────────────────────────────────────
# Lister les projets (filtré par team_id)
# ───────────────────────────────────────────────
@router.get("/", response_model=List[schemas.project.ProjectOut])
def list_projects(
    team_id: Optional[int] = Query(None, description="Filtrer par équipe"),
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    statement = select(Project)
    
    if team_id:
        # Vérifier que l'utilisateur a accès à cette équipe
        team = session.get(Team, team_id)
        if not team or team.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Accès non autorisé à cette équipe")
        statement = statement.where(Project.team_id == team_id)
    else:
        # Pour MVP : seulement les projets des équipes dont on est propriétaire
        statement = statement.where(Project.created_by == current_user.id)
    
    projects = session.exec(statement).all()
    return projects


# ───────────────────────────────────────────────
# Détails d'un projet spécifique
# ───────────────────────────────────────────────
@router.get("/{project_id}", response_model=schemas.project.ProjectOut)
def get_project(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    
    # Vérifier accès (MVP : propriétaire de l'équipe)
    team = session.get(Team, project.team_id)
    if not team or team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    return project


# ───────────────────────────────────────────────
# Modifier un projet (nom, description, statut)
# ───────────────────────────────────────────────
@router.patch("/{project_id}", response_model=schemas.project.ProjectOut)
def update_project(
    project_id: int,
    project_update: schemas.project.ProjectUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    
    # Vérifier que l'utilisateur est le créateur ou propriétaire de l'équipe (MVP)
    team = session.get(Team, project.team_id)
    if not team or team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Seul le propriétaire de l'équipe peut modifier le projet")
    
    update_data = project_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    
    session.add(project)
    session.commit()
    session.refresh(project)
    
    return project
