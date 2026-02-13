# backend/app/database.py
import os
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker

# ───────────────────────────────────────────────
# Configuration de la base de données
# ───────────────────────────────────────────────

# Chemin absolu vers le dossier database/
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)  # Crée le dossier s'il n'existe pas

DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'app.db'}"
ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_DIR / 'app.db'}"

# Engine synchrone (pour migrations ou scripts init)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Important pour SQLite en multi-thread
    echo=False  # Passe à True pour voir les requêtes SQL en dev
)

# Engine asynchrone (optionnel pour l'instant, mais prêt pour plus tard)
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False
)

# Session maker synchrone
def get_session() -> Session:
    with Session(engine) as session:
        yield session

# Session maker asynchrone (si on passe à async routes plus tard)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=Session
)

# ───────────────────────────────────────────────
# Création des tables (exécuter une fois au démarrage ou via migration)
# ───────────────────────────────────────────────

def create_db_and_tables():
    """Crée toutes les tables si elles n'existent pas"""
    SQLModel.metadata.create_all(engine)

# ───────────────────────────────────────────────
# Exécuter la création des tables au démarrage (pour MVP)
# ───────────────────────────────────────────────
if __name__ == "__main__":
    create_db_and_tables()
    print("Base de données SQLite créée / tables vérifiées.")
