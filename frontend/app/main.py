# frontend/app/main.py
"""
Application Dash principale pour le frontend web du gestionnaire de tâches
- Utilise dash-bootstrap-components pour un layout moderne rapide
- Support multi-pages (login, register, dashboard, team, kanban)
- Gestion d'état global via dcc.Store (token JWT, user info, current team/project)
- Appel API vers le backend FastAPI
"""

import dash
from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

# Import des pages et composants
from .pages import login, register, dashboard, team, project_kanban
from .components import navbar, sidebar

# ───────────────────────────────────────────────
# Configuration de l'application Dash
# ───────────────────────────────────────────────
app = Dash(
    __name__,
    use_pages=True,                    # Active le routing multi-pages
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,          # Thème Bootstrap
        dbc.icons.FONT_AWESOME,        # Icônes FA
        "/assets/custom.css"           # Fichier CSS custom
    ],
    suppress_callback_exceptions=True, # Évite erreurs si callbacks appellent composants non chargés
    title="E-KANDRA - Gestion de Tâches Collaborative"
)

# ───────────────────────────────────────────────
# Layout global de l'application
# ───────────────────────────────────────────────
app.layout = html.Div([
    # Stores globaux (état partagé entre pages)
    dcc.Store(id="store-user", data={}, storage_type="session"),     # Infos utilisateur + token
    dcc.Store(id="store-current-team", data=None, storage_type="session"),
    dcc.Store(id="store-current-project", data=None, storage_type="session"),
    dcc.Store(id="store-auth-token", data="", storage_type="session"),  # JWT token

    # Location pour gérer les URLs et redirections
    dcc.Location(id="url", refresh=True),

    # Layout principal
    dbc.Container([
        # Navbar en haut (visible après login)
        navbar.layout,

        dbc.Row([
            # Sidebar gauche (visible après login)
            dbc.Col(sidebar.layout, width=2, id="sidebar-col"),

            # Contenu principal (pages)
            dbc.Col(
                html.Div(id="page-content", className="p-4"),
                width=10,
                id="content-col"
            )
        ], className="g-0", id="main-row")
    ], fluid=True, className="p-0")

], id="main-app", style={"minHeight": "100vh"})


# ───────────────────────────────────────────────
# Callback principal : routing multi-pages + protection auth
# ───────────────────────────────────────────────
@callback(
    Output("page-content", "children"),
    Output("sidebar-col", "style"),
    Output("navbar", "style"),  # On ajoute un ID="navbar" dans navbar.py
    Input("url", "pathname"),
    State("store-auth-token", "data")
)
def display_page(pathname, token):
    # Si pas de token → force login
    if not token and pathname not in ["/login", "/register"]:
        return login.layout, {"display": "none"}, {"display": "none"}

    # Routing simple
    if pathname == "/login" or pathname == "/":
        return login.layout, {"display": "none"}, {"display": "none"}

    elif pathname == "/register":
        return register.layout, {"display": "none"}, {"display": "none"}

    elif pathname == "/dashboard":
        return dashboard.layout, {"display": "block"}, {"display": "block"}

    elif pathname.startswith("/team/"):
        return team.layout, {"display": "block"}, {"display": "block"}

    elif pathname.startswith("/project/"):
        return project_kanban.layout, {"display": "block"}, {"display": "block"}

    else:
        # Page 404
        return html.H1("Page non trouvée (404)", className="text-danger mt-5"), {"display": "block"}, {"display": "block"}


# ───────────────────────────────────────────────
# Callback exemple : déconnexion (à appeler depuis navbar)
# ───────────────────────────────────────────────
@callback(
    Output("store-auth-token", "data", allow_duplicate=True),
    Output("store-user", "data", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("logout-btn", "n_clicks"),  # À ajouter dans navbar.py
    prevent_initial_call=True
)
def logout(n_clicks):
    if n_clicks:
        return "", {}, "/login"
    raise PreventUpdate


# ───────────────────────────────────────────────
# Lancement de l'application (en dev)
# ───────────────────────────────────────────────
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
