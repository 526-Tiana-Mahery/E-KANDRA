# mobile/components/task_card.py

from kivy.properties import DictProperty, StringProperty, ObjectProperty
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior  # pour cliquer sur la carte

from kivymd.uix.card import MDCard
from kivymd.uix.chip import MDChip
from kivymd.uix.menu import MDDropdownMenu

Builder.load_file(__file__.replace('.py', '.kv'))

class TaskCard(MDCard, ButtonBehavior):
    """
    Carte représentant une tâche dans le Kanban
    - Affiche titre, description courte, priorité, assigné(s)
    - Clic → ouvre détails (à implémenter)
    - Drag → pour déplacer entre colonnes (MVP : via bouton ou futur drag)
    """

    task_data = DictProperty({})
    on_task_selected = ObjectProperty(None)     # callback clic → détails
    on_status_change_request = ObjectProperty(None)  # callback pour changer statut

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = "12dp"
        self.spacing = "8dp"
        self.size_hint_y = None
        self.height = "140dp"          # hauteur fixe pour uniformité
        self.elevation = 1
        self.radius = [12, 12, 12, 12]
        self.md_bg_color = (1, 1, 1, 1)

        self.bind(task_data=self.update_content)
        Clock.schedule_once(self.build_card, 0)

    def build_card(self, dt):
        """Construit ou rafraîchit le visuel de la carte"""
        self.clear_widgets()

        # Titre
        title = MDLabel(
            text=self.task_data.get('title', 'Sans titre'),
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height="32dp",
            valign="middle"
        )
        self.add_widget(title)

        # Description (tronquée)
        desc = MDLabel(
            text=self.task_data.get('description', '').strip()[:120] + ('...' if len(self.task_data.get('description', '')) > 120 else ''),
            font_style="Body",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="48dp",
            valign="top",
            markup=True
        )
        self.add_widget(desc)

        # Tags / Priorité / Assigné (chips en bas)
        bottom_layout = MDBoxLayout(
            orientation='horizontal',
            spacing="8dp",
            size_hint_y=None,
            height="36dp",
            padding=[0, 4, 0, 0]
        )

        # Priorité (chip colorée)
        priority = self.task_data.get('priority', 'Medium')
        priority_chip = MDChip(
            text=priority,
            icon="alert-circle" if priority == "High" else "alert" if priority == "Medium" else "information",
            chip_bg_color={
                "High": (0.9, 0.2, 0.2, 1),
                "Medium": (0.9, 0.6, 0.1, 1),
                "Low": (0.2, 0.7, 0.3, 1)
            }.get(priority, (0.5, 0.5, 0.5, 1)),
            text_color=(1,1,1,1),
            size_hint_x=0.4
        )
        bottom_layout.add_widget(priority_chip)

        # Assigné (avatar ou initiales)
        assigned = self.task_data.get('assigned_to', 'Non assigné')
        assigned_chip = MDChip(
            text=assigned[:2].upper() if assigned != 'Non assigné' else "NA",
            icon="account",
            size_hint_x=0.6
        )
        bottom_layout.add_widget(assigned_chip)

        self.add_widget(bottom_layout)

    def update_content(self, *args):
        """Rafraîchit quand task_data change"""
        self.build_card(0)

    def on_release(self):
        """Clic sur la carte → ouvre détails ou trigger callback"""
        if self.on_task_selected:
            self.on_task_selected(self.task_data)

    def on_touch_move(self, touch):
        """Option : détection basique de drag (à améliorer pour vrai drag & drop)"""
        # Pour MVP : on peut juste logger ou ignorer
        return super().on_touch_move(touch)

    def show_context_menu(self, touch):
        """Menu contextuel (optionnel : déplacer vers..., éditer, supprimer)"""
        menu_items = [
            {"text": f"Déplacer vers To Do",     "viewclass": "OneLineListItem", "on_release": lambda x=self: self.request_status_change("To Do")},
            {"text": f"Déplacer vers In Progress", "viewclass": "OneLineListItem", "on_release": lambda x=self: self.request_status_change("In Progress")},
            {"text": f"Déplacer vers Done",       "viewclass": "OneLineListItem", "on_release": lambda x=self: self.request_status_change("Done")},
            {"text": "Éditer tâche",              "viewclass": "OneLineListItem"},
            {"text": "Supprimer",                 "viewclass": "OneLineListItem"},
        ]
        MDDropdownMenu(caller=self, items=menu_items, width_mult=4).open()

    def request_status_change(self, new_status):
        if self.on_status_change_request:
            self.on_status_change_request(self.task_data['id'], new_status)
