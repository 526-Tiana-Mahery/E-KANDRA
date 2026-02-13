# backend/app/schemas/user.py
"""
Schémas Pydantic spécifiques pour l'API User.
- On utilise ces schémas dans les routes FastAPI (request/response models)
- Différents des modèles SQLModel pour plus de contrôle sur ce qui est exposé
- Permet de valider les données entrantes et de formater les réponses sortantes
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, constr, Field

# ───────────────────────────────────────────────
# Schéma de base partagé (champs communs lecture/écriture)
# ───────────────────────────────────────────────
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Adresse email valide et unique")
    username: constr(min_length=3, max_length=50) = Field(
        ..., description="Nom d'utilisateur unique (3-50 caractères)"
    )
    full_name: Optional[str] = Field(
        None, max_length=100, description="Nom complet (optionnel)"
    )


# ───────────────────────────────────────────────
# Schéma pour l'inscription (POST /register)
# ───────────────────────────────────────────────
class UserCreate(UserBase):
    password: constr(min_length=8) = Field(
        ..., description="Mot de passe (minimum 8 caractères)"
    )


# ───────────────────────────────────────────────
# Schéma pour mise à jour du profil (PATCH /users/me)
# ───────────────────────────────────────────────
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[constr(min_length=3, max_length=50)] = None
    full_name: Optional[str] = None
    password: Optional[constr(min_length=8)] = None


# ───────────────────────────────────────────────
# Schéma de réponse publique (ce qu'on renvoie dans les GET)
# ───────────────────────────────────────────────
class UserOut(UserBase):
    id: int = Field(..., description="ID unique de l'utilisateur")
    is_active: bool = Field(..., description="Compte actif ou non")
    created_at: Optional[str] = None  # On pourra formater en ISO si besoin

    class Config:
        from_attributes = True  # Permet de convertir depuis un objet SQLModel ou ORM


# ───────────────────────────────────────────────
# Schéma pour login (POST /login) - ce que l'utilisateur envoie
# ───────────────────────────────────────────────
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ───────────────────────────────────────────────
# Schéma de réponse après login réussi (avec token JWT)
# ───────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ───────────────────────────────────────────────
# Schéma pour l'utilisateur courant (dans les endpoints protégés)
# ───────────────────────────────────────────────
class UserInDBOut(UserOut):
    # On peut ajouter des champs internes si besoin (ex: last_login)
    pass
