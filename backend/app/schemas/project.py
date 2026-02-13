# backend/app/schemas/project.py
"""
Schémas Pydantic pour les Projets dans l'API
- Validation des données entrantes et formatage des réponses sortantes
- Champs adaptés pour les opérations CRUD sur les projets
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, constr, Field

# ───────────────────────────────────────────────
# Schéma de base partagé (champs communs)
# ───────────────────────────────────────────────
class ProjectBase(BaseModel):
    name: constr(min_length=3, max_length=150) = Field(
        ..., description="Nom du projet (obligatoire, 3 à 150 caractères)"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Description détaillée du projet"
    )
    status: str = Field(
        default="active",
        description="Statut du projet : active, archived, completed"
    )


# ───────────────────────────────────────────────
# Schéma pour créer un nouveau projet (POST /projects)
# ───────────────────────────────────────────────
class ProjectCreate(ProjectBase):
    team_id: int = Field(
        ..., description="ID de l'équipe à laquelle rattacher ce projet"
    )


# ───────────────────────────────────────────────
# Schéma pour mise à jour d'un projet (PATCH /projects/{project_id})
# ───────────────────────────────────────────────
class ProjectUpdate(BaseModel):
    name: Optional[constr(min_length=3, max_length=150)] = None
    description: Optional[str] = None
    status: Optional[str] = None


# ───────────────────────────────────────────────
# Schéma de réponse publique (renvoyé dans les GET)
# ───────────────────────────────────────────────
class ProjectOut(ProjectBase):
    id: int = Field(..., description="ID unique du projet")
    team_id: int = Field(..., description="ID de l'équipe propriétaire")
    created_by: int = Field(..., description="ID de l'utilisateur qui a créé le projet")
    created_at: datetime = Field(..., description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Dernière mise à jour")

    class Config:
        from_attributes = True  # Conversion depuis SQLModel ou ORM


# ───────────────────────────────────────────────
# Schéma étendu (optionnel) : avec quelques stats pour le dashboard
# (à remplir dans les endpoints quand on aura les relations)
# ───────────────────────────────────────────────
class ProjectWithStats(ProjectOut):
    task_count: int = Field(default=0, description="Nombre total de tâches")
    todo_count: int = Field(default=0, description="Tâches en 'todo'")
    in_progress_count: int = Field(default=0, description="Tâches en cours")
    done_count: int = Field(default=0, description="Tâches terminées")
