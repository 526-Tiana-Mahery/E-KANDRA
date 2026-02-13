# backend/app/config.py
"""
Configuration globale de l'application
- Utilise pydantic-settings pour charger depuis .env ou variables d'environnement
- SECRET_KEY est obligatoire et doit être fort (généré une fois et gardé secret)
- Les autres paramètres ont des valeurs par défaut raisonnables pour le MVP
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# ───────────────────────────────────────────────
# Classe de configuration (pydantic-settings)
# ───────────────────────────────────────────────
class Settings(BaseSettings):
    # Clé secrète pour signer les tokens JWT (à changer absolument !)
    SECRET_KEY: str = "your-super-secret-key-change-me-immediately-1234567890abcdef"

    # Durée de vie du token d'accès (en minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 heures pour le MVP (à réduire en prod)

    # Nom du projet (pour logs, titres, etc.)
    PROJECT_NAME: str = "Task Manager MVP"

    # Base de données (déjà défini dans database.py, mais on peut surcharger si besoin)
    DATABASE_URL: str = ""  # Laisser vide → on utilise le chemin relatif dans database.py

    # Mode développement (active les logs détaillés, reload, etc.)
    DEBUG: bool = True

    # Modèle de configuration : cherche un fichier .env à la racine du projet
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore les variables inconnues dans .env
    )


# ───────────────────────────────────────────────
# Instance globale des settings (à importer partout où besoin)
# ───────────────────────────────────────────────
settings = Settings()


# ───────────────────────────────────────────────
# Fonction helper pour générer une nouvelle SECRET_KEY forte (à exécuter une fois)
# Exemple d'utilisation : python -c "import secrets; print(secrets.token_urlsafe(64))"
# ───────────────────────────────────────────────
if __name__ == "__main__":
    import secrets
    print("Nouvelle SECRET_KEY générée (copie-la dans .env) :")
    print(secrets.token_urlsafe(64))
