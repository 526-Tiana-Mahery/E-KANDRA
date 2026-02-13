# mobile/services/websocket_service.py

import json
import threading
from typing import Callable, Optional

try:
    import websocket  # pip install websocket-client
except ImportError:
    print("[WARNING] websocket-client non installé → WebSocket désactivé")
    websocket = None

from kivy.clock import Clock
from kivy.logger import Logger


class WebSocketService:
    """
    Gestion de la connexion WebSocket pour mises à jour live (Kanban, notifications, etc.)
    Compatible avec FastAPI + websocket (ex: via /ws/kanban/{project_id})
    """

    def __init__(self):
        self.ws = None
        self.ws_thread = None
        self.on_message_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None
        self.on_connect_callback: Optional[Callable] = None
        self.on_disconnect_callback: Optional[Callable] = None

        self.url = None
        self.is_connected = False

    def connect(
        self,
        url: str = None,
        on_message: Callable = None,
        on_error: Callable = None,
        on_connect: Callable = None,
        on_disconnect: Callable = None,
        channel: str = None,
        token: str = None
    ):
        """
        Établit la connexion WebSocket
        - url: ex: ws://127.0.0.1:8000/ws/project/123
        - channel: optionnel, si ton backend utilise des rooms/subscriptions
        """
        if websocket is None:
            Logger.warning("WebSocket: bibliothèque manquante")
            return

        if url is None:
            # Exemple par défaut (adapte selon ton backend)
            base = "ws://127.0.0.1:8000" if "localhost" in BASE_URL else "wss://ton-domaine.com"
            url = f"{base}/ws/kanban/{channel}" if channel else f"{base}/ws"

        self.url = url
        self.on_message_callback = on_message
        self.on_error_callback = on_error
        self.on_connect_callback = on_connect
        self.on_disconnect_callback = on_disconnect

        # Ajout token si fourni (ex: ?token=xxx ou Authorization header)
        if token:
            self.url += f"?token={token}"  # ou utilise header si ton backend le supporte

        self._start_connection()

    def _start_connection(self):
        """Lance la connexion dans un thread séparé"""
        if self.ws_thread and self.ws_thread.is_alive():
            return

        def on_open(ws):
            self.is_connected = True
            Logger.info(f"WebSocket connecté: {self.url}")
            if self.on_connect_callback:
                Clock.schedule_once(lambda dt: self.on_connect_callback())

        def on_message(ws, message):
            try:
                data = json.loads(message)
                if self.on_message_callback:
                    Clock.schedule_once(lambda dt: self.on_message_callback(data))
            except json.JSONDecodeError:
                Logger.warning("Message WS non-JSON reçu")

        def on_error(ws, error):
            self.is_connected = False
            Logger.error(f"WebSocket erreur: {error}")
            if self.on_error_callback:
                Clock.schedule_once(lambda dt: self.on_error_callback(error))

        def on_close(ws, close_status_code, close_msg):
            self.is_connected = False
            Logger.info(f"WebSocket fermé: {close_msg}")
            if self.on_disconnect_callback:
                Clock.schedule_once(lambda dt: self.on_disconnect_callback())

        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        self.ws_thread = threading.Thread(
            target=self.ws.run_forever,
            kwargs={"ping_interval": 30, "ping_timeout": 10},
            daemon=True
        )
        self.ws_thread.start()

    def send(self, data: dict):
        """Envoie un message au serveur (ex: "task_moved")"""
        if self.is_connected and self.ws:
            try:
                self.ws.send(json.dumps(data))
            except Exception as e:
                Logger.error(f"Erreur envoi WS: {e}")

    def disconnect(self):
        """Ferme proprement la connexion"""
        if self.ws:
            self.ws.close()
        self.is_connected = False
        if self.ws_thread and self.ws_thread.is_alive():
            # Le daemon=True permet de ne pas bloquer la fermeture de l'app
            pass

    def is_alive(self) -> bool:
        return self.is_connected
