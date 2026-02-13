# mobile/services/auth_service.py

import json
import os
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock

# Pour les requêtes HTTP (on suppose que tu utilises requests ou httpx)
import requests

# Configuration (à adapter selon ton backend)
BACKEND_URL = "http://127.0.0.1:8000"   # ou ton URL de production
AUTH_ENDPOINT = f"{BACKEND_URL}/api/auth/login"
TOKEN_KEY = "access_token"

# Emplacement du stockage local (JsonStore est simple pour MVP)
STORE_PATH = os.path.join(os.path.expanduser("~"), ".e_kandra_mobile.json")
store = JsonStore(STORE_PATH)


def login_user(email: str, password: str) -> tuple[bool, dict]:
    """
    Tente une connexion via l'API backend
    Retourne (success: bool, response_data: dict)
    """
    try:
        payload = {"email": email, "password": password}
        response = requests.post(AUTH_ENDPOINT, json=payload, timeout=8)

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token") or data.get("token")
            if token:
                save_auth_token(token)
                # Option : stocker aussi user_id, username, etc.
                store.put("user", email=email, **data.get("user", {}))
                return True, data
            else:
                return False, {"detail": "Token non reçu"}
        else:
            try:
                error = response.json().get("detail", "Erreur serveur")
            except:
                error = response.text[:100]
            return False, {"detail": error or f"Code {response.status_code}"}

    except requests.exceptions.RequestException as e:
        return False, {"detail": f"Erreur réseau : {str(e)}"}


def save_auth_token(token: str):
    """Stocke le token de manière persistante"""
    store.put(TOKEN_KEY, value=token)
    print("[Auth] Token sauvegardé")


def load_auth_token() -> str | None:
    """Récupère le token stocké"""
    if store.exists(TOKEN_KEY):
        return store.get(TOKEN_KEY)["value"]
    return None


def is_user_logged_in() -> bool:
    """Vérifie si un token valide existe (MVP : juste existence)"""
    token = load_auth_token()
    if not token:
        return False
    
    # Option : valider le token auprès du backend (refresh ou /me)
    # Pour MVP on considère que oui si présent
    return True


def get_current_user() -> dict | None:
    """Récupère les infos utilisateur stockées"""
    if store.exists("user"):
        return store.get("user")
    return None


def logout():
    """Déconnexion locale"""
    if store.exists(TOKEN_KEY):
        store.delete(TOKEN_KEY)
    if store.exists("user"):
        store.delete("user")
    print("[Auth] Déconnexion effectuée")


# Option : vérification périodique ou refresh token (plus tard)
def start_auth_monitor(app):
    """Exemple : vérifier toutes les X minutes si toujours connecté"""
    def check():
        if not is_user_logged_in():
            app.sm.current = "login"
    Clock.schedule_interval(lambda dt: check(), 300)  # toutes les 5 min
