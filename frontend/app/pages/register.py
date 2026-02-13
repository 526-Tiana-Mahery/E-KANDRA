# frontend/app/pages/register.py
"""
Page d'inscription (register)
- Formulaire : email, username, mot de passe, nom complet (optionnel)
- Appel à l'API backend /auth/register
- Redirection vers /login après succès
- Gestion des erreurs (email déjà pris, username déjà pris, etc.)
"""

from dash import html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import requests

# ───────────────────────────────────────────────
# Layout de la page register
# ───────────────────────────────────────────────
layout = dbc.Container([
    dbc.Row([
        dbc.Col(width=3),
        dbc.Col([
            html.H2("Inscription", className="text-center mb-4 mt-5"),
            html.Div(id="register-alert", className="mb-3"),

            dbc.Form([
                dbc.Label("Email", html_for="register-email"),
                dbc.Input(
                    id="register-email",
                    type="email",
                    placeholder="votre@email.com",
                    className="mb-3",
                    required=True
                ),

                dbc.Label("Nom d'utilisateur", html_for="register-username"),
                dbc.Input(
                    id="register-username",
                    type="text",
                    placeholder="pseudo (3-50 caractères)",
                    className="mb-3",
                    required=True
                ),

                dbc.Label("Mot de passe", html_for="register-password"),
                dbc.Input(
                    id="register-password",
                    type="password",
                    placeholder="Minimum 8 caractères",
                    className="mb-3",
                    required=True
                ),

                dbc.Label("Nom complet (optionnel)", html_for="register-fullname"),
                dbc.Input(
                    id="register-fullname",
                    type="text",
                    placeholder="Prénom Nom",
                    className="mb-3"
                ),

                dbc.Button(
                    "Créer mon compte",
                    id="register-btn",
                    color="success",
                    className="w-100 mt-3",
                    n_clicks=0
                ),
            ]),

            html.Div([
                html.A("Déjà un compte ? Connectez-vous", href="/login", className="d-block text-center mt-3")
            ])
        ], width=6),
        dbc.Col(width=3)
    ], justify="center", className="vh-100 align-items-center")
], fluid=True, className="bg-light")


# ───────────────────────────────────────────────
# Callback : gérer l'inscription
# ───────────────────────────────────────────────
@callback(
    Output("register-alert", "children"),
    Output("url", "pathname", allow_duplicate=True),
    Input("register-btn", "n_clicks"),
    State("register-email", "value"),
    State("register-username", "value"),
    State("register-password", "value"),
    State("register-fullname", "value"),
    prevent_initial_call=True
)
def handle_register(n_clicks, email, username, password, full_name):
    if not n_clicks or n_clicks == 0:
        raise PreventUpdate

    # Validation côté client basique
    if not email or not username or not password:
        return dbc.Alert("Veuillez remplir les champs obligatoires", color="danger", dismissable=True), no_update

    if len(password) < 8:
        return dbc.Alert("Le mot de passe doit contenir au moins 8 caractères", color="danger"), no_update

    try:
        payload = {
            "email": email,
            "username": username,
            "password": password,
        }
        if full_name:
            payload["full_name"] = full_name

        response = requests.post(
            "http://127.0.0.1:8000/auth/register",  # À rendre configurable via .env
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            return (
                dbc.Alert(
                    "Compte créé avec succès ! Vous allez être redirigé vers la connexion...",
                    color="success",
                    dismissable=False,
                    duration=4000
                ),
                "/login"
            )

        elif response.status_code == 400:
            error_detail = response.json().get("detail", "Erreur inconnue")
            return dbc.Alert(error_detail, color="danger", dismissable=True), no_update

        else:
            return dbc.Alert(f"Erreur serveur ({response.status_code})", color="danger"), no_update

    except requests.exceptions.RequestException as e:
        return dbc.Alert(f"Impossible de contacter le serveur : {str(e)}", color="danger"), no_update
