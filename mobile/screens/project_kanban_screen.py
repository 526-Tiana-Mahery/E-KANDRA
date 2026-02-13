# mobile/screens/project_kanban_screen.py

from kivy.properties import StringProperty, NumericProperty, ListProperty, ObjectProperty
from kivy.lang import Builder
from kivy.clock import Clock

Builder.load_file(__file__.replace('.py', '.kv'))

from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar

# Imports des composants réutilisables
from ..components.kanban_column import KanbanColumn
from ..components.task_card import TaskCard

# Services
from ..services.api_service import get_project_tasks, create_task, update_task_status
from ..services.websocket_service import WebSocketService


class ProjectKanbanScreen(MDScreen):
    """
    Écran Kanban pour un projet spécifique
    """

    project_id = NumericProperty(0)
    project_name = StringProperty("Projet sans nom")
    project_description = StringProperty("")

    columns = ListProperty([])          # liste des noms de colonnes, ex: ["To Do", "In Progress", "Done"]
    tasks_by_column = ObjectProperty({}) # dict { "To Do": [task1, task2], ... }

    ws_service = ObjectProperty(None)

    def on_enter(self):
        """Chargé à chaque fois que l'écran est affiché"""
        if self.project_id == 0:
            self.show_error("Aucun projet sélectionné")
            self.manager.current = "dashboard"
            return

        self.load_project_data()
        self.connect_websocket()

    def on_leave(self):
        """Quand on quitte l'écran"""
        if self.ws_service:
            self.ws_service.disconnect()

    def load_project_data(self):
        """Récupère les tâches du projet via API"""
        try:
            data = get_project_tasks(self.project_id)
            self.project_name = data.get("name", "Projet inconnu")
            self.project_description = data.get("description", "")

            # Normalement ton backend renvoie les tâches groupées ou non
            # Ici on simule / organise par statut
            tasks = data.get("tasks", [])
            self.organize_tasks(tasks)

        except Exception as e:
            self.show_error(f"Erreur chargement projet : {str(e)}")

    def organize_tasks(self, tasks_list):
        """Regroupe les tâches par colonne/statut"""
        self.tasks_by_column = {"To Do": [], "In Progress": [], "Done": []}
        
        for task in tasks_list:
            status = task.get("status", "To Do")
            if status not in self.tasks_by_column:
                self.tasks_by_column[status] = []
            self.tasks_by_column[status].append(task)

        # Force refresh des colonnes dans le KV
        self.columns = list(self.tasks_by_column.keys())

    def connect_websocket(self):
        """Connexion WebSocket pour mises à jour en temps réel"""
        try:
            self.ws_service = WebSocketService()
            self.ws_service.connect(
                on_message=self.on_ws_message,
                on_error=self.on_ws_error,
                channel=f"project_{self.project_id}"
            )
        except Exception as e:
            print(f"WebSocket non disponible : {e}")

    def on_ws_message(self, message):
        """Callback WebSocket - mise à jour reçue"""
        if message.get("type") == "task_update":
            task = message.get("task")
            if task:
                self.update_task_in_ui(task)
                Clock.schedule_once(lambda dt: self.show_snack(f"Tâche '{task['title']}' mise à jour"))

    def update_task_in_ui(self, updated_task):
        """Déplace ou met à jour une tâche dans les colonnes"""
        task_id = updated_task["id"]
        new_status = updated_task["status"]

        # Trouver et supprimer l'ancienne version
        for col_tasks in self.tasks_by_column.values():
            for i, t in enumerate(col_tasks):
                if t["id"] == task_id:
                    del col_tasks[i]
                    break

        # Ajouter dans la nouvelle colonne
        if new_status not in self.tasks_by_column:
            self.tasks_by_column[new_status] = []
        self.tasks_by_column[new_status].append(updated_task)

        # Refresh affichage
        self.columns = []   # trick pour forcer refresh
        self.columns = list(self.tasks_by_column.keys())

    def show_error(self, msg):
        MDSnackbar(text=msg, duration=4).open()

    def show_snack(self, msg):
        MDSnackbar(text=msg, duration=2).open()

    def add_new_task(self):
        """Ouvre un dialog ou va vers un écran de création"""
        # Pour MVP : simulation rapide
        new_task = {
            "id": 999,
            "title": "Nouvelle tâche",
            "description": "À compléter...",
            "status": "To Do",
            "priority": "Medium"
        }
        create_task(self.project_id, new_task)
        self.show_snack("Tâche créée (simulation)")

    def on_task_status_change(self, task_id, new_status):
        """Appelé par drag & drop ou clic sur menu"""
        update_task_status(task_id, new_status)
        # Le websocket devrait renvoyer la mise à jour → on_ws_message gère le refresh
