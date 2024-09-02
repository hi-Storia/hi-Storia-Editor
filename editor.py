from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image

# Importa le altre schermate come facevi prima
from modules.arduino_tool.arduino_tool import ArduinoToolScreen
from modules.studio.studio import StudioScreen
from modules.player_creator.player_creator import PlayerCreatorScreen
from kivy.graphics import Color, Rectangle

import sys
import os

# Funzione per convertire il colore esadecimale in formato RGBA per Kivy
def hex_to_rgba(hex_color, alpha=1.0):
    hex_color = hex_color.lstrip('#')
    return [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)] + [alpha]

class InfoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Info - Crediti e informazioni", font_size=24))
        self.add_widget(layout)

class HelpScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Help - Video e link", font_size=24))
        layout.add_widget(Label(text="contatta stefano.colarelli@educational.city", font_size=17))
        self.add_widget(layout)

class HiStoriaEditorApp(App):
    def build(self):
        self.sm = ScreenManager()

        # Aggiungi tutte le schermate al ScreenManager
        self.sm.add_widget(ArduinoToolScreen(name='arduino'))
        self.sm.add_widget(StudioScreen(name='studio'))
        self.sm.add_widget(PlayerCreatorScreen(name='crea_player'))
        self.sm.add_widget(InfoScreen(name='info'))
        self.sm.add_widget(HelpScreen(name='aiuto'))

        # Determina il percorso per il logo
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        logo_path = os.path.join(base_path, 'assets', 'images', 'logo.png')

        # Layout principale
        layout = BoxLayout(orientation='vertical')

        # Menu orizzontale con logo
        menu_layout = BoxLayout(size_hint_y=0.1)

        # Logo dinamico che si adatta alle dimensioni del layout
        logo_image = Image(source=logo_path, size_hint=(None, None), allow_stretch=True, keep_ratio=True)
        menu_layout.bind(size=lambda instance, value: self.update_logo_size(instance, logo_image))
        menu_layout.add_widget(logo_image)
        
        # Aggiungi pulsanti del menu
        for menu_item in [("Studio", "studio"), ("Crea Player", "crea_player"), ("Arduino", "arduino"), ("Info", "info"), ("Aiuto", "aiuto")]:
            button = Button(text=menu_item[0], background_normal="", background_color=hex_to_rgba("#FFFFFF"), 
                            color=hex_to_rgba("#248598"), bold=True, height=60)
            button.bind(on_press=lambda btn, screen=menu_item[1]: self.switch_screen(screen))
            menu_layout.add_widget(button)

        layout.add_widget(menu_layout)
        layout.add_widget(self.sm)

        return layout
    
    def update_logo_size(self, menu_layout, logo_image):
        # Imposta la larghezza e l'altezza del logo in modo che siano proporzionali alla dimensione del layout
        logo_image.width = menu_layout.height * (214 / 58)  # Mantiene la proporzione originale del logo
        logo_image.height = menu_layout.height  # Si adatta all'altezza del layout

    def switch_screen(self, screen_name):
        if self.sm.has_screen(screen_name):
            self.sm.current = screen_name
        else:
            print(f"Schermata '{screen_name}' non trovata")

if __name__ == '__main__':
    HiStoriaEditorApp().run()
