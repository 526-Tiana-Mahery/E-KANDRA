# frontend/app/pages/project_kanban.py
"""
Page principale du board Kanban pour un projet spécifique
Chemin : /project/{project_id}/kanban
"""

from dash import html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import requests
from datetime import datetime

# Import du composant colonne Kanban (à créer ou adapter)
from ..components.kanban_column import render_column

# ───────────────────────────────────────────────
# Layout de la page Kanban
# ───────────────────────────────────────────────
def layout(project_id=None):
    if not project_id:
        return html.Div("ID du projet manquant", className="alert alert-danger")

    return dbc.Container([
        # Stores
        dcc.Store(id="store-project-id", data=int(project_id)),
        dcc.Store(id="store-tasks", data=[]),

        # Titre du projet
        html.H2(id="project-kanban-title", className="mt-4 mb-2"),
        html.P(id="project-kanban-desc", className="text-muted mb-4"),

        # Bouton nouvelle tâche
        dbc.Button(
            [html.I(className="fas fa-plus me-2"), "Nouvelle tâche"],
            id="new-task-btn",
            color="primary",
            className="mb-4"
        ),

        # Board Kanban (4 colonnes)
        dbc.Row([
            dbc.Col(
                render_column("todo", "À faire", [], "column-todo"),
                width=3, className="px-2"
            ),
            dbc.Col(
                render_column("in_progress", "En cours", [], "column-in-progress"),
                width=3, className="px-2"
            ),
            dbc.Col(
                render_column("review", "À valider", [], "column-review"),
                width=3, className="px-2"
            ),
            dbc.Col(
                render_column("done", "Terminé", [], "column-done"),
                width=3, className="px-2"
            ),
        ], id="kanban-board", className="g-0"),

        # Alerte feedback (drag & drop, création, erreur)
        html.Div(id="kanban-alert", className="mt-3"),

        # Modal création de tâche
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Nouvelle tâche")),
            dbc.ModalBody([
                dbc.FormFloating([
                    dbc.Input(id="task-title", placeholder="Titre de la tâche", required=True),
                    dbc.Label("Titre")
                ], className="mb-3"),

                dbc.FormFloating([
                    dbc.Textarea(id="task-desc", placeholder="Description détaillée...", rows=4),
                    dbc.Label("Description")
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col([
                        dbc.Label("Priorité"),
                        dbc.Select(
                            id="task-priority",
                            options=[
                                {"label": "Basse", "value": "low"},
                                {"label": "Moyenne", "value": "medium"},
                                {"label": "Haute", "value": "high"},
                                {"label": "Urgente", "value": "urgent"}
                            ],
                            value="medium"
                        )
                    ], width=6),

                    dbc.Col([
                        dbc.Label("Assigné à (ID utilisateur)"),
                        dbc.Input(id="task-assignee", type="number", placeholder="Optionnel")
                    ], width=6),
                ], className="mb-3"),

                dbc.FormFloating([
                    dbc.Input(id="task-due-date", type="date", placeholder="Date d'échéance"),
                    dbc.Label("Date d'échéance")
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Annuler", id="cancel-task-btn", className="me-2"),
                dbc.Button("Créer", id="confirm-task-btn", color="success")
            ])
        ], id="new-task-modal", is_open=False, size="lg"),

        # Interval pour polling (rafraîchissement périodique)
        dcc.Interval(id="refresh-interval", interval=10*1000, n_intervals=0),

    ], fluid=True, className="py-3")


# ───────────────────────────────────────────────
# Charger les infos du projet + les tâches
# ───────────────────────────────────────────────
@callback(
    Output("project-kanban-title", "children"),
    Output("project-kanban-desc", "children"),
    Output("store-tasks", "data"),
    Input("store-project-id", "data"),
    Input("store-auth-token", "data"),
    Input("refresh-interval", "n_intervals")
)
def load_project_and_tasks(project_id, token, _):
    if not project_id or not token:
        return "Projet inconnu", "", []

    headers = {"Authorization": f"Bearer {token}"}

    # Infos projet
    try:
        p_resp = requests.get(f"http://127.0.0.1:8000/projects/{project_id}", headers=headers)
        if p_resp.status_code != 200:
            return "Erreur chargement projet", "", []

        project = p_resp.json()
        title = project.get("name", "Projet sans nom")
        desc = project.get("description", "Aucune description")

    except Exception:
        return "Erreur serveur (projet)", "", []

    # Tâches du projet
    try:
        t_resp = requests.get(
            f"http://127.0.0.1:8000/tasks?project_id={project_id}",
            headers=headers
        )
        tasks = t_resp.json() if t_resp.status_code == 200 else []
    except Exception:
        tasks = []

    return title, desc, tasks


# ───────────────────────────────────────────────
# Répartir les tâches dans les colonnes + rendre les colonnes
# ───────────────────────────────────────────────
@callback(
    Output("column-todo", "children"),
    Output("column-in-progress", "children"),
    Output("column-review", "children"),
    Output("column-done", "children"),
    Input("store-tasks", "data")
)
def distribute_tasks(tasks):
    columns = {
        "todo": [],
        "in_progress": [],
        "review": [],
        "done": []
    }

    for task in tasks or []:
        status = task.get("status", "todo").lower()
        if status in columns:
            columns[status].append(task)

    return (
        render_column("todo", "À faire", columns["todo"], "column-todo"),
        render_column("in_progress", "En cours", columns["in_progress"], "column-in-progress"),
        render_column("review", "À valider", columns["review"], "column-review"),
        render_column("done", "Terminé", columns["done"], "column-done")
    )


# ───────────────────────────────────────────────
# Ouvrir / fermer le modal création tâche
# ───────────────────────────────────────────────
@callback(
    Output("new-task-modal", "is_open", allow_duplicate=True),
    Input("new-task-btn", "n_clicks"),
    Input("cancel-task-btn", "n_clicks"),
    State("new-task-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_new_task_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open


# ───────────────────────────────────────────────
# Créer une nouvelle tâche
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
    prevent_initial_call=True
)
def create_new_task(n_clicks, title, desc, priority, assignee, due_date, project_id, token):
    if not n_clicks or not title or not project_id or not token:
        return no_update, no_update, no_update

    payload = {
        "title": title,
        "project_id": project_id,
        "priority": priority or "medium"
    }
    if desc: payload["description"] = desc
    if assignee: payload["assigned_to"] = int(assignee)
    if due_date: payload["due_date"] = due_date

    try:
        resp = requests.post(
            "http://127.0.0.1:8000/tasks",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )

        if resp.status_code in (200, 201):
            new_task = resp.json()
            alert = dbc.Alert("Tâche créée avec succès !", color="success", dismissable=True, duration=4000)
            # Pour l'instant on recharge via polling/refresh
            return False, no_update, alert
        else:
            return no_update, no_update, dbc.Alert(f"Erreur {resp.status_code}: {resp.text}", color="danger")

    except Exception as e:
        return no_update, no_update, dbc.Alert(f"Erreur connexion: {str(e)}", color="danger")
