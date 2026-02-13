# frontend/app/components/kanban_column.py
"""
Composant Kanban Column (une colonne du board : To Do, In Progress, Review, Done)
- Affiche titre + compteur de tâches
- Rend les cartes via task_card.py
- Style différencié par statut (couleur de fond)
- ID unique pour le drag & drop (children modifiable)
"""

from dash import html
import dash_bootstrap_components as dbc

def render(status: str, title: str, tasks: list, column_id: str):
    """
    Génère le layout d'une colonne Kanban

    Paramètres :
    - status       : "todo", "in_progress", "review", "done" (utilisé pour ID et couleur)
    - title        : texte affiché (ex: "À faire")
    - tasks        : liste de dicts tâches pour cette colonne
    - column_id    : identifiant unique pour le contenu droppable (ex: "column-todo")
    """

    # Couleurs de fond selon statut
    column_colors = {
        "todo": "#f8f9fa",         # Gris clair
        "in_progress": "#fff3cd",  # Jaune clair
        "review": "#d1ecf1",       # Bleu clair
        "done": "#d4edda"          # Vert clair
    }

    bg_color = column_colors.get(status, "#f8f9fa")

    # Compteur de tâches
    count_badge = dbc.Badge(
        str(len(tasks)),
        color="secondary",
        className="ms-2 rounded-pill",
        style={"fontSize": "0.8rem"}
    )

    # Cartes tâches (appel à ton composant task_card)
    from .task_card import render as render_task_card  # Import relatif

    task_cards = [
        render_task_card(task)
        for task in tasks
    ]

    return html.Div(
        [
            # En-tête colonne
            html.Div(
                [
                    html.H5(title, className="mb-0"),
                    count_badge
                ],
                className="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom"
            ),

            # Zone droppable (contenu modifiable par drag & drop)
            html.Div(
                task_cards,
                id=column_id,
                className="kanban-column-content flex-grow-1",
                style={
                    "minHeight": "400px",
                    "padding": "8px",
                    "borderRadius": "6px"
                }
            )
        ],
        id=f"col-wrapper-{status}",
        className="kanban-column p-3 rounded shadow-sm h-100",
        style={
            "backgroundColor": bg_color,
            "border": "1px solid #dee2e6",
            "display": "flex",
            "flexDirection": "column"
        }
    )
