# frontend/app/components/task_card.py
"""
Composant Task Card (carte individuelle de tâche dans le Kanban)
- Affiche : titre, extrait description, priorité (badge couleur), deadline, assigné
- Style différencié selon priorité (bordure gauche colorée)
- ID unique pour drag & drop : "task-{id}"
- Hover + curseur grab
- Compatible avec les callbacks drag & drop
"""

from dash import html
import dash_bootstrap_components as dbc
from datetime import datetime

def render(task: dict):
    """
    Génère une carte Dash pour une tâche
    task : dict provenant de l'API (id, title, description, status, priority, due_date, assigned_to...)
    """

    # Couleurs par priorité
    priority_map = {
        "low": {"badge": "success", "border": "#28a745"},
        "medium": {"badge": "info", "border": "#17a2b8"},
        "high": {"badge": "warning", "border": "#ffc107"},
        "urgent": {"badge": "danger", "border": "#dc3545"}
    }

    prio = task.get("priority", "medium")
    prio_config = priority_map.get(prio, {"badge": "secondary", "border": "#6c757d"})

    # Deadline
    due = task.get("due_date")
    due_display = "Pas de date limite"
    due_class = "text-muted small"
    if due:
        try:
            due_dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
            due_display = due_dt.strftime("%d/%m/%Y")
            if due_dt < datetime.utcnow():
                due_class = "text-danger small fw-bold"
        except:
            due_display = due[:10] if due else "Invalide"

    # Assigné (simple pour MVP)
    assigned = task.get("assigned_to")
    assigned_text = f"Assigné à #{assigned}" if assigned else "Non assigné"

    # Description tronquée + tooltip complet
    desc = task.get("description", "")
    desc_short = desc[:90] + ("..." if len(desc) > 90 else "")

    card = dbc.Card(
        dbc.CardBody(
            [
                html.H6(
                    task.get("title", "Sans titre"),
                    className="card-title mb-2 text-truncate",
                    title=task.get("title")  # tooltip complet
                ),
                html.P(
                    desc_short,
                    className="card-text small text-muted mb-3",
                    title=desc or "Aucune description"
                ),
                html.Div(
                    [
                        dbc.Badge(
                            prio.capitalize(),
                            color=prio_config["badge"],
                            className="me-2"
                        ),
                        html.Span(due_display, className=due_class)
                    ],
                    className="d-flex justify-content-between align-items-center mb-2"
                ),
                html.Small(
                    assigned_text,
                    className="text-muted d-block"
                )
            ],
            className="p-3"
        ),
        id=f"task-{task['id']}",
        className="mb-3 shadow-sm task-card",
        style={
            "cursor": "grab",
            "borderLeft": f"4px solid {prio_config['border']}",
            "transition": "transform 0.2s"
        }
    )

    return card
