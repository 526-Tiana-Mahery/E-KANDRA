# backend/app/api/auth.py
"""
Routes d'authentification (FastAPI)
- POST /auth/register : inscription
- POST /auth/login   : connexion + génération token JWT
- GET  /auth/me      : infos utilisateur courant (protégée)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select, Session
from typing import Annotated

from .. import schemas
from .. import models
from ..dependencies import (
    get_current_user,
    verify_password,
    get_password_hash,
    create_access_token,
    get_session,
)
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# ───────────────────────────────────────────────
# Inscription d'un nouvel utilisateur
# ───────────────────────────────────────────────
@router.post("/register", response_model=schemas.user.UserOut)
def register(
    user_create: schemas.user.UserCreate,
    session: Session = Depends(get_session)
):
    # Vérifier si l'email ou username existe déjà
    stmt = select(models.user.User).where(
        (models.user.User.email == user_create.email) |
        (models.user.User.username == user_create.username)
    )
    existing_user = session.exec(stmt).first()
    
    if existing_user:
        if existing_user.email == user_create.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email déjà utilisé"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nom d'utilisateur déjà pris"
            )

    # Créer l'utilisateur
    hashed_password = get_password_hash(user_create.password)
    db_user = models.user.User(
        **user_create.dict(exclude={"password"}),
        hashed_password=hashed_password
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return db_user


# ───────────────────────────────────────────────
# Connexion + génération token JWT
# ───────────────────────────────────────────────
@router.post("/login", response_model=schemas.user.Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
):
    # Trouver l'utilisateur par email ou username
    stmt = select(models.user.User).where(
        (models.user.User.email == form_data.username) |
        (models.user.User.username == form_data.username)
    )
    user = session.exec(stmt).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilisateur inactif"
        )
    
    # Générer le token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# ───────────────────────────────────────────────
# Récupérer les infos de l'utilisateur connecté
# ───────────────────────────────────────────────
@router.get("/me", response_model=schemas.user.UserOut)
def read_users_me(
    current_user: Annotated[models.user.User, Depends(get_current_user)]
):
    return current_user
