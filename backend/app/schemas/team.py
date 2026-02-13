# backend/app/schemas/team.py
"""
Schémas Pydantic pour les Équipes (Teams) dans l'API
- Utilisés pour valider les données entrantes et formater les réponses sortantes
- On évite d'exposer des informations internes inutiles
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, constr, Field

# ───────────────────────────────────────────────
# Schéma de base partagé (champs communs)
# ───────────────────────────────────────────────
class TeamBase(BaseModel):
    name: constr(min_length=3, max_length=100) = Field(
        ..., description="Nom de l'équipe (doit être unique pour l'utilisateur créateur)"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Description de l'équipe ou de son objectif"
    )


# ───────────────────────────────────────────────
# Schéma pour créer une nouvelle équipe (POST /teams)
# ───────────────────────────────────────────────
class TeamCreate(TeamBase):
    pass  # Pour le MVP, pas de champs supplémentaires requis


# ───────────────────────────────────────────────
# Schéma pour mise à jour d'une équipe (PATCH /teams/{team_id})
# ───────────────────────────────────────────────
class TeamUpdate(BaseModel):
    name: Optional[constr(min_length=3, max_length=100)] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# ───────────────────────────────────────────────
# Schéma de réponse publique (renvoyé dans GET /teams, GET /teams/{id}, etc.)
# ───────────────────────────────────────────────
class TeamOut(TeamBase):
    id: int = Field(..., description="ID unique de l'équipe")
    owner_id: int = Field(..., description="ID de l'utilisateur propriétaire")
    created_at: datetime = Field(..., description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Dernière mise à jour")
    is_active: bool = Field(..., description="Équipe active ou archivée")

    class Config:
        from_attributes = True  # Permet de convertir depuis un objet SQLModel


# ───────────────────────────────────────────────
# Schéma étendu (optionnel) : avec nombre de membres / projets (pour dashboard)
# À utiliser plus tard quand on implémente les compteurs
# ───────────────────────────────────────────────
class TeamWithStats(TeamOut):
    member_count: int = Field(default=0, description="Nombre de membres")
    project_count: int = Field(default=0, description="Nombre de projets associés")
