# frontend/app/callbacks/kanban_callbacks.py
"""
Callbacks dédiés au Kanban (project_kanban.py)
- Rafraîchissement périodique des tâches (polling)
- Drag & drop entre colonnes → PATCH statut
- Création de tâche + mise à jour locale
- Feedback utilisateur via alertes
- Préparation / simulation WebSocket
"""

from dash import callback, Input, Output, State, no_update, ctx
import dash_bootstrap_components as dbc
import requests
from datetime import datetime
import json

# ───────────────────────────────────────────────
# 1. Rafraîchissement périodique des tâches (polling via Interval)
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
    Recharge toutes les tâches du projet toutes les X secondes.
    C'est la méthode la plus simple et fiable pour le MVP.
    """
    if not project_id or not token:
        return no_update

    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(
            f"http://127.0.0.1:8000/tasks?project_id={project_id}",
            headers=headers,
            timeout=5
        )

        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"Erreur refresh tâches {resp.status_code}: {resp.text}")
            return no_update

    except Exception as e:
        print(f"Erreur connexion polling: {str(e)}")
        return no_update


# ───────────────────────────────────────────────
# 2. Création d'une nouvelle tâche + ajout immédiat au store
# ───────────────────────────────────────────────
@callback(
    Output("new-task-modal", "is_open", allow_duplicate=True),
    Output("store-tasks", "data", allow_duplicate=True),
    Output("kanban-alert", "children", allow_duplicate=True),
    Input("confirm-task-btn", "n_clicks"),
    State("task-title", "value"),
    State("task-desc", "value"),
    State("task-priority", "value"),
    State("task-assignee", "value"),
    State("task-due-date", "value"),
    State("store-project-id", "data"),
    State("store-auth-token", "data"),
    State("store-tasks", "data"),
    prevent_initial_call=True
)
def create_kanban_task(
    n_clicks,
    title,
    desc,
    priority,
    assignee,
    due_date,
    project_id,
    token,
    current_tasks
):
    if not n_clicks or not title or not project_id or not token:
        raise no_update

    payload = {
        "title": title,
        "project_id": project_id,
        "status": "todo",  # nouvelle tâche commence toujours en todo
        "priority": priority or "medium"
    }
    if desc:
        payload["description"] = desc
    if assignee:
        payload["assigned_to"] = int(assignee)
    if due_date:
        payload["due_date"] = due_date

    try:
        resp = requests.post(
            "http://127.0.0.1:8000/tasks",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )

        if resp.status_code in (200, 201):
            new_task = resp.json()
            current_tasks = current_tasks or []
            current_tasks.append(new_task)
            alert = dbc.Alert(
                f"Tâche '{title}' créée avec succès !",
                color="success",
                dismissable=True,
                duration=4000
            )
            return False, current_tasks, alert

        else:
            return no_update, no_update, dbc.Alert(
                f"Erreur création : {resp.status_code} - {resp.text[:100]}...",
                color="danger",
                dismissable=True
            )

    except Exception as e:
        return no_update, no_update, dbc.Alert(
            f"Erreur réseau : {str(e)}",
            color="danger",
            dismissable=True
        )


# ───────────────────────────────────────────────
# 3. Drag & drop : détection du changement de statut
# ───────────────────────────────────────────────
@callback(
    Output("store-tasks", "data", allow_duplicate=True),
    Output("kanban-alert", "children", allow_duplicate=True),
    Input("kanban-grid", "layout"),  # dash_draggable layout change après drag
    State("store-tasks", "data"),
    State("store-auth-token", "data"),
    State("store-project-id", "data"),
    prevent_initial_call=True
)
def handle_kanban_drag_drop(new_layout, tasks, token, project_id):
    """
    Détecte quand une tâche est déplacée entre colonnes et met à jour le statut via PATCH
    """
    if not new_layout or not tasks or not token or not project_id:
        raise no_update

    # Trouver quelle tâche a bougé et vers quelle colonne
    moved_task_id = None
    new_status = None

    status_map = {0: "todo", 1: "in_progress", 2: "review", 3: "done"}

    for item in new_layout:
        if item.get("i", "").startswith("task-"):
            task_id_str = item["i"].replace("task-", "")
            try:
                task_id = int(task_id_str)
            except ValueError:
                continue

            col_index = item["x"]  # colonne 0 → todo, 1 → in_progress, etc.
            potential_status = status_map.get(col_index)

            if potential_status:
                # Vérifier si le statut a vraiment changé
                task = next((t for t in tasks if t["id"] == task_id), None)
                if task and task["status"] != potential_status:
                    moved_task_id = task_id
                    new_status = potential_status
                    break

    if not moved_task_id or not new_status:
        raise no_update

    # PATCH au backend
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.patch(
            f"http://127.0.0.1:8000/tasks/{moved_task_id}",
            json={"status": new_status},
            headers=headers,
            timeout=5
        )

        if resp.status_code in (200, 204):
            # Mise à jour locale
            for t in tasks:
                if t["id"] == moved_task_id:
                    t["status"] = new_status
                    t["updated_at"] = datetime.utcnow().isoformat()
                    break

            alert = dbc.Alert(
                f"Tâche déplacée vers '{new_status}'",
                color="success",
                dismissable=True,
                duration=3000
            )
            return tasks, alert

        else:
            return no_update, dbc.Alert("Échec déplacement (serveur)", color="danger", dismissable=True)

    except Exception as e:
        print(f"Erreur PATCH drag & drop: {str(e)}")
        return no_update, dbc.Alert("Erreur connexion", color="danger", dismissable=True)


# ───────────────────────────────────────────────
# 4. Placeholder pour futur WebSocket (à activer quand prêt)
# ───────────────────────────────────────────────
@callback(
    Output("kanban-alert", "children", allow_duplicate=True),
    Input("refresh-interval", "n_intervals"),
    prevent_initial_call=True
)
def websocket_placeholder(n):
    # Quand WebSocket sera implémenté :
    # → détecter les événements broadcast et mettre à jour store-tasks
    return no_update  # Pour l'instant : on reste sur polling
