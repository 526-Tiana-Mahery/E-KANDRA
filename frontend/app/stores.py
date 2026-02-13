# frontend/app/stores.py
"""
Stores globaux Dash (état partagé entre pages et callbacks)
- store-auth-token : JWT token après login
- store-user : infos utilisateur (id, username, etc.)
- store-current-team : équipe sélectionnée
- store-current-project : projet sélectionné
- store-tasks : cache local des tâches du projet courant (pour Kanban)
"""

from dash import dcc

# Liste des stores à déclarer dans main.py (layout global)
global_stores = [
    dcc.Store(id="store-auth-token", data="", storage_type="session"),
    dcc.Store(id="store-user", data={}, storage_type="session"),
    dcc.Store(id="store-current-team", data=None, storage_type="session"),
    dcc.Store(id="store-current-project", data=None, storage_type="session"),
    dcc.Store(id="store-tasks", data=[], storage_type="session"),
]

# Fonction helper pour les initialiser dans main.py
def get_global_stores():
    return global_stores
