# E-KANDRA - Gestion collaborative de tâches (Kanban)

MVP d'une application de gestion de tâches en mode Kanban, 100% Python.

## Technologies
- Backend : FastAPI + Tornado (WebSocket)
- Frontend web : Dash + Plotly + Bootstrap
- Base de données : SQLite
- Auth : JWT
- Temps réel : Tornado WebSocket

## Lancement

### Backend (API + WebSocket)
```bash
cd task-manager-mvp
source venv/bin/activate
python backend/run.py
# ou
uvicorn backend.app.main:app --reload --port 8000
