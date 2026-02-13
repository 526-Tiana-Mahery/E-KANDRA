# frontend/app/components/navbar.py
"""
Composant Navbar global (haut de page)
- Visible uniquement après connexion
- Affiche logo, nom utilisateur, bouton logout
- Utilise bootstrap navbar pour responsive
"""

from dash import html, dcc, Input, Output, callback, no_update
import dash_bootstrap_components as dbc

# ───────────────────────────────────────────────
# Layout du navbar
# ───────────────────────────────────────────────
layout = dbc.NavbarSimple(
    children=[
        # Liens à gauche (optionnels pour MVP)
        dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
        # Espace pour futur menu déroulant (équipes récentes, etc.)

        # À droite : infos utilisateur + logout
        dbc.NavItem(
            dbc.NavLink(
                id="user-display",
                href="#",
                className="d-flex align-items-center"
            )
        ),
        dbc.NavItem(
            dbc.Button(
                [html.I(className="fas fa-sign-out-alt me-2"), "Déconnexion"],
                id="logout-btn",
                color="outline-danger",
                size="sm",
                className="ms-3"
            )
        ),
    ],
    brand="E-KANDRA",
    brand_href="/dashboard",
    color="dark",
    dark=True,
    sticky="top",
    expand="lg",
    className="shadow-sm",
    id="navbar"  # Pour pouvoir cacher/afficher via callback dans main.py
)


# ───────────────────────────────────────────────
# Callback : afficher le nom de l'utilisateur connecté dans le navbar
# ───────────────────────────────────────────────
@callback(
    Output("user-display", "children"),
    Input("store-user", "data")
)
def update_user_display(user_data):
    if not user_data:
        return no_update

    username = user_data.get("username", "Utilisateur")
    full_name = user_data.get("full_name")

    display_text = full_name if full_name else username

    return [
        html.I(className="fas fa-user-circle me-2 fa-lg"),
        html.Span(f"{display_text}", className="fw-bold")
    ]


# ───────────────────────────────────────────────
# Note : la logique de déconnexion est déjà dans main.py (callback logout)
# → Elle vide les stores et redirige vers /login
