# backend/app/api/tasks.py
"""
Routes API pour les Tâches (Tasks)
- CRUD basique pour les tâches d'un projet
- Mise à jour du statut (drag & drop)
- Broadcast WebSocket après chaque modification importante
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from typing import List, Annotated

from .. import models, schemas
from ..dependencies import get_current_user, get_session
from ..models.user import User
from ..models.project import Project
from ..models.task import Task
from ..websocket.kanban_ws import broadcast_to_project

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ───────────────────────────────────────────────
# Créer une nouvelle tâche dans un projet
# ───────────────────────────────────────────────
@router.post("/", response_model=schemas.task.TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    task_create: schemas.task.TaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    # Vérifier que le projet existe et que l'utilisateur y a accès (MVP : propriétaire de l'équipe)
    project = session.get(Project, task_create.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    team = session.get(models.team.Team, project.team_id)
    if not team or team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à ce projet (MVP)")

    db_task = Task(
        **task_create.dict(),
        created_by=current_user.id
    )

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Broadcast WebSocket : nouvelle tâche créée
    broadcast_to_project(
        project_id=task_create.project_id,
        event={
            "event_type": "task_created",
            "task_id": db_task.id,
            "project_id": project.id,
            "data": schemas.task.TaskOut.from_orm(db_task).dict(),
            "updated_by": current_user.id
        }
    )

    return db_task


# ───────────────────────────────────────────────
# Lister les tâches d'un projet (filtré par status optionnel)
# ───────────────────────────────────────────────
@router.get("/", response_model=List[schemas.task.TaskOut])
def list_tasks(
    project_id: int,
    status: str | None = None,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    team = session.get(models.team.Team, project.team_id)
    if not team or team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    statement = select(Task).where(Task.project_id == project_id)
    if status:
        statement = statement.where(Task.status == status)

    tasks = session.exec(statement).all()
    return tasks


# ───────────────────────────────────────────────
# Détails d'une tâche spécifique
# ───────────────────────────────────────────────
@router.get("/{task_id}", response_model=schemas.task.TaskOut)
def get_task(
    task_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")

    project = session.get(Project, task.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet associé introuvable")

    team = session.get(models.team.Team, project.team_id)
    if not team or team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    return task


# ───────────────────────────────────────────────
# Mettre à jour une tâche (statut, titre, priorité, etc.)
# ───────────────────────────────────────────────
@router.patch("/{task_id}", response_model=schemas.task.TaskOut)
def update_task(
    task_id: int,
    task_update: schemas.task.TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")

    project = session.get(Project, task.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet associé introuvable")

    team = session.get(models.team.Team, project.team_id)
    if not team or team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé (MVP)")

    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)

    # Broadcast WebSocket : tâche modifiée (important pour drag & drop)
    broadcast_to_project(
        project_id=project.id,
        event={
            "event_type": "task_updated",
            "task_id": task.id,
            "project_id": project.id,
            "data": schemas.task.TaskOut.from_orm(task).dict(),
            "updated_by": current_user.id
        }
    )

    return task
