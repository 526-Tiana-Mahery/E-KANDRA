# backend/websocket/kanban_ws.py
"""
Handler WebSocket Tornado pour les mises à jour en temps réel du Kanban
- Connexion par projet : ws://.../ws/kanban/{project_id}
- Gestion de connexions multiples par projet
- Broadcast d'événements (task_created, task_updated, task_moved, etc.)
- Pour MVP : pas d'authentification WS stricte (on peut ajouter plus tard via token dans query)
"""

import json
from typing import Dict, Set
from tornado.websocket import WebSocketHandler

# Stockage en mémoire des connexions actives par project_id (MVP : pas de Redis)
# Format : {project_id: set(WebSocketHandler)}
active_connections: Dict[int, Set[WebSocketHandler]] = {}


class KanbanWebSocketHandler(WebSocketHandler):
    """
    WebSocket handler pour un projet Kanban spécifique
    """

    def open(self, project_id: str):
        """
        Quand un client se connecte : ws://.../ws/kanban/123
        """
        try:
            self.project_id = int(project_id)
        except ValueError:
            self.close(code=1003, reason="project_id doit être un entier")
            return

        # Ajouter cette connexion au set du projet
        if self.project_id not in active_connections:
            active_connections[self.project_id] = set()
        
        active_connections[self.project_id].add(self)
        print(f"Client connecté au projet {self.project_id} | Connexions actives : {len(active_connections[self.project_id])}")

        # Message de bienvenue (optionnel)
        self.write_message(json.dumps({
            "event_type": "connected",
            "message": f"Connecté au Kanban du projet {self.project_id}",
            "active_users": len(active_connections[self.project_id])
        }))


    def on_message(self, message: str):
        """
        Messages envoyés par le client (pour MVP : on n'en attend pas vraiment,
        car les mises à jour viennent du backend via API → broadcast)
        Peut servir pour du chat futur ou ack
        """
        try:
            data = json.loads(message)
            print(f"Message reçu du projet {self.project_id}: {data}")
            # Pour MVP : on ignore ou on peut renvoyer un ack
            self.write_message(json.dumps({"event_type": "ack", "received": data}))
        except json.JSONDecodeError:
            self.write_message(json.dumps({"event_type": "error", "message": "JSON invalide"}))


    def on_close(self):
        """
        Quand le client se déconnecte
        """
        if hasattr(self, "project_id") and self.project_id in active_connections:
            active_connections[self.project_id].discard(self)
            if not active_connections[self.project_id]:
                del active_connections[self.project_id]
            print(f"Client déconnecté du projet {self.project_id} | Restant : {len(active_connections.get(self.project_id, set()))}")


    def check_origin(self, origin: str) -> bool:
        """
        Autorise toutes origines pour MVP (CORS-like pour WS)
        À restreindre en production (ex: vérifier origin == frontend_url)
        """
        return True


# ───────────────────────────────────────────────
# Fonction utilitaire pour broadcaster un événement à tous les clients d'un projet
# À appeler depuis les endpoints API quand une tâche change
# ───────────────────────────────────────────────
def broadcast_to_project(project_id: int, event: dict):
    """
    Envoie un événement JSON à tous les clients connectés sur ce project_id
    Exemple d'event :
    {
        "event_type": "task_moved",
        "task_id": 42,
        "new_status": "in_progress",
        "updated_by": 5
    }
    """
    if project_id not in active_connections:
        return  # Pas de clients → rien à faire

    message = json.dumps(event)
    disconnected = set()

    for conn in active_connections[project_id]:
        try:
            conn.write_message(message)
        except Exception:
            disconnected.add(conn)

    # Nettoyage des connexions mortes
    for conn in disconnected:
        active_connections[project_id].discard(conn)

    if not active_connections[project_id]:
        del active_connections[project_id]
