# mobile/components/sidebar.py

from kivy.properties import StringProperty, ListProperty
from kivy.lang import Builder

Builder.load_file(__file__.replace('.py', '.kv'))

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer

from ..services.auth_service import logout, get_current_user


class SidebarContent(MDBoxLayout):
    """
    Contenu du drawer latéral (menu)
    """

    current_user_name = StringProperty("Utilisateur")
    current_user_email = StringProperty("")
    menu_items = ListProperty([
        {"text": "Tableau de bord", "icon": "view-dashboard", "screen": "dashboard"},
        {"text": "Projets", "icon": "folder-multiple", "screen": "dashboard"},  # ou un écran liste projets
        {"text": "Équipes", "icon": "account-group", "screen": "team"},
        {"text": "Notifications", "icon": "bell-outline", "screen": None},
        {"text": "Paramètres", "icon": "cog-outline", "screen": None},
        {"text": "Déconnexion", "icon": "logout", "screen": "logout"},
    ])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        Clock.schedule_once(self.load_user_info, 0)

    def load_user_info(self, dt):
        user = get_current_user()
        if user:
            self.current_user_name = user.get("username", "Utilisateur")
            self.current_user_email = user.get("email", "")

    def on_menu_item_press(self, screen_name: str):
        """Navigation depuis le menu"""
        if screen_name == "logout":
            logout()
            self.parent.parent.parent.manager.current = "login"  # accès au ScreenManager
        elif screen_name:
            self.parent.parent.parent.manager.current = screen_name

        # Ferme le drawer après sélection
        self.parent.parent.ids.nav_drawer.set_state("close")


class Sidebar(MDNavigationDrawer):
    """Wrapper pour utiliser facilement le drawer"""
    pass
