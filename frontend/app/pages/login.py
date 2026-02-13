# frontend/app/pages/login.py
"""
Page de connexion (login)
- Formulaire simple : email/username + mot de passe
- Appel à l'API backend /auth/login
- Sauvegarde token + user dans les stores
- Redirection vers dashboard en cas de succès
"""

from dash import html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import requests
import json

# ───────────────────────────────────────────────
# Layout de la page login
# ───────────────────────────────────────────────
layout = dbc.Container([
    dbc.Row([
        dbc.Col(width=3),
        dbc.Col([
            html.H2("Connexion", className="text-center mb-4 mt-5"),
            html.Div(id="login-alert", className="mb-3"),

            dbc.Form([
                dbc.Label("Email ou Nom d'utilisateur", html_for="login-username"),
                dbc.Input(
                    id="login-username",
                    type="text",
                    placeholder="votre@email.com ou pseudo",
                    className="mb-3",
                    required=True
                ),

                dbc.Label("Mot de passe", html_for="login-password"),
                dbc.Input(
                    id="login-password",
                    type="password",
                    placeholder="********",
                    className="mb-3",
                    required=True
                ),

                dbc.Button(
                    "Se connecter",
                    id="login-btn",
                    color="primary",
                    className="w-100 mt-3",
                    n_clicks=0
                ),
            ]),

            html.Div([
                html.A("Pas de compte ? Inscrivez-vous", href="/register", className="d-block text-center mt-3")
            ])
        ], width=6),
        dbc.Col(width=3)
    ], justify="center", className="vh-100 align-items-center")
], fluid=True, className="bg-light")


# ───────────────────────────────────────────────
# Callback : gérer la connexion
# ───────────────────────────────────────────────
@callback(
    Output("login-alert", "children"),
    Output("store-auth-token", "data", allow_duplicate=True),
    Output("store-user", "data", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("login-btn", "n_clicks"),
    State("login-username", "value"),
    State("login-password", "value"),
    State("store-auth-token", "data"),
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password, current_token):
    if not n_clicks or n_clicks == 0:
        raise PreventUpdate

    if not username or not password:
        return dbc.Alert("Veuillez remplir tous les champs", color="danger", dismissable=True), no_update, no_update, no_update

    try:
        # Appel API au backend
        response = requests.post(
            "http://127.0.0.1:8000/auth/login",  # À remplacer par variable d'env plus tard
            data={
                "username": username,  # Peut être email ou username
                "password": password
            }
        )

        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]

            # Récupérer les infos user via /auth/me
            user_resp = requests.get(
                "http://127.0.0.1:8000/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )

            if user_resp.status_code == 200:
                user_data = user_resp.json()
                return (
                    dbc.Alert("Connexion réussie ! Redirection...", color="success", dismissable=False),
                    token,
                    user_data,
                    "/dashboard"
                )
            else:
                return dbc.Alert("Erreur lors de la récupération des infos utilisateur", color="danger"), no_update, no_update, no_update

        elif response.status_code == 401:
            return dbc.Alert("Identifiants incorrects", color="danger", dismissable=True), no_update, no_update, no_update
        else:
            return dbc.Alert(f"Erreur serveur : {response.status_code}", color="danger"), no_update, no_update, no_update

    except requests.exceptions.RequestException as e:
        return dbc.Alert(f"Impossible de contacter le serveur : {str(e)}", color="danger"), no_update, no_update, no_update
