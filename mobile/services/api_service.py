# mobile/services/api_service.py

import requests
from typing import Dict, Any, Optional, Tuple

from .auth_service import load_auth_token

# Configuration backend (à adapter selon ton environnement)
BASE_URL = "http://127.0.0.1:8000"  # ou "https://ton-domaine.com" en prod
API_PREFIX = "/api"

TIMEOUT = 10  # secondes


def get_headers() -> Dict[str, str]:
    """Retourne les headers avec Bearer token si disponible"""
    token = load_auth_token()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def handle_response(response: requests.Response) -> Tuple[bool, Any]:
    """Gestion standard des réponses API"""
    try:
        data = response.json() if response.text else {}
    except ValueError:
        data = {"detail": response.text[:200]}

    if response.status_code in (200, 201):
        return True, data
    else:
        error_msg = data.get("detail", f"Erreur {response.status_code}")
        return False, {"detail": error_msg, "status_code": response.status_code}


# ─── Projets ────────────────────────────────────────────────────────────────

def get_user_projects(limit: int = 10, offset: int = 0) -> Dict:
    """Récupère la liste des projets de l'utilisateur"""
    url = f"{BASE_URL}{API_PREFIX}/projects/?limit={limit}&offset={offset}"
    try:
        resp = requests.get(url, headers=get_headers(), timeout=TIMEOUT)
        success, data = handle_response(resp)
        return data if success else {"projects": [], "error": data.get("detail")}
    except requests.RequestException as e:
        return {"projects": [], "error": f"Erreur réseau: {str(e)}"}


def get_project(project_id: int) -> Dict:
    """Détails d'un projet spécifique"""
    url = f"{BASE_URL}{API_PREFIX}/projects/{project_id}"
    try:
        resp = requests.get(url, headers=get_headers(), timeout=TIMEOUT)
        success, data = handle_response(resp)
        return data if success else {"error": data.get("detail")}
    except requests.RequestException as e:
        return {"error": f"Erreur réseau: {str(e)}"}


# ─── Tâches ─────────────────────────────────────────────────────────────────

def get_project_tasks(project_id: int) -> Dict:
    """Récupère toutes les tâches d'un projet"""
    url = f"{BASE_URL}{API_PREFIX}/projects/{project_id}/tasks"
    try:
        resp = requests.get(url, headers=get_headers(), timeout=TIMEOUT)
        success, data = handle_response(resp)
        return data if success else {"tasks": [], "error": data.get("detail")}
    except requests.RequestException as e:
        return {"tasks": [], "error": f"Erreur réseau: {str(e)}"}


def create_task(project_id: int, task_data: Dict) -> Tuple[bool, Dict]:
    """Crée une nouvelle tâche dans un projet"""
    url = f"{BASE_URL}{API_PREFIX}/projects/{project_id}/tasks"
    try:
        resp = requests.post(url, json=task_data, headers=get_headers(), timeout=TIMEOUT)
        return handle_response(resp)
    except requests.RequestException as e:
        return False, {"detail": f"Erreur réseau: {str(e)}"}


def update_task_status(task_id: int, new_status: str) -> Tuple[bool, Dict]:
    """Met à jour uniquement le statut d'une tâche (pour drag & drop)"""
    url = f"{BASE_URL}{API_PREFIX}/tasks/{task_id}"
    payload = {"status": new_status}
    try:
        resp = requests.patch(url, json=payload, headers=get_headers(), timeout=TIMEOUT)
        return handle_response(resp)
    except requests.RequestException as e:
        return False, {"detail": f"Erreur réseau: {str(e)}"}


# ─── Équipes ────────────────────────────────────────────────────────────────

def get_user_teams(limit: int = 5) -> Dict:
    """Récupère les équipes de l'utilisateur"""
    url = f"{BASE_URL}{API_PREFIX}/teams/?limit={limit}"
    try:
        resp = requests.get(url, headers=get_headers(), timeout=TIMEOUT)
        success, data = handle_response(resp)
        return data if success else {"teams": [], "error": data.get("detail")}
    except requests.RequestException as e:
        return {"teams": [], "error": f"Erreur réseau: {str(e)}"}


# ─── Utilitaires futurs ─────────────────────────────────────────────────────

def check_connection() -> bool:
    """Test ping rapide vers le backend"""
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        return resp.status_code == 200
    except:
        return False
