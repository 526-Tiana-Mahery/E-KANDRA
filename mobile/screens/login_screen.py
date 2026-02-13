# mobile/screens/login_screen.py

from kivy.properties import StringProperty
from kivy.lang import Builder

# Charge automatiquement le fichier .kv du même nom
Builder.load_file(__file__.replace('.py', '.kv'))

from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar

# À adapter selon ton organisation réelle
try:
    from ..services.auth_service import login_user, save_auth_token
except ImportError:
    # Pour tests / développement isolé
    def login_user(email, password):
        # Simulation pour tester l'interface
        if email and password:
            return True, {"access_token": "fake-jwt-token-123"}
        return False, {"detail": "Identifiants incorrects"}

    def save_auth_token(token):
        print(f"[DEBUG] Token sauvegardé (simulation) : {token}")


class LoginScreen(MDScreen):
    """
    Écran de connexion
    """

    error_text = StringProperty("")

    def on_enter(self):
        """Quand l'écran devient visible"""
        self.ids.email.focus = True
        self.error_text = ""

    def attempt_login(self):
        """Appelé quand on clique sur le bouton Se connecter"""
        email = self.ids.email.text.strip()
        password = self.ids.password.text.strip()

        if not email or not password:
            self.error_text = "Veuillez remplir les deux champs"
            return

        self.error_text = ""
        # Option : désactiver le bouton pendant la requête
        # self.ids.btn_login.disabled = True

        try:
            success, result = login_user(email, password)

            if success:
                token = result.get("access_token") or result.get("token")
                if token:
                    save_auth_token(token)

                # Option : petite notification de succès
                MDSnackbar(
                    text="Connexion réussie !",
                    pos_hint={"center_x": .5, "center_y": .1},
                    duration=2,
                ).open()

                # Passage à l'écran principal
                self.manager.current = "dashboard"

                # Option : direction de la transition
                # self.manager.transition.direction = "left"

            else:
                error_msg = result.get("detail", "Erreur de connexion")
                self.error_text = error_msg

        except Exception as e:
            self.error_text = f"Problème réseau : {str(e)}"

        # finally:
        #     self.ids.btn_login.disabled = False

    def clear_error(self):
        """Efface le message d'erreur quand l'utilisateur tape"""
        self.error_text = ""
