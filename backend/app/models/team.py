# backend/app/models/team.py
"""
Modèle pour les Équipes (Teams)
- Une équipe a un nom, une description, un propriétaire (user)
- Une équipe peut avoir plusieurs membres (via table de liaison TeamMember, à créer plus tard)
- Pour le MVP : on commence simple avec owner_id seulement
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import constr

# ───────────────────────────────────────────────
# Base commune pour les schémas Team
# ───────────────────────────────────────────────
class TeamBase(SQLModel):
    name: constr(min_length=3, max_length=100) = Field(
        index=True,
        nullable=False,
        description="Nom de l'équipe (unique au sein de l'utilisateur ou global selon choix)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Description courte de l'équipe / du projet"
    )
    is_active: bool = Field(
        default=True,
        description="Équipe active ou archivée"
    )


# ───────────────────────────────────────────────
# Schéma pour la création d'une nouvelle équipe
# ───────────────────────────────────────────────
class TeamCreate(TeamBase):
    pass  # Pour MVP, pas de champs supplémentaires requis


# ───────────────────────────────────────────────
# Schéma pour mise à jour d'une équipe
# ───────────────────────────────────────────────
class TeamUpdate(SQLModel):
    name: Optional[constr(min_length=3, max_length=100)] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# ───────────────────────────────────────────────
# Modèle de base de données : Table teams
# ───────────────────────────────────────────────
class Team(TeamBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Clé étrangère vers le propriétaire
    owner_id: int = Field(
        foreign_key="user.id",
        nullable=False,
        index=True,
        description="ID de l'utilisateur qui a créé l'équipe (admin principal)"
    )
    
    # Date de création / mise à jour
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relation : propriétaire (back_populates pour bidirectionnel)
    owner: "User" = Relationship(back_populates="owned_teams")
    
    # Relations futures (à ajouter quand on implémente les membres)
    # members: List["TeamMember"] = Relationship(back_populates="team")
    # projects: List["Project"] = Relationship(back_populates="team")


# ───────────────────────────────────────────────
# Schéma pour lecture publique (renvoyé dans les réponses API)
# ───────────────────────────────────────────────
class TeamPublic(TeamBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ───────────────────────────────────────────────
# À ajouter plus tard dans models/user.py (pour la relation inverse) :
# owned_teams: List["Team"] = Relationship(back_populates="owner")
# ───────────────────────────────────────────────
