# frontend/app/components/sidebar.py
"""
Composant Sidebar gauche (navigation secondaire)
- Liens rapides : Dashboard, Mes tâches, Notifications futures
- Liste des équipes où l'utilisateur est actif
- Liens vers les projets récents (optionnel)
- Responsive : se cache sur mobile ou petites résolutions
"""

from dash import html, dcc, Input, Output, callback, no_update
import dash_bootstrap_components as dbc

# ───────────────────────────────────────────────
# Layout de la sidebar
# ───────────────────────────────────────────────
layout = html.Div([
    html.Div([
        html.H5("Navigation", className="sidebar-title mb-3"),

        dbc.Nav([
            dbc.NavLink(
                [html.I(className="fas fa-home me-2"), "Dashboard"],
                href="/dashboard",
                active="exact"
            ),
            dbc.NavLink(
                [html.I(className="fas fa-tasks me-2"), "Mes tâches"],
                href="#",  # À implémenter plus tard
                disabled=True,
                className="text-muted"
            ),
            dbc.NavLink(
                [html.I(className="fas fa-bell me-2"), "Notifications"],
                href="#",
                disabled=True,
                className="text-muted"
            ),
        ], vertical=True, pills=True, className="mb-4"),

        html.Hr(),

        html.H6("Mes équipes", className="sidebar-subtitle mb-3"),
        html.Div(id="sidebar-teams-list", children=[
            html.Div("Chargement des équipes...", className="text-muted small")
        ]),

        html.Hr(),

        html.H6("Projets récents", className="sidebar-subtitle mb-3"),
        html.Div(id="sidebar-projects-recents", children=[
            html.Div("Aucun projet récent", className="text-muted small")
        ]),
    ], className="sidebar-content p-3"),

], id="sidebar", className="sidebar bg-light border-end vh-100 position-sticky top-0")


# ───────────────────────────────────────────────
# Callback : charger les équipes dans la sidebar
# ───────────────────────────────────────────────
@callback(
    Output("sidebar-teams-list", "children"),
    Input("store-auth-token", "data"),
    Input("store-user", "data")
)
def load_sidebar_teams(token, user_data):
    if not token or not user_data:
        return html.Div("Connectez-vous pour voir vos équipes", className="text-muted small")

    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get("http://127.0.0.1:8000/teams/my-teams", headers=headers)

        if resp.status_code == 200:
            teams = resp.json()

            if not teams:
                return html.Div("Aucune équipe pour le moment", className="text-muted small")

            team_links = []
            for team in teams[:5]:  # Limite à 5 pour ne pas surcharger
                team_links.append(
                    dbc.NavLink(
                        team.get("name", "Équipe sans nom"),
                        href=f"/team/{team['id']}",
                        className="small"
                    )
                )

            return team_links

        else:
            return html.Div("Erreur chargement équipes", className="text-danger small")

    except Exception:
        return html.Div("Impossible de charger les équipes", className="text-danger small")


# ───────────────────────────────────────────────
# Callback : projets récents (simulé ou via API future)
# ───────────────────────────────────────────────
@callback(
    Output("sidebar-projects-recents", "children"),
    Input("store-auth-token", "data")
)
def load_recent_projects(token):
    # Pour MVP : placeholder
    # À remplacer par appel API /projects/recent ou filtré par user
    return [
        html.Div("Projet Alpha - En cours", className="small text-muted"),
        html.Div("Campagne Pub - Deadline demain", className="small text-warning"),
        html.Div("Refonte UI - Terminé", className="small text-success"),
    ]
