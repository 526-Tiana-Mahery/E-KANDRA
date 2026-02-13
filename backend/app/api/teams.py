# backend/app/api/teams.py
"""
Routes API pour les équipes (Teams)
- Création, liste, détails, mise à jour
- Protection : authentification requise pour la plupart des actions
- Permissions basiques : seul le propriétaire peut modifier pour MVP
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from typing import List, Annotated

from .. import models, schemas
from ..dependencies import get_current_user, get_session
from ..models.user import User
from ..models.team import Team

router = APIRouter(prefix="/teams", tags=["teams"])


# ───────────────────────────────────────────────
# Liste des équipes de l'utilisateur connecté
# ───────────────────────────────────────────────
@router.get("/my-teams", response_model=List[schemas.team.TeamOut])
def get_my_teams(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    # Pour MVP : on retourne seulement les équipes où l'utilisateur est propriétaire
    # (plus tard : ajouter table TeamMember pour les équipes où il est invité/membre)
    statement = select(Team).where(Team.owner_id == current_user.id)
    teams = session.exec(statement).all()
    return teams


# ───────────────────────────────────────────────
# Créer une nouvelle équipe
# ───────────────────────────────────────────────
@router.post("/", response_model=schemas.team.TeamOut, status_code=status.HTTP_201_CREATED)
def create_team(
    team_create: schemas.team.TeamCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    # Créer l'équipe avec l'utilisateur courant comme propriétaire
    db_team = Team(
        **team_create.dict(),
        owner_id=current_user.id
    )
    
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    
    return db_team


# ───────────────────────────────────────────────
# Détails d'une équipe spécifique
# ───────────────────────────────────────────────
@router.get("/{team_id}", response_model=schemas.team.TeamOut)
def get_team(
    team_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Équipe non trouvée")
    
    # Pour MVP : autoriser la vue si propriétaire
    # (plus tard : autoriser si membre via TeamMember)
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    return team


# ───────────────────────────────────────────────
# Modifier une équipe (nom, description, etc.)
# ───────────────────────────────────────────────
@router.patch("/{team_id}", response_model=schemas.team.TeamOut)
def update_team(
    team_id: int,
    team_update: schemas.team.TeamUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Équipe non trouvée")
    
    # Seul le propriétaire peut modifier pour le MVP
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Seul le propriétaire peut modifier l'équipe")
    
    # Mise à jour des champs fournis
    update_data = team_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(team, key, value)
    
    session.add(team)
    session.commit()
    session.refresh(team)
    
    return team
