# backend/app/models/user.py
"""
Définition du modèle User avec SQLModel.
- Table : users
- Champs principaux : id, email, username, hashed_password, is_active, etc.
- On sépare les schémas pour :
  - Création (CreateUser)
  - Mise à jour (UpdateUser)
  - Lecture publique (UserPublic)
  - Lecture complète (User) avec mot de passe hashé (pour usage interne seulement)
"""

from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import EmailStr, constr

# ───────────────────────────────────────────────
# Base commune pour tous les schémas User
# ───────────────────────────────────────────────
class UserBase(SQLModel):
    email: EmailStr = Field(
        unique=True,
        index=True,
        nullable=False,
        description="Adresse email unique de l'utilisateur"
    )
    username: constr(min_length=3, max_length=50) = Field(
        unique=True,
        index=True,
        nullable=False,
        description="Nom d'utilisateur unique (3-50 caractères)"
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Nom complet (optionnel)"
    )
    is_active: bool = Field(
        default=True,
        description="Compte actif ou désactivé (pour ban ou vérification)"
    )


# ───────────────────────────────────────────────
# Schéma pour la création d'un nouvel utilisateur
# (ce que l'utilisateur envoie lors de l'inscription)
# ───────────────────────────────────────────────
class UserCreate(UserBase):
    password: str = Field(
        min_length=8,
        description="Mot de passe en clair (sera hashé avant stockage)"
    )


# ───────────────────────────────────────────────
# Schéma pour mise à jour (PATCH) d'un utilisateur
# Tous les champs optionnels
# ───────────────────────────────────────────────
class UserUpdate(SQLModel):
    email: Optional[EmailStr] = None
    username: Optional[constr(min_length=3, max_length=50)] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


# ───────────────────────────────────────────────
# Modèle de base de données (table réelle)
# ───────────────────────────────────────────────
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(
        nullable=False,
        description="Mot de passe hashé (jamais le mot de passe en clair)"
    )

    # Relations futures (exemples, à ajouter plus tard)
    # teams: List["TeamMember"] = Relationship(back_populates="user")
    # owned_teams: List["Team"] = Relationship(back_populates="owner")


# ───────────────────────────────────────────────
# Schéma pour lecture publique (sans mot de passe)
# À renvoyer dans les réponses API
# ───────────────────────────────────────────────
class UserPublic(UserBase):
    id: int

    class Config:
        from_attributes = True  # Permet de convertir depuis l'objet SQLModel


# ───────────────────────────────────────────────
# Schéma interne (avec hashed_password) pour usage backend seulement
# ───────────────────────────────────────────────
class UserInDB(User):
    pass  # Hérite de tout, y compris hashed_password
