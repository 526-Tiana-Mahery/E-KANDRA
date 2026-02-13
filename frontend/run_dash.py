# frontend/run_dash.py
"""
Lanceur dédié pour l'application Dash
- Permet de lancer Dash indépendamment du backend
- Options utiles : debug, port personnalisé, host, rechargement auto
- Utilise python-dotenv pour charger .env si besoin (ex: variables API_URL)
- À lancer dans un terminal séparé du backend
"""

import os
from dotenv import load_dotenv
from frontend.app.main import app  # Importe l'app Dash créée dans main.py

# ───────────────────────────────────────────────
# Chargement des variables d'environnement (optionnel)
# ───────────────────────────────────────────────
load_dotenv()  # Charge .env à la racine du projet si présent

# Variables utiles (exemple : URL du backend pour les appels API depuis Dash)
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")
print(f"Configuration Dash → Backend API ciblé : {BACKEND_API_URL}")

# ───────────────────────────────────────────────
# Options de lancement (personnalisables)
# ───────────────────────────────────────────────
if __name__ == "__main__":
    # Port par défaut pour Dash (différent de FastAPI pour éviter conflit)
    PORT = int(os.getenv("DASH_PORT", 8050))
    HOST = os.getenv("DASH_HOST", "0.0.0.0")  # 0.0.0.0 pour accès depuis réseau local
    DEBUG = os.getenv("DASH_DEBUG", "True").lower() == "true"

    print(f"Lancement Dash sur http://{HOST}:{PORT}")
    print(f"Mode debug : {DEBUG}")
    print("Accédez à l'interface : http://localhost:8050 (ou votre IP locale)")
    print("Swagger API backend : http://localhost:8000/docs")

    app.run_server(
        debug=DEBUG,
        port=PORT,
        host=HOST,
        dev_tools_ui=True,           # Barre d'outils dev Dash
        dev_tools_props_check=True,  # Vérifie les props des composants
        use_reloader=DEBUG           # Auto-reload quand code Dash change
    )
