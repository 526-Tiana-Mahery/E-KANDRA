# backend/app/models/task.py
"""
Modèle pour les Tâches (Tasks) dans le système Kanban
- Chaque tâche appartient à un projet (project_id)
- Statut Kanban : "todo", "in_progress", "done" (extensible plus tard)
- Priorité, assigné à un utilisateur, dates, etc.
- Pour le MVP : structure simple mais prête à évoluer
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import constr

# ───────────────────────────────────────────────
# Statuts Kanban possibles (enum-like en string pour simplicité MVP)
# On pourra passer à un Enum plus tard
KANBAN_STATUSES = ["todo", "in_progress", "review", "done"]

# ───────────────────────────────────────────────
# Base commune pour tous les schémas Task
# ───────────────────────────────────────────────
class TaskBase(SQLModel):
    title: constr(min_length=1, max_length=200) = Field(
        nullable=False,
        description="Titre court de la tâche"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Description détaillée, notes, etc."
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
        default=None,
        description="Date d'échéance"
    )


# ───────────────────────────────────────────────
# Schéma pour créer une nouvelle tâche
# ───────────────────────────────────────────────
class TaskCreate(TaskBase):
    project_id: int = Field(
        description="ID du projet auquel appartient cette tâche"
    )
    assigned_to: Optional[int] = Field(
        default=None,
        description="ID de l'utilisateur assigné (optionnel au début)"
    )


# ───────────────────────────────────────────────
# Schéma pour mise à jour d'une tâche (drag & drop = changement de status)
# ───────────────────────────────────────────────
class TaskUpdate(SQLModel):
    title: Optional[constr(min_length=1, max_length=200)] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None


# ───────────────────────────────────────────────
# Modèle de base de données : Table tasks
# ───────────────────────────────────────────────
class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Clés étrangères
    project_id: int = Field(
        foreign_key="project.id",
        nullable=False,
        index=True,
        description="Projet parent"
    )
    assigned_to: Optional[int] = Field(
        foreign_key="user.id",
        default=None,
        description="Utilisateur assigné à la tâche"
    )
    created_by: int = Field(
        foreign_key="user.id",
        nullable=False,
        description="Créateur de la tâche"
    )
    
    # Dates automatiques
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relations
    project: "Project" = Relationship(back_populates="tasks")
    assignee: Optional["User"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[Task.assigned_to]"})
    creator: "User" = Relationship(sa_relationship_kwargs={"foreign_keys": "[Task.created_by]"})


# ───────────────────────────────────────────────
# Schéma pour lecture publique (renvoyé dans les réponses API et WebSocket)
# ───────────────────────────────────────────────
class TaskPublic(TaskBase):
    id: int
    project_id: int
    assigned_to: Optional[int]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
