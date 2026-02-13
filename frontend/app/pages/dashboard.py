# frontend/app/pages/dashboard.py
"""
Page Dashboard principal (après connexion)
- Liste les équipes de l'utilisateur (propriétaire ou membre)
- Aperçu rapide par équipe (projets, tâches en cours, etc.)
- Bouton "Créer une équipe"
- Liens vers les équipes et projets
"""

from dash import html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import requests
from datetime import datetime

# ───────────────────────────────────────────────
# Layout du dashboard
# ───────────────────────────────────────────────
layout = dbc.Container([
    html.H2("Tableau de bord", className="mt-4 mb-4"),

    # Alerte / message d'accueil
    html.Div(id="dashboard-welcome", className="mb-4"),

    # Bouton créer équipe
    dbc.Button(
        [html.I(className="fas fa-plus me-2"), "Créer une nouvelle équipe"],
        id="create-team-btn",
        color="primary",
        className="mb-4",
        n_clicks=0
    ),

    # Liste des équipes (cartes)
    dbc.Row(id="teams-list", className="g-4"),

    # Modal pour créer une équipe (apparait au clic sur le bouton)
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Nouvelle équipe")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Label("Nom de l'équipe", html_for="team-name"),
                dbc.Input(id="team-name", type="text", placeholder="ex: Équipe Marketing 2026"),

                dbc.Label("Description (optionnel)", html_for="team-desc", className="mt-3"),
                dbc.Textarea(id="team-desc", placeholder="Objectif de l'équipe...", rows=3),
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Annuler", id="cancel-team-btn", className="ms-auto", n_clicks=0),
            dbc.Button("Créer", id="confirm-team-btn", color="primary", n_clicks=0)
        ])
    ], id="create-team-modal", is_open=False),
], fluid=True, className="py-4")


# ───────────────────────────────────────────────
# Callback : charger les équipes de l'utilisateur connecté
# ───────────────────────────────────────────────
@callback(
    Output("teams-list", "children"),
    Output("dashboard-welcome", "children"),
    Input("store-auth-token", "data"),
    Input("store-user", "data")
)
def load_teams(token, user_data):
    if not token or not user_data:
        return no_update, no_update

    user_id = user_data.get("id")
    welcome_msg = html.Div([
        html.H4(f"Bonjour {user_data.get('username', 'Utilisateur')}", className="mb-2"),
        html.P("Voici vos équipes actives. Créez-en une nouvelle ou cliquez sur une équipe pour voir ses projets.")
    ])

    try:
        # Appel API pour récupérer les équipes (à implémenter dans backend/api/teams.py)
        # Pour l'instant : placeholder (simulé ou erreur si pas encore implémenté)
        response = requests.get(
            "http://127.0.0.1:8000/teams/my-teams",  # Route à créer plus tard
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            teams = response.json()  # liste d'objets {id, name, description, owner_id, ...}

            if not teams:
                return (
                    dbc.Alert("Vous n'avez pas encore d'équipe. Créez-en une !", color="info"),
                    welcome_msg
                )

            team_cards = []
            for team in teams:
                card = dbc.Card([
                    dbc.CardBody([
                        html.H5(team.get("name", "Équipe sans nom"), className="card-title"),
                        html.P(team.get("description", "Aucune description"), className="card-text text-muted"),
                        html.Small(f"Créée le {team.get('created_at', 'inconnu')}", className="text-muted"),
                        dbc.Button(
                            "Ouvrir l'équipe",
                            href=f"/team/{team['id']}",
                            color="primary",
                            size="sm",
                            className="mt-3"
                        )
                    ])
                ], className="shadow-sm h-100")

                team_cards.append(dbc.Col(card, width=4, lg=3))

            return dbc.Row(team_cards), welcome_msg

        else:
            return dbc.Alert("Impossible de charger vos équipes pour le moment.", color="warning"), welcome_msg

    except Exception as e:
        print(f"Erreur chargement équipes: {e}")
        return dbc.Alert("Erreur de connexion au serveur.", color="danger"), welcome_msg


# ───────────────────────────────────────────────
# Callback : ouvrir/fermer le modal de création d'équipe
# ───────────────────────────────────────────────
@callback(
    Output("create-team-modal", "is_open"),
    Input("create-team-btn", "n_clicks"),
    Input("cancel-team-btn", "n_clicks"),
    State("create-team-modal", "is_open")
)
def toggle_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open


# ───────────────────────────────────────────────
# Callback : créer une nouvelle équipe (appel API)
# ───────────────────────────────────────────────
@callback(
    Output("create-team-modal", "is_open", allow_duplicate=True),
    Output("teams-list", "children", allow_duplicate=True),
    Input("confirm-team-btn", "n_clicks"),
    State("team-name", "value"),
    State("team-desc", "value"),
    State("store-auth-token", "data"),
    prevent_initial_call=True
)
def create_team(n_clicks, name, desc, token):
    if not n_clicks or not name:
        raise PreventUpdate

    try:
        payload = {"name": name}
        if desc:
            payload["description"] = desc

        response = requests.post(
            "http://127.0.0.1:8000/teams",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code in (200, 201):
            # Fermer modal + recharger la liste
            return False, no_update  # Le callback load_teams se déclenchera via refresh du store ou polling
        else:
            # Gérer erreur (ex: nom déjà pris)
            return no_update, dbc.Alert("Erreur lors de la création.", color="danger")

    except Exception:
        return no_update, dbc.Alert("Erreur serveur.", color="danger")
