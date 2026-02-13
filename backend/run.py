# backend/run.py
"""
Lanceur principal du backend : combine FastAPI + Tornado WebSocket
- Utilise uvicorn pour servir FastAPI
- Intègre Tornado pour gérer les WebSockets (plus mature que les WebSockets natifs FastAPI pour MVP)
- Permet de servir les deux sur le même port (ex: 8000)
"""

import asyncio
import uvicorn
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.httpserver import HTTPServer

from backend.app.main import app as fastapi_app  # L'app FastAPI créée dans main.py
from backend.websocket.kanban_ws import KanbanWebSocketHandler  # On va créer ce handler après

# ───────────────────────────────────────────────
# Configuration du serveur Tornado + intégration FastAPI
# ───────────────────────────────────────────────
def run_server():
    # Port et host
    HOST = "0.0.0.0"
    PORT = 8000

    # Application Tornado qui va gérer les WebSockets
    tornado_app = Application(
        [
            # Route WebSocket pour le Kanban (ex: ws://localhost:8000/ws/kanban/{project_id})
            (r"/ws/kanban/(?P<project_id>\d+)", KanbanWebSocketHandler),
            # On peut ajouter d'autres routes WS ici plus tard (ex: invitations, notifications)
        ],
        debug=True,
    )

    # Serveur Tornado
    http_server = HTTPServer(tornado_app)

    # Boucle événementielle asyncio (compatible avec FastAPI async)
    loop = asyncio.get_event_loop()
    IOLoop.configure(loop)

    # On lance le serveur HTTP/Tornado
    http_server.listen(PORT, address=HOST)
    print(f"Tornado WebSocket server démarré sur http://{HOST}:{PORT}")

    # On monte FastAPI via ASGI dans Tornado (via uvicorn)
    # Alternative : lancer uvicorn séparément, mais on veut tout sur le même port
    # Pour MVP : on lance uvicorn en thread ou on utilise un proxy reverse (mais ici on simplifie)

    # Lancement uvicorn dans la boucle asyncio
    config = uvicorn.Config(
        "backend.app.main:app",
        host=HOST,
        port=PORT,
        log_level="info",
        reload=True,  # Auto-reload en dev
        factory=False,
    )
    server = uvicorn.Server(config)

    # On lance tout dans la boucle
    loop.run_until_complete(server.serve())

if __name__ == "__main__":
    print("Démarrage du serveur backend (FastAPI + Tornado WebSocket)...")
    run_server()
