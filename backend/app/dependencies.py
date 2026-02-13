# backend/app/dependencies.py
"""
Dépendances FastAPI pour l'authentification JWT
- Gestion des tokens JWT (création, validation)
- Récupération de l'utilisateur courant à partir du token
- Exceptions personnalisées pour les erreurs d'auth
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import select

from .database import get_session
from .models.user import User
from .config import settings  # On va créer ce fichier après

# ───────────────────────────────────────────────
# Configuration de sécurité
# ───────────────────────────────────────────────

# Schéma OAuth2 (Bearer token dans l'en-tête Authorization)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Hashage des mots de passe (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Algorithme JWT (HS256 est standard et suffisant pour MVP)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Durée de vie du token (à ajuster)


# ───────────────────────────────────────────────
# Modèle pour le payload du token JWT
# ───────────────────────────────────────────────
class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None


# ───────────────────────────────────────────────
# Fonctions utilitaires pour le hashage et la vérification
# ───────────────────────────────────────────────

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe en clair correspond au hash stocké"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Génère un hash bcrypt à partir d'un mot de passe en clair"""
    return pwd_context.hash(password)


# ───────────────────────────────────────────────
# Création d'un token JWT
# ───────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ───────────────────────────────────────────────
# Dépendance principale : récupérer l'utilisateur courant à partir du token
# ───────────────────────────────────────────────
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception
        token_data = TokenData(username=username, user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    # Récupérer l'utilisateur en base
    statement = select(User).where(User.username == token_data.username)
    user = session.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


# ───────────────────────────────────────────────
# Dépendance optionnelle : utilisateur courant ou None (pour routes publiques)
# ───────────────────────────────────────────────
async def get_current_user_optional(
    token: Annotated[Optional[str], Depends(oauth2_scheme)] = None,
    session = Depends(get_session)
) -> Optional[User]:
    if token is None:
        return None
    try:
        return await get_current_user(token, session)
    except HTTPException:
        return None
