# frontend/app/pages/team.py
"""
Page de vue d'une équipe (/team/{team_id})
- Affiche infos équipe (nom, desc, propriétaire)
- Liste des projets avec stats rapides (tâches todo/in_progress/done)
- Bouton "Créer un projet"
- Aperçu des membres (simplifié pour MVP)
"""

from dash import html, dcc, Input, Output, State, callback, no_update, MATCH, ALL
import dash_bootstrap_components as dbc
import requests
from dash.dependencies import Input as InputState

# ───────────────────────────────────────────────
# Layout de la page team
# ───────────────────────────────────────────────
def layout(team_id=None):
    """
    Layout dynamique avec team_id passé via URL
    """
    return dbc.Container([
        dcc.Location(id="team-location", refresh=False),
        dcc.Store(id="store-team-id", data=team_id),

        html.H2(id="team-title", className="mt-4 mb-3"),
        html.P(id="team-description", className="text-muted mb-4"),

        dbc.Row([
            dbc.Col([
                html.H4("Projets", className="mb-3"),
                dbc.Button(
                    [html.I(className="fas fa-plus me-2"), "Nouveau projet"],
                    id="create-project-btn",
                    color="success",
                    className="mb-4",
                    n_clicks=0
                ),
                html.Div(id="projects-list"),
            ], width=9),

            dbc.Col([
                html.H5("Membres", className="mb-3"),
                html.Div(id="team-members-list", className="list-group"),
            ], width=3),
        ]),

        # Modal création projet
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Nouveau projet")),
            dbc.ModalBody([
                dbc.Form([
                    dbc.Label("Nom du projet", html_for="project-name"),
                    dbc.Input(id="project-name", type="text", placeholder="ex: Refonte site web"),

                    dbc.Label("Description (optionnel)", html_for="project-desc", className="mt-3"),
                    dbc.Textarea(id="project-desc", placeholder="Objectifs, deadline...", rows=4),
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Annuler", id="cancel-project-btn", className="ms-auto"),
                dbc.Button("Créer", id="confirm-project-btn", color="primary")
            ])
        ], id="create-project-modal", is_open=False),
    ], fluid=True, className="py-4")


# ───────────────────────────────────────────────
# Callback : charger les infos de l'équipe + projets + membres
# ───────────────────────────────────────────────
@callback(
    Output("team-title", "children"),
    Output("team-description", "children"),
    Output("projects-list", "children"),
    Output("team-members-list", "children"),
    Input("store-auth-token", "data"),
    Input("store-team-id", "data")
)
def load_team_data(token, team_id):
    if not token or not team_id:
        return "Équipe non trouvée", "", [], []

    try:
        headers = {"Authorization": f"Bearer {token}"}

        # Récupérer infos équipe
        team_resp = requests.get(f"http://127.0.0.1:8000/teams/{team_id}", headers=headers)
        if team_resp.status_code != 200:
            return "Erreur chargement équipe", "", [], []

        team = team_resp.json()

        # Récupérer projets de l'équipe (route à créer)
        projects_resp = requests.get(f"http://127.0.0.1:8000/projects?team_id={team_id}", headers=headers)
        projects = projects_resp.json() if projects_resp.status_code == 200 else []

        # Récupérer membres (simulé ou route future)
        members_resp = requests.get(f"http://127.0.0.1:8000/teams/{team_id}/members", headers=headers)
        members = members_resp.json() if members_resp.status_code == 200 else [{"username": "Vous (propriétaire)"}]

        # Titre et desc
        title = f"{team['name']} ({'Propriétaire' if team['owner_id'] == team.get('current_user_id') else 'Membre'})"
        desc = team.get("description", "Aucune description disponible.")

        # Cartes projets
        project_cards = []
        for proj in projects:
            card = dbc.Card([
                dbc.CardBody([
                    html.H5(proj["name"], className="card-title"),
                    html.P(proj.get("description", "")[:100] + "...", className="card-text text-muted"),
                    html.Small(f"Statut : {proj['status']}", className="text-muted d-block"),
                    dbc.Button(
                        "Ouvrir Kanban",
                        href=f"/project/{proj['id']}/kanban",
                        color="primary",
                        size="sm",
                        className="mt-3"
                    )
                ])
            ], className="mb-3 shadow-sm")

            project_cards.append(card)

        # Liste membres (simple)
        members_list = [html.Div(m.get("username", "Utilisateur inconnu"), className="list-group-item") for m in members]

        return title, desc, project_cards, members_list

    except Exception as e:
        print(f"Erreur chargement équipe {team_id}: {e}")
        return "Erreur", "", [dbc.Alert("Impossible de charger les données.", color="danger")], []


# ───────────────────────────────────────────────
# Callback : toggle modal création projet
# ───────────────────────────────────────────────
@callback(
    Output("create-project-modal", "is_open"),
    Input("create-project-btn", "n_clicks"),
    Input("cancel-project-btn", "n_clicks"),
    State("create-project-modal", "is_open")
)
def toggle_project_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open


# ───────────────────────────────────────────────
# Callback : créer un projet dans l'équipe
# ───────────────────────────────────────────────
@callback(
    Output("create-project-modal", "is_open", allow_duplicate=True),
    Output("projects-list", "children", allow_duplicate=True),
    Input("confirm-project-btn", "n_clicks"),
    State("project-name", "value"),
    State("project-desc", "value"),
    State("store-auth-token", "data"),
    State("store-team-id", "data"),
    prevent_initial_call=True
)
def create_project(n_clicks, name, desc, token, team_id):
    if not n_clicks or not name or not team_id:
        raise PreventUpdate

    try:
        payload = {
            "name": name,
            "team_id": team_id
        }
        if desc:
            payload["description"] = desc

        response = requests.post(
            "http://127.0.0.1:8000/projects",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code in (200, 201):
            return False, no_update  # Rechargement via load_team_data
        else:
            return no_update, dbc.Alert("Erreur création projet", color="danger")

    except Exception:
        return no_update, dbc.Alert("Erreur serveur", color="danger")
