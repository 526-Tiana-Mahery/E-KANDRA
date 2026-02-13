# mobile/main.py
"""
Point d'entrée principal de l'application mobile E-KANDRA (Kivy + KivyMD)
"""

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp

# Pour forcer une taille mobile en développement
Window.size = (360, 740)
Window.top = 40
Window.left = 1000

# ─── Imports écrans ────────────────────────────────────────────────
from screens.login_screen import LoginScreen
from screens.dashboard_screen import DashboardScreen
from screens.team_screen import TeamScreen
from screens.project_kanban_screen import ProjectKanbanScreen

# ─── Imports composants navigation ─────────────────────────────────
from components.sidebar import SidebarContent, Sidebar

# ─── Import service auth (pour vérifier si déjà connecté) ──────────
from services.auth_service import is_user_logged_in


class E_KANDRA_App(MDApp):
    """
    Classe principale de l'application mobile E-KANDRA
    """

    def build(self):
        self.title = "E-KANDRA"
        self.icon = "assets/images/icon.png"

        # ─── Configuration du thème ────────────────────────────────────
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"          # ou "Dark"
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_hue = "600"

        # Police par défaut (optionnel si déjà dans main.kv)
        # self.theme_cls.font_name = "assets/fonts/Roboto-Regular.ttf"

        # ─── Structure principale avec Navigation Drawer ───────────────
        self.nav_layout = MDNavigationLayout()

        # ScreenManager
        self.sm = MDScreenManager(transition="FadeTransition")

        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(DashboardScreen(name="dashboard"))
        self.sm.add_widget(TeamScreen(name="team"))
        self.sm.add_widget(ProjectKanbanScreen(name="kanban"))

        # Drawer latéral
        self.sidebar_content = SidebarContent()
        self.drawer = Sidebar(content=self.sidebar_content)
        self.drawer.set_state("close")  # fermé par défaut

        # Ajout au layout principal
        self.nav_layout.add_widget(self.sm)
        self.nav_layout.add_widget(self.drawer)

        # ─── Logique de démarrage ──────────────────────────────────────
        if is_user_logged_in():
            self.sm.current = "dashboard"
        else:
            self.sm.current = "login"

        return self.nav_layout


    def on_start(self):
        print("Application E-KANDRA Mobile démarrée")
        # Option : ping backend ou refresh token ici
        # if not check_connection():
        #     self.show_snackbar("Serveur inaccessible")


    def open_drawer(self):
        """Méthode utilitaire pour ouvrir le drawer depuis n'importe où"""
        if hasattr(self, 'drawer'):
            self.drawer.set_state("open")


    def go_to(self, screen_name: str):
        """Raccourci pour changer d'écran"""
        if screen_name in self.sm.screen_names:
            self.sm.current = screen_name


if __name__ == "__main__":
    E_KANDRA_App().run()
