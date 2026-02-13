# mobile/components/kanban_column.py

from kivy.properties import StringProperty, ListProperty, NumericProperty, ObjectProperty
from kivy.lang import Builder
from kivy.uix.behaviors import DragBehavior

from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout

Builder.load_file(__file__.replace('.py', '.kv'))

from ..components.task_card import TaskCard


class KanbanColumn(MDCard):
    """
    Une colonne Kanban réutilisable
    - Affiche un titre, un compteur de tâches
    - Contient des TaskCard
    - Accepte le drop d'une tâche (changement de statut)
    """

    column_name = StringProperty("To Do")
    tasks = ListProperty([])                  # liste des dicts de tâches
    task_count = NumericProperty(0)
    on_task_dropped = ObjectProperty(None)    # callback quand une tâche est droppée ici

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.elevation = 1
        self.radius = [12, 12, 12, 12]
        self.padding = [0, 0, 0, 0]
        self.spacing = 0
        self.md_bg_color = (0.96, 0.96, 0.98, 1)  # gris très clair

        self.bind(tasks=self.update_task_count)
        Clock.schedule_once(self.build_content, 0)

    def build_content(self, dt):
        """Construit dynamiquement le contenu quand l'objet est prêt"""
        self.clear_widgets()

        # Header
        header = MDBoxLayout(
            orientation='horizontal',
            padding=[16, 12, 16, 12],
            spacing=8,
            size_hint_y=None,
            height="48dp",
            md_bg_color=(0.92, 0.92, 0.96, 1)
        )

        title = MDLabel(
            text=self.column_name,
            font_style="H6",
            bold=True,
            size_hint_x=0.7
        )
        count = MDLabel(
            text=f"{len(self.tasks)}",
            halign="right",
            theme_text_color="Secondary",
            size_hint_x=0.3
        )

        header.add_widget(title)
        header.add_widget(count)
        self.add_widget(header)

        # Zone des tâches (scrollable si beaucoup)
        scroll = ScrollView(size_hint=(1, 1))
        tasks_layout = MDBoxLayout(
            orientation='vertical',
            padding=[8, 8, 8, 8],
            spacing=12,
            size_hint_y=None,
            adaptive_height=True
        )

        for task_data in self.tasks:
            card = TaskCard(task_data=task_data)
            tasks_layout.add_widget(card)

        scroll.add_widget(tasks_layout)
        self.add_widget(scroll)

    def update_task_count(self, *args):
        self.task_count = len(self.tasks)
        # Pour rafraîchir le header si déjà construit
        if hasattr(self, 'children') and len(self.children) > 0:
            header = self.children[-1]  # header est le dernier ajouté (premier visuellement)
            if isinstance(header, MDBoxLayout) and len(header.children) == 2:
                count_label = header.children[0]  # right-aligned
                count_label.text = str(self.task_count)

    def on_touch_down(self, touch):
        """Accepte le drop si c'est une tâche qui est dragguée"""
        if super().on_touch_down(touch):
            return True

        # Logique drag & drop basique (à combiner avec DragBehavior si besoin)
        # Pour MVP : on peut juste détecter le drop via le parent ou un event global
        return False

    def add_task_widget(self, task_card):
        """Ajoute une carte quand drop ici (appelée depuis le drag manager)"""
        # À implémenter selon ta stratégie de drag & drop
        # Exemple simple :
        self.ids.tasks_layout.add_widget(task_card)  # si tu ajoutes un id dans le kv
        self.tasks.append(task_card.task_data)
        if self.on_task_dropped:
            self.on_task_dropped(task_card.task_data['id'], self.column_name)
