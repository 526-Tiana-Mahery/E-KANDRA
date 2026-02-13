# backend/app/models/project.py
"""
Modèle pour les Projets
- Un projet appartient à une équipe (team_id)
- Il a un créateur (created_by → référence à User)
- Champs basiques : nom, description, statut, dates
- Pour le MVP : on reste simple, sans sous-équipes imbriquées
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import constr

# ───────────────────────────────────────────────
# Base commune pour tous les schémas Project
# ───────────────────────────────────────────────
class ProjectBase(SQLModel):
    name: constr(min_length=3, max_length=150) = Field(
        index=True,
        nullable=False,
        description="Nom du projet (ex: 'Site Web E-commerce', 'Campagne Marketing Q2')"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Description détaillée du projet"
    )
    status: str = Field(
        default="active",
        description="Statut : active, archived, completed (pour filtrer)"
    )


# ───────────────────────────────────────────────
# Schéma pour créer un nouveau projet
# ───────────────────────────────────────────────
class ProjectCreate(ProjectBase):
    team_id: int = Field(
        description="ID de l'équipe à laquelle ce projet appartient"
    )


# ───────────────────────────────────────────────
# Schéma pour mise à jour d'un projet (tout optionnel)
# ───────────────────────────────────────────────
class ProjectUpdate(SQLModel):
    name: Optional[constr(min_length=3, max_length=150)] = None
    description: Optional[str] = None
    status: Optional[str] = None


# ───────────────────────────────────────────────
# Modèle de base de données : Table projects
# ───────────────────────────────────────────────
class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Clés étrangères
    team_id: int = Field(
        foreign_key="team.id",
        nullable=False,
        index=True,
        description="Équipe propriétaire du projet"
    )
    created_by: int = Field(
        foreign_key="user.id",
        nullable=False,
        description="Utilisateur qui a créé le projet (souvent l'admin de l'équipe)"
    )
    
    # Dates automatiques
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relations
    team: "Team" = Relationship(back_populates="projects")
    creator: "User" = Relationship()  # back_populates pas obligatoire ici
    
    # Relation future : liste des tâches
    # tasks: List["Task"] = Relationship(back_populates="project")


# ───────────────────────────────────────────────
# Schéma pour lecture publique (API responses)
# ───────────────────────────────────────────────
class ProjectPublic(ProjectBase):
    id: int
    team_id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True  # Permet conversion depuis objet SQLModel
