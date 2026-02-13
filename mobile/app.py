# mobile/app.py
"""
Classe principale de l'application mobile E-KANDRA
- Hérite de MDApp (KivyMD)
- Configure le thème Material Design
- Gère le ScreenManager et les transitions d'écran
- Contient les méthodes globales (changement d'écran, theme, etc.)
"""

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window

# Pour forcer une taille mobile en développement (optionnel)
Window.size = (380, 760)  # taille portrait téléphone standard

class E_KANDRA_App(MDApp):
    """
    Application principale
    """

    # Propriétés globales accessibles partout (ex: dans les .kv ou écrans)
    current_user = StringProperty("")          # username après login
    auth_token = StringProperty("")            # JWT token
    current_team_id = StringProperty("")       # équipe sélectionnée
    current_project_id = StringProperty("")    # projet sélectionné
    is_dark_theme = BooleanProperty(False)     # switch thème clair/sombre

    def build(self):
        """
        Construction de l'interface principale
        """
        # Thème global Material Design 3
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"  # ou "Dark"
        self.theme_cls.material_style = "M3"

        # Icône de l'application (à remplacer par ton vrai logo)
        self.icon = "assets/images/logo.png"

        # ScreenManager avec transition fluide
        self.sm = ScreenManager(transition=SlideTransition(duration=0.3))

        # Ajout des écrans (on les importera et créera ensuite)
        from screens.login_screen import LoginScreen
        from screens.dashboard_screen import DashboardScreen
        from screens.team_screen import TeamScreen
        from screens.project_kanban_screen import ProjectKanbanScreen

        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(DashboardScreen(name="dashboard"))
        self.sm.add_widget(TeamScreen(name="team"))
        self.sm.add_widget(ProjectKanbanScreen(name="kanban"))

        # Écran de démarrage
        self.sm.current = "login"

        return self.sm

    def on_start(self):
        """Appelé au démarrage de l'app"""
        print("E-KANDRA Mobile démarrée !")
        # Exemple : vérifier si token déjà présent dans stockage local
        # (on implémentera plus tard avec JsonStore ou secure storage)

    def on_stop(self):
        """Appelé quand l'app est fermée"""
        print("E-KANDRA Mobile fermée.")

    # Méthodes utiles globales (à appeler depuis n'importe quel écran)
    def switch_screen(self, screen_name: str):
        """Change d'écran avec animation"""
        self.sm.current = screen_name

    def switch_theme(self):
        """Alterne entre thème clair et sombre"""
        self.is_dark_theme = not self.is_dark_theme
        self.theme_cls.theme_style = "Dark" if self.is_dark_theme else "Light"

    def show_snackbar(self, message: str, duration: float = 2.5):
        """Affiche une snackbar rapide (message en bas)"""
        from kivymd.uix.snackbar import MDSnackbar
        MDSnackbar(
            text=message,
            duration=duration,
            pos_hint={"center_x": 0.5, "center_y": 0.1}
        ).open()

if __name__ == "__main__":
    E_KANDRA_App().run()
