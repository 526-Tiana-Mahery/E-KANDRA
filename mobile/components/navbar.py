# mobile/components/navbar.py

from kivy.properties import StringProperty, NumericProperty
from kivy.lang import Builder
from kivy.clock import Clock

Builder.load_file(__file__.replace('.py', '.kv'))

from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.behaviors import TouchBehavior


class NavBar(MDBottomNavigation):
    """
    Barre de navigation inférieure fixe
    - Icônes + labels pour les écrans principaux
    - Gère le changement d'écran actif
    - Peut être stylée globalement via main.kv
    """

    current_screen_name = StringProperty("dashboard")
    badge_count = NumericProperty(0)  # ex: notifications non lues

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.panel_color = (1, 1, 1, 1)
        self.selected_color = self.theme_cls.primary_color
        self.text_color = (0.4, 0.4, 0.4, 1)
        self.elevation = 8

        Clock.schedule_once(self.build_items, 0)

    def build_items(self, dt):
        """Crée les items de la barre (peut être dynamique plus tard)"""
        self.clear_widgets()

        items = [
            {"name": "dashboard", "text": "Accueil", "icon": "view-dashboard", "badge": 0},
            {"name": "kanban",    "text": "Projets", "icon": "view-kanban",    "badge": 2},
            {"name": "team",      "text": "Équipes", "icon": "account-group",  "badge": 0},
            {"name": "profile",   "text": "Profil",  "icon": "account-circle", "badge": 0},
        ]

        for item_data in items:
            item = MDBottomNavigationItem(
                name=item_data["name"],
                text=item_data["text"],
                icon=item_data["icon"],
                badge_icon="numeric",
                badge_icon_text=str(item_data["badge"]) if item_data["badge"] > 0 else "",
            )
            item.bind(on_tab_press=self.on_tab_press)
            self.add_widget(item)

        # Sélectionne l'onglet actif au démarrage
        self.switch_tab(self.current_screen_name)

    def on_tab_press(self, item):
        """Quand un onglet est cliqué"""
        screen_name = item.name

        # Navigation vers l'écran correspondant
        if screen_name in self.manager.screen_names:
            self.manager.current = screen_name
            self.current_screen_name = screen_name
        else:
            print(f"Écran '{screen_name}' non trouvé")

    def update_badge(self, screen_name: str, count: int):
        """Met à jour le badge d'un onglet spécifique"""
        for item in self.get_items():
            if item.name == screen_name:
                item.badge_icon_text = str(count) if count > 0 else ""
                break


# Raccourci pour accéder à la navbar depuis l'app
# Exemple d'utilisation dans un écran :
# app.navbar.update_badge("kanban", 3)
