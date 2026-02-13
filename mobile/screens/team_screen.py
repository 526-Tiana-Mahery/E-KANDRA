# mobile/screens/team_screen.py

from kivy.properties import StringProperty, NumericProperty, ListProperty, DictProperty
from kivy.lang import Builder

Builder.load_file(__file__.replace('.py', '.kv'))

from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineAvatarListItem, IconLeftWidget
from kivymd.uix.snackbar import MDSnackbar

# Services
from ..services.api_service import get_team_details, get_team_members


class TeamScreen(MDScreen):
    """
    Écran de détails d'une équipe
    - Affiche nom, description, membres, projets liés
    - Possibilité d'inviter, quitter, etc. (MVP minimal)
    """

    team_id = StringProperty("")           # ex: "t1" ou UUID selon backend
    team_name = StringProperty("Équipe sans nom")
    team_description = StringProperty("")
    member_count = NumericProperty(0)
    members = ListProperty([])             # liste de dicts {id, username, role, avatar?}
    projects_linked = ListProperty([])     # liste de projets associés

    def on_enter(self):
        """Chargement quand l'écran devient visible"""
        if not self.team_id:
            self.show_message("Aucune équipe sélectionnée")
            self.manager.current = "dashboard"
            return

        self.load_team_data()

    def load_team_data(self):
        """Récupère les infos de l'équipe via API"""
        try:
            # Détails généraux
            team_data = get_team_details(self.team_id)
            self.team_name = team_data.get("name", "Équipe inconnue")
            self.team_description = team_data.get("description", "")
            self.member_count = team_data.get("member_count", 0)

            # Membres
            members_data = get_team_members(self.team_id)
            self.members = members_data.get("members", [])

            # Projets liés (optionnel selon ton backend)
            # projects_data = get_team_projects(self.team_id)
            # self.projects_linked = projects_data.get("projects", [])

        except Exception as e:
            print(f"Erreur chargement équipe: {e}")
            self.show_message("Impossible de charger les données de l'équipe")

    def show_message(self, text: str, duration: int = 3):
        MDSnackbar(
            text=text,
            pos_hint={"center_x": .5, "center_y": .1},
            duration=duration
        ).open()

    def invite_member(self):
        """Action placeholder pour inviter quelqu'un"""
        self.show_message("Fonctionnalité d'invitation en cours de développement", 4)

    def leave_team(self):
        """Quitter l'équipe (confirmation à ajouter en prod)"""
        self.show_message("Vous avez quitté l'équipe (simulation)")
        self.manager.current = "dashboard"

    def go_to_member_profile(self, member_id):
        """Placeholder pour profil membre"""
        self.show_message(f"Profil de l'utilisateur {member_id} (à implémenter)")
