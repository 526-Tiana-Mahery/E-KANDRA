# frontend/app/callbacks/kanban_callbacks.py
"""
Callbacks pour le board Kanban (project_kanban.py)
- Rafraîchissement périodique des tâches (polling via Interval)
- Gestion du drag & drop → détection changement colonne + PATCH statut
- Feedback utilisateur via alertes Dash
- Placeholder pour futur vrai WebSocket (broadcast depuis backend)
"""

from dash import callback, Input, Output, State, no_update, ctx
import dash_bootstrap_components as dbc
import requests
from datetime import datetime


# ───────────────────────────────────────────────
# 1. Rafraîchissement périodique des tâches (polling)
# ───────────────────────────────────────────────
@callback(
    Output("store-tasks", "data", allow_duplicate=True),
    Input("refresh-interval", "n_intervals"),
    State("store-project-id", "data"),
    State("store-auth-token", "data"),
    prevent_initial_call=True
)
def refresh_kanban_tasks(n_intervals, project_id, token):
    """
    Recharge les tâches toutes les X secondes (ex: 10s)
    Permet de voir les changements faits par d'autres utilisateurs (simule WS)
    """
    if not project_id or not token:
        return no_update

    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(
            f"http://127.0.0.1:8000/tasks?project_id={project_id}",
            headers=headers,
            timeout=6
        )

        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"Erreur refresh tâches {resp.status_code}: {resp.text[:100]}...")
            return no_update

    except Exception as e:
        print(f"Erreur polling: {str(e)}")
        return no_update


# ───────────────────────────────────────────────
# 2. Drag & drop : détection du déplacement entre colonnes
# ───────────────────────────────────────────────
@callback(
    Output("store-tasks", "data", allow_duplicate=True),
    Output("kanban-alert", "children", allow_duplicate=True),
    Input("kanban-grid", "layout"),  # layout mis à jour par dash_draggable
    State("store-tasks", "data"),
    State("store-auth-token", "data"),
    State("store-project-id", "data"),
    prevent_initial_call=True
)
def handle_kanban_drag_drop(new_layout, tasks, token, project_id):
    """
    Quand une tâche change de colonne :
    - identifie la tâche et le nouveau statut
    - envoie PATCH /tasks/{id}
    - met à jour le store local
    - affiche une alerte de confirmation
    """
    if not new_layout or not tasks or not token or not project_id:
        raise no_update

    # Mapping : index colonne → statut
    status_by_index = {0: "todo", 1: "in_progress", 2: "review", 3: "done"}

    moved_task_id = None
    new_status = None

    for item in new_layout:
        card_id = item.get("i", "")
        if not card_id.startswith("task-"):
            continue

        task_id = int(card_id.replace("task-", ""))
        col_index = item.get("x")  # position horizontale = colonne

        candidate_status = status_by_index.get(col_index)
        if not candidate_status:
            continue

        task = next((t for t in tasks if t["id"] == task_id), None)
        if task and task["status"] != candidate_status:
            moved_task_id = task_id
            new_status = candidate_status
            break

    if not moved_task_id or not new_status:
        raise no_update

    # Appel PATCH au backend
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.patch(
            f"http://127.0.0.1:8000/tasks/{moved_task_id}",
            json={"status": new_status},
            headers=headers,
            timeout=5
        )

        if resp.status_code in (200, 204):
            # Mise à jour locale (pour UX immédiate)
            for t in tasks:
                if t["id"] == moved_task_id:
                    t["status"] = new_status
                    t["updated_at"] = datetime.utcnow().isoformat()
                    break

            alert = dbc.Alert(
                f"Tâche déplacée vers **{new_status}**",
                color="success",
                dismissable=True,
                duration=3000,
                className="mt-2"
            )
            return tasks, alert

        else:
            return no_update, dbc.Alert(
                f"Échec déplacement (erreur {resp.status_code})",
                color="danger",
                dismissable=True,
                duration=5000
            )

    except Exception as e:
        print(f"Erreur PATCH drag & drop : {str(e)}")
        return no_update, dbc.Alert(
            "Erreur réseau lors du déplacement",
            color="danger",
            dismissable=True,
            duration=5000
        )


# ───────────────────────────────────────────────
# 3. Placeholder / préparation pour vrai WebSocket
# ───────────────────────────────────────────────
@callback(
    Output("kanban-alert", "children", allow_duplicate=True),
    Input("refresh-interval", "n_intervals"),
    prevent_initial_call=True
)
def websocket_placeholder_alert(n):
    """
    Pour l'instant : on utilise polling.
    Quand WebSocket sera implémenté, ce callback pourra être supprimé ou modifié
    pour réagir aux événements broadcast (task_created, task_updated, etc.)
    """
    return no_update  # Pas d'alerte automatique pour l'instant
