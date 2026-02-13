# backend/app/schemas/task.py
"""
Schémas Pydantic pour les Tâches (Tasks) dans l'API et WebSocket
- Validation stricte des entrées
- Formatage des réponses (sans données sensibles)
- Champs adaptés pour les opérations CRUD et drag & drop (changement de status)
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, constr, Field

# Statuts Kanban possibles (doivent correspondre à ceux du modèle SQLModel)
KANBAN_STATUSES = ["todo", "in_progress", "review", "done"]

# ───────────────────────────────────────────────
# Schéma de base partagé (champs communs)
# ───────────────────────────────────────────────
class TaskBase(BaseModel):
    title: constr(min_length=1, max_length=200) = Field(
        ..., description="Titre de la tâche (obligatoire)"
    )
    description: Optional[str] = Field(
        None, max_length=2000, description="Description détaillée ou notes"
    )
    status: str = Field(
        default="todo",
        description=f"Statut Kanban : {', '.join(KANBAN_STATUSES)}"
    )
    priority: str = Field(
        default="medium",
        description="Priorité : low, medium, high, urgent"
    )
    due_date: Optional[datetime] = Field(
        None, description="Date d'échéance (ISO format)"
    )


# ───────────────────────────────────────────────
# Schéma pour créer une nouvelle tâche (POST /tasks)
# ───────────────────────────────────────────────
class TaskCreate(TaskBase):
    project_id: int = Field(
        ..., description="ID du projet auquel rattacher la tâche"
    )
    assigned_to: Optional[int] = Field(
        None, description="ID de l'utilisateur assigné (optionnel)"
    )


# ───────────────────────────────────────────────
# Schéma pour mise à jour d'une tâche (PATCH /tasks/{task_id})
# Utilisé notamment pour le drag & drop (changer status)
# ───────────────────────────────────────────────
class TaskUpdate(BaseModel):
    title: Optional[constr(min_length=1, max_length=200)] = None
    description: Optional[str] = None
    status: Optional[str] = Field(
        None, description=f"Changement de statut : {', '.join(KANBAN_STATUSES)}"
    )
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None


# ───────────────────────────────────────────────
# Schéma de réponse publique (renvoyé dans GET /tasks, WebSocket events)
# ───────────────────────────────────────────────
class TaskOut(TaskBase):
    id: int = Field(..., description="ID unique de la tâche")
    project_id: int = Field(..., description="ID du projet parent")
    assigned_to: Optional[int] = Field(None, description="ID de l'utilisateur assigné")
    created_by: int = Field(..., description="ID de l'utilisateur qui a créé la tâche")
    created_at: datetime = Field(..., description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Dernière mise à jour")

    class Config:
        from_attributes = True  # Permet conversion depuis objet SQLModel


# ───────────────────────────────────────────────
# Schéma pour les événements WebSocket (ex: tâche déplacée)
# Plus léger, optimisé pour le temps réel
# ───────────────────────────────────────────────
class TaskEvent(BaseModel):
    event_type: str = Field(..., description="Ex: 'task_created', 'task_updated', 'task_moved'")
    task_id: int
    project_id: int
    data: TaskOut | TaskUpdate  # Selon l'événement : tâche complète ou juste les changements
    updated_by: int  # ID de l'utilisateur qui a provoqué l'événement
