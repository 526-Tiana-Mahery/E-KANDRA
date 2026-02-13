# mobile/screens/dashboard_screen.py

from kivy.properties import StringProperty, ListProperty
from kivy.lang import Builder

# Charge automatiquement le .kv correspondant (dashboard_screen.kv)
Builder.load_file(__file__.replace('.py', '.kv'))

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.list import OneLineAvatarListItem

# Imports services (à adapter selon ce que tu as déjà)
from ..services.api_service import get_user_projects, get_user_teams
# from ..services.auth_service import get_current_user


class DashboardScreen(MDScreen):
    """
    Écran d'accueil / tableau de bord après connexion
    """

    username = StringProperty("Utilisateur")
    welcome_message = StringProperty("Chargement...")
    
    recent_projects = ListProperty([])
    recent_teams = ListProperty([])

    def on_enter(self):
        """Appelé chaque fois que l'écran devient visible"""
        self.load_dashboard_data()

    def load_dashboard_data(self):
        """Récupère les données principales pour le dashboard"""
        self.welcome_message = f"Bonjour, {self.username}"

        # Exemple d'appel API (à remplacer par ta vraie implémentation)
        try:
            # Récupération des projets récents
            projects_data = get_user_projects(limit=5)
            self.recent_projects = projects_data.get("projects", [])

            # Récupération des équipes
            teams_data = get_user_teams(limit=3)
            self.recent_teams = teams_data.get("teams", [])

        except Exception as e:
            print(f"Erreur chargement dashboard: {e}")
            self.welcome_message += "\n[Erreur de chargement des données]"

    def go_to_kanban(self, project_id):
        """Navigue vers l'écran Kanban d'un projet spécifique"""
        # On peut passer des données via le screen manager si besoin
        kanban_screen = self.manager.get_screen("kanban")
        kanban_screen.project_id = project_id  # ← à implémenter dans project_kanban_screen.py
        self.manager.current = "kanban"

    def go_to_team(self, team_id):
        """Navigue vers l'écran d'une équipe"""
        team_screen = self.manager.get_screen("team")
        team_screen.team_id = team_id
        self.manager.current = "team"

    def refresh(self, *args):
        """Appelé par le PullToRefresh (si tu en mets un)"""
        self.load_dashboard_data()


# ────────────────────────────────────────────────
# Pour tester rapidement sans backend réel
# (supprime cette partie quand auth_service et api_service fonctionnent)
if "get_user_projects" not in globals():
    def get_user_projects(limit=5):
        return {
            "projects": [
                {"id": 1, "name": "Site E-commerce", "progress": 75},
                {"id": 2, "name": "App Mobile", "progress": 30},
                {"id": 3, "name": "Refonte UI", "progress": 90},
            ]
        }

    def get_user_teams(limit=3):
        return {
            "teams": [
                {"id": "t1", "name": "Équipe Dev", "members": 5},
                {"id": "t2", "name": "Designers", "members": 3},
            ]
        }
