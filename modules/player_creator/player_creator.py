from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.core.text import LabelBase
from .ui_components import show_add_track_popup, show_edit_track_popup, show_edit_intro_track_popup, show_error_popup, show_info_popup, show_export_confirmation
from .image_manager import ImageManager
import os
import shutil
import json
from .languages import iso_639_1_languages  # Importa la mappa delle lingue
from .levels import level_mapping  # Importa la mappa dei livelli

# Caricamento del font DejaVu Sans
import sys
import os
from tkinter import Tk, filedialog
import shutil

# Determina il percorso delle risorse in base all'ambiente
if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

# Caricamento del font DejaVu Sans
font_path = os.path.join(base_path, 'assets', 'fonts', 'DejaVuSans.ttf')
LabelBase.register(name='DejaVuSans', fn_regular=font_path)

from .ui_components import show_add_track_popup, show_edit_track_popup, show_add_intro_track_popup
from .project_manager import ProjectManager
from .languages import iso_639_1_languages


class TrackBox(BoxLayout):
    def __init__(self, track, index, screen, **kwargs):
        super(TrackBox, self).__init__(**kwargs)
        self.track = track
        self.index = index
        self.screen = screen
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 60

        # Imposta il colore di sfondo
        with self.canvas.before:
            Color(1, 1, 1, 1)  # Sfondo bianco per le tracce regolari
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(pos=self.update_rect, size=self.update_rect)

        self.build_content()

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def build_content(self):
        self.clear_widgets()

        # Track information
        subtitle_status = "Sub: Caricato" if self.track["subtitle_file"] else "Sub: Auto"
        track_info = f"Traccia {self.index}: {self.track['title']} - {subtitle_status}"
        self.track_info_label = Label(text=track_info, size_hint_x=0.4, color=(0, 0, 0, 1))  # Testo nero
        self.add_widget(self.track_info_label)

        # Move up button (nascosto se è la prima traccia)
        if self.index > 2:
            move_up_button = Button(text="\u2191", size_hint_x=None, width=50, font_name='DejaVuSans')  # Freccia in su
            move_up_button.bind(on_press=lambda instance: self.screen.move_track_up(self.index))
            self.add_widget(move_up_button)

        # Move down button (nascosto se è l'ultima traccia)
        total_tracks = len(self.screen.project_manager.projects[self.screen.current_project]["tracks"])
        if self.index < total_tracks + 1:
            move_down_button = Button(text="\u2193", size_hint_x=None, width=50, font_name='DejaVuSans')  # Freccia in giù
            move_down_button.bind(on_press=lambda instance: self.screen.move_track_down(self.index))
            self.add_widget(move_down_button)

        # Edit button
        edit_button = Button(text="Modifica", size_hint_x=None, width=80)
        edit_button.bind(on_press=lambda instance: self.screen.edit_track(self.track))
        self.add_widget(edit_button)

        # Delete button
        delete_button = Button(text="Elimina", size_hint_x=None, width=80)
        delete_button.bind(on_press=lambda instance: self.screen.delete_track(self.track))
        self.add_widget(delete_button)


class PlayerCreatorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_manager = ProjectManager()
        self.image_manager = ImageManager(self.project_manager)
        self.current_project = None
        self.confirm_popup = None
        self.introduction_track_custom = False  # Per tracciare se l'utente ha caricato una traccia personalizzata

        # Determina il percorso del file dell'immagine
        if hasattr(sys, '_MEIPASS'):
            # Quando viene eseguito con PyInstaller, sys._MEIPASS contiene il percorso della directory temporanea
            background_image_path = os.path.join(sys._MEIPASS, 'assets', 'images', 'background-player.png')
        else:
            # Quando viene eseguito come script Python, usa il percorso relativo alla directory corrente
            background_image_path = os.path.join(base_path, 'assets', 'images', 'background-player.png')

        # Aggiungi l'immagine di sfondo al layout principale
        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)  # Colore di default bianco
            self.bg_rect = Rectangle(source=background_image_path, size=self.size, pos=self.pos)
            self.bind(pos=self.update_bg_rect, size=self.update_bg_rect)

        # Check for existing projects
        self.project_manager.load_projects_from_file()
        if not self.project_manager.projects:
            self.show_create_project_or_variant()
        else:
            self.show_dashboard()

    def update_bg_rect(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def show_dashboard(self):
        self.clear_widgets()

        dashboard_layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        dashboard_layout.bind(minimum_height=dashboard_layout.setter('height'))

        title_label = Label(text="Audioguide Esistenti", font_size=32, bold=True, color=(0, 0, 0, 1), size_hint_y=None, height=50)
        dashboard_layout.add_widget(title_label)

        has_projects = len(self.project_manager.projects) > 0

        if has_projects:
            first_project_name = list(self.project_manager.projects.keys())[0]
            first_project = self.project_manager.projects[first_project_name]

            for project_name, project in self.project_manager.projects.items():
                project_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=100)

                image_source = project.get("image", "assets/images/default.jpg")
                project_image = Image(source=image_source, size_hint_x=None, width=100)
                project_box.add_widget(project_image)

                info_box = BoxLayout(orientation='vertical')
                info_box.add_widget(Label(text=project_name, font_size=24, bold=True))
                info_box.add_widget(Label(text=f"Autore: {project['general']['author']}", font_size=18))
                info_box.add_widget(Label(text=f"Livello: {project['general']['level']}, Lingua: {project['general']['language']}", font_size=18))

                num_tracks = len([track for track in project["tracks"] if track["track_number"] > 1])
                info_box.add_widget(Label(text=f"Tracce: {num_tracks}", font_size=18))
                project_box.add_widget(info_box)

                buttons_box = BoxLayout(orientation='vertical', size_hint_x=0.3)
                edit_button = Button(text="Modifica", size_hint_y=None, height=40)
                edit_button.bind(on_press=lambda instance, pname=project_name: self.edit_project(pname))
                buttons_box.add_widget(edit_button)

                delete_button = Button(text="Elimina", size_hint_y=None, height=40)
                delete_button.bind(on_press=lambda instance, pname=project_name: self.show_delete_confirmation(pname))
                buttons_box.add_widget(delete_button)

                project_box.add_widget(buttons_box)
                dashboard_layout.add_widget(project_box)

            # Controlla se ci sono immagini già caricate per il progetto
            if "images" in first_project and first_project["images"]:
                load_images_button = Button(text="Modifica fotogallery", size_hint_y=None, height=50)
                load_images_button.bind(on_press=lambda instance: self.show_image_gallery(first_project_name))
            else:
                load_images_button = Button(text="Crea fotogallery", size_hint_y=None, height=50)
                load_images_button.bind(on_press=lambda instance: self.load_images_for_project(first_project_name))
            
            # Crea un BoxLayout orizzontale per affiancare i due pulsanti
            buttons_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)

            new_level_lang_button = Button(text="Crea nuovo livello/lingua", size_hint_y=None, height=50)
            new_level_lang_button.bind(on_press=lambda instance: self.show_create_project_or_variant(
                original_project_name=first_project_name,
                is_variant=True
            ))

            # Imposta entrambi i pulsanti con size_hint_x=0.5
            buttons_row.add_widget(new_level_lang_button)
            buttons_row.add_widget(load_images_button)

            # Aggiungi la riga con i due pulsanti al layout della dashboard
            dashboard_layout.add_widget(buttons_row)

        else:
            new_project_button = Button(text="Crea Nuova Audioguida", size_hint_y=None, height=50)
            new_project_button.bind(on_press=lambda instance: self.show_create_project_or_variant(is_variant=False))
            dashboard_layout.add_widget(new_project_button)

        # Pulsante di esportazione che occupa l'intera larghezza
        export_button = Button(text="Esporta Audioguida", size_hint_y=None, height=50)
        export_button.bind(on_press=lambda instance: show_export_confirmation(self, self.export_audioguide))

        # Aggiungi il pulsante di esportazione al layout della dashboard con larghezza piena
        dashboard_layout.add_widget(export_button)
        
        scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        scroll_view.add_widget(dashboard_layout)
        self.add_widget(scroll_view)

    def show_create_project_or_variant(self, original_project_name=None, is_variant=False):
        self.clear_widgets()

        root_layout = RelativeLayout()
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=5, size_hint_y=None)
        self.main_layout.bind(minimum_height=self.main_layout.setter('height'))

        title_label = Label(text="Crea Nuovo Livello/Lingua" if is_variant else "Crea Prima Audioguida", font_size=32, bold=True, color=(0, 0, 0, 1), size_hint_y=None, height=50)
        self.main_layout.add_widget(title_label)

        # Se è una variante, usa i valori dell'audioguida originale come placeholder
        if is_variant and original_project_name:
            original_project = self.project_manager.projects[original_project_name]
            project_name_input = TextInput(text=original_project_name, multiline=False, size_hint_y=None, height=40)
            project_name_input.disabled = True  # Disabilitato per mantenere il nome invariato
            project_author_input = TextInput(text=original_project['general']['author'], multiline=False, size_hint_y=None, height=40)
            project_author_input.disabled = True  # Disabilitato per mantenere l'autore invariato
        else:
            project_name_input = TextInput(hint_text="Nome Audioguida", multiline=False, size_hint_y=None, height=40)
            project_author_input = TextInput(hint_text="Autore", multiline=False, size_hint_y=None, height=40)

        self.main_layout.add_widget(project_name_input)
        self.main_layout.add_widget(project_author_input)

        # Layout orizzontale per lingua e livello
        horizontal_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)

        # Spinner per la lingua
        language_spinner = Spinner(
            text="Seleziona lingua",
            values=list(iso_639_1_languages.values()),
            size_hint_x=0.5  # Occupa metà dello spazio orizzontale
        )
        horizontal_layout.add_widget(language_spinner)

        # Spinner per il livello
        level_spinner = Spinner(
            text="Seleziona livello",
            values=["Base", "Per bambini", "Per non vedenti", "Per adolescenti", "Per esperti"],
            size_hint_x=0.5  # Occupa metà dello spazio orizzontale
        )
        horizontal_layout.add_widget(level_spinner)

        # Aggiungi il layout orizzontale al layout principale
        self.main_layout.add_widget(horizontal_layout)

        # Pulsante per creare la variante o audioguida
        create_button = Button(text="Crea Variante" if is_variant else "Crea Audioguida", size_hint_y=None, height=50)
        create_button.bind(on_press=lambda instance: self.create_project_or_variant(
            original_project_name if is_variant else project_name_input.text,
            project_author_input.text,
            language_spinner.text,
            level_spinner.text,
            is_variant=is_variant
        ))
        self.main_layout.add_widget(create_button)

        # Aggiungi il pulsante "Torna alla Dashboard" solo se siamo in modalità variante
        if is_variant:
            back_button = Button(text="Torna alla Dashboard", size_hint_y=None, height=40)
            back_button.bind(on_press=lambda instance: self.show_dashboard())
            self.main_layout.add_widget(back_button)

        scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        scroll_view.add_widget(self.main_layout)
        root_layout.add_widget(scroll_view)

        self.add_widget(root_layout)

    def create_project_or_variant(self, name, author, language, level, is_variant=False):
        # Verifica che sia stata selezionata una lingua e un livello
        if language == "Seleziona lingua" or level == "Seleziona livello":
            show_error_popup("Errore", "Devi selezionare sia una lingua che un livello.")
            return

        # Se è una variante, verifica che lingua e livello siano diversi dall'originale
        if is_variant:
            original_project = self.project_manager.projects[name]
            # Verifica se la lingua e il livello sono uguali all'originale
            if language == original_project['general']['language'] and level == original_project['general']['level']:
                show_error_popup("Errore", "Stai selezionando la stessa versione dell'audioguida originale.")
                return

        # Creazione del progetto o della variante
        self.project_manager.create_new_project(name, author, language, level, is_variant=is_variant)
        self.show_dashboard()

    def create_variant(self, original_project_name, name, language, level):
        original_project = self.project_manager.projects[original_project_name]
        
        # Controlla se la lingua e il livello sono uguali a quelli dell'originale
        if language == original_project['general']['language'] and level == original_project['general']['level']:
            show_error_popup("Errore", "Stai selezionando la stessa versione dell'audioguida originale.")
        else:
            # Crea una nuova variante
            self.project_manager.create_new_project(name, original_project['general']['author'], language, level)
            self.show_dashboard()

    def show_editor(self):
        self.clear_widgets()

        tab_panel = TabbedPanel(do_default_tab=False)

        for level, languages in self.project_manager.get_levels_and_languages(self.current_project).items():
            for language in languages:
                tab = TabbedPanelItem(text=f"{level} - {language}")

                # Il contenitore per tutto il contenuto audio
                audio_layout = BoxLayout(orientation='vertical', padding=5, spacing=5, size_hint_y=None)
                audio_layout.bind(minimum_height=audio_layout.setter('height'))  # Importante per lo scorrimento

                # Aggiungi il pulsante "Aggiungi Traccia"
                add_track_button = Button(text="Aggiungi Traccia", size_hint_y=None, height=40)
                audio_layout.add_widget(add_track_button)

                # Binding per aggiungere tracce
                add_track_button.bind(on_press=lambda instance: show_add_track_popup(self))

                # Mostra la traccia introduttiva
                self.show_introduction_track(audio_layout)

                # Layout per tracce
                track_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
                track_layout.bind(minimum_height=track_layout.setter('height'))  # Permette lo scorrimento verticale

                # Aggiungi le tracce
                self.display_tracks(track_layout)

                # Aggiungi il track_layout all'audio_layout
                audio_layout.add_widget(track_layout)

                # Usa un ScrollView per contenere l'audio_layout
                scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
                scroll_view.add_widget(audio_layout)

                tab.content = scroll_view  # Aggiungi lo ScrollView al tab
                tab_panel.add_widget(tab)

        # Aggiungi il TabbedPanel al layout principale
        self.add_widget(tab_panel)

        # Pulsante per tornare alla dashboard
        back_button = Button(text="Torna alla Dashboard", size_hint_y=None, height=40)
        back_button.bind(on_press=lambda instance: self.show_dashboard())
        self.add_widget(back_button)

    def show_introduction_track(self, parent_layout):
        # Introduzione Box Layout
        intro_layout = BoxLayout(orientation='horizontal', padding=10, spacing=10, size_hint_y=None, height=60)

        # Ottieni la traccia introduttiva per il progetto corrente
        intro_track = self.project_manager.get_intro_track(self.current_project)

        if intro_track:  # Situazione 2: Traccia personalizzata caricata
            intro_label = Label(text="Traccia 1 (Intro) personalizzata caricata", font_size=18, color=(1, 1, 1, 1), size_hint_x=0.6)
            intro_layout.add_widget(intro_label)

            # Pulsante "Cambia" per caricare una nuova traccia
            change_button = Button(text="Cambia", size_hint_x=None, width=140)
            change_button.bind(on_press=lambda instance: show_add_intro_track_popup(self))
            intro_layout.add_widget(change_button)

            # Pulsante "Rimuovi e usa predefinita"
            remove_button = Button(text="Rimuovi e usa predefinita", size_hint_x=None, width=280)
            remove_button.bind(on_press=lambda instance: self.delete_intro_track(intro_layout))
            intro_layout.add_widget(remove_button)

        else:  # Situazione 1: Usa traccia predefinita
            # Crea un layout orizzontale per il testo e il checkbox, senza margini e padding
            intro_label_layout = BoxLayout(orientation='horizontal', size_hint_x=0.6, padding=(200, 0), spacing=0)

            # Aggiungi il label per la traccia introduttiva
            intro_label = Label(text="Traccia 1 (Intro)", font_size=18, color=(1, 1, 1, 1), size_hint_x=None, width=200)
            intro_label_layout.add_widget(intro_label)

            # Checkbox per utilizzare la traccia predefinita inline con il testo, senza margini extra
            use_default_checkbox = CheckBox(active=True, size_hint_x=None, width=60)
            intro_label_layout.add_widget(use_default_checkbox)

            # Aggiungi un secondo label per il testo che segue il checkbox, senza margini extra
            use_default_label = Label(text="Usa traccia predefinita", font_size=18, color=(1, 1, 1, 1), size_hint_x=None, width=150)
            intro_label_layout.add_widget(use_default_label)

            # Aggiungi il layout con il checkbox e il testo alla riga dell'introduzione
            intro_layout.add_widget(intro_label_layout)

            # Funzione che mostra/nasconde il popup quando il checkbox viene deselezionato
            def toggle_upload_button(checkbox, value):
                if not value:
                    show_add_intro_track_popup(self, on_popup_dismiss=lambda: self.check_intro_track_popup_result(checkbox))

            use_default_checkbox.bind(active=toggle_upload_button)

        parent_layout.add_widget(intro_layout)

    def check_intro_track_popup_result(self, checkbox):
        # Verifica se è stata caricata una traccia personalizzata. Se no, ripristina il checkbox.
        intro_track = self.project_manager.get_intro_track(self.current_project)
        if not intro_track:
            checkbox.active = True

    def show_intro_edit_delete_buttons(self, intro_layout):
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)

        # Modifica la traccia introduttiva
        edit_button = Button(text="Modifica", size_hint_x=None, width=80)
        edit_button.bind(on_press=lambda instance: show_edit_intro_track_popup(self))  # Funzione separata per l'introduzione
        button_layout.add_widget(edit_button)

        # Elimina la traccia introduttiva personalizzata
        delete_button = Button(text="Elimina", size_hint_x=None, width=80)
        delete_button.bind(on_press=lambda instance: self.delete_intro_track(intro_layout))
        button_layout.add_widget(delete_button)

        intro_layout.add_widget(button_layout)

    def delete_intro_track(self, intro_layout):
        # Elimina la traccia introduttiva del progetto corrente
        self.project_manager.delete_intro_track(self.current_project)
        self.introduction_track_custom = False
        intro_layout.clear_widgets()
        self.show_introduction_track(intro_layout)

    def display_tracks(self, track_layout):
        track_layout.clear_widgets()

        # Ordina le tracce per numero di traccia e assegna il nuovo indice
        tracks = sorted(self.project_manager.projects[self.current_project]["tracks"], key=lambda t: t["track_number"])

        for i, track in enumerate(tracks):
            track_box = TrackBox(track, i + 2, self)
            track_layout.add_widget(track_box)

    def move_track_up(self, index):
        tracks = self.project_manager.projects[self.current_project]["tracks"]
        if index > 2:
            tracks[index - 2], tracks[index - 3] = tracks[index - 3], tracks[index - 2]
            self.update_track_numbers(tracks)
            self.project_manager.save_projects_to_file()
            self.show_editor()

    def move_track_down(self, index):
        tracks = self.project_manager.projects[self.current_project]["tracks"]
        if index < len(tracks) + 1:
            tracks[index - 2], tracks[index - 1] = tracks[index - 1], tracks[index - 2]
            self.update_track_numbers(tracks)
            self.project_manager.save_projects_to_file()
            self.show_editor()

    def update_track_numbers(self, tracks):
        for i, track in enumerate(tracks, start=2):
            track["track_number"] = i

    def edit_project(self, project_name):
        self.current_project = project_name
        self.show_editor()

    def edit_track(self, track):
        show_edit_track_popup(self, track)

    def delete_track(self, track):
        self.project_manager.projects[self.current_project]["tracks"].remove(track)
        self.project_manager.save_projects_to_file()
        self.show_editor()

    def add_language_or_level(self, project_name):
        pass

    def show_delete_confirmation(self, project_name):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f"Sei sicuro di voler eliminare l'audioguida '{project_name}'?"))

        confirm_button = Button(text="Conferma", size_hint_y=None, height=40)
        confirm_button.bind(on_press=lambda instance: self.delete_project(project_name))
        content.add_widget(confirm_button)

        cancel_button = Button(text="Annulla", size_hint_y=None, height=40)
        cancel_button.bind(on_press=lambda instance: self.confirm_popup.dismiss())
        content.add_widget(cancel_button)

        self.confirm_popup = Popup(title="Conferma Eliminazione", content=content, size_hint=(0.75, 0.5))
        self.confirm_popup.open()

    def delete_project(self, project_name):
        self.project_manager.delete_project(project_name)
        self.confirm_popup.dismiss()
        self.show_dashboard()

    def load_images_for_project(self, project_name):
        result = self.image_manager.load_images_for_project(project_name)
        
        # Gestisci i vari casi di ritorno
        if result == "Nessuna immagine selezionata.":
            # Opzionalmente puoi mostrare un messaggio di notifica, ma non è un errore critico
            show_info_popup("Info", result)
        elif "Errore" in result:
            show_error_popup("Errore", result)
        else:
            show_info_popup("Successo", result)
            # Aggiorna la dashboard dopo il caricamento delle immagini
            self.show_dashboard()

    def show_image_gallery(self, project_name):
        self.clear_widgets()

        project = self.project_manager.projects.get(project_name)

        # Conta il numero di immagini già caricate
        images = project.get("images", [])
        num_images = len(images)
        remaining_slots = 10 - num_images

        gallery_layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        gallery_layout.bind(minimum_height=gallery_layout.setter('height'))

        title_label = Label(text="Modifica Immagini", font_size=32, bold=True, color=(0, 0, 0, 1), size_hint_y=None, height=50)
        gallery_layout.add_widget(title_label)

        # Visualizza le immagini già caricate
        image_grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        image_grid.bind(minimum_height=image_grid.setter('height'))

        for image_path in images:
            image_box = BoxLayout(orientation='vertical', size_hint_y=None, height=300)
            img = Image(source=os.path.join(self.project_manager.project_base_dir, project_name, image_path), size_hint=(None, None), size=(200, 200))
            image_box.add_widget(img)

            # Aggiungi solo il pulsante "Elimina"
            delete_button = Button(text="Elimina", size_hint_y=None, height=40)
            delete_button.bind(on_press=lambda instance, img_path=image_path: self.delete_image_and_update_gallery(project_name, img_path))
            image_box.add_widget(delete_button)

            image_grid.add_widget(image_box)

        gallery_layout.add_widget(image_grid)

        # Pulsante per caricare altre immagini
        if remaining_slots > 0:
            load_more_button = Button(
                text=f"Carica altre immagini ({remaining_slots} disponibili)",
                size_hint_y=None,
                height=50,
            )
            load_more_button.bind(on_press=lambda instance: self.load_more_images(project_name, remaining_slots))
        else:
            load_more_button = Button(
                text="Limite massimo immagini",
                size_hint_y=None,
                height=50,
                disabled=True
            )
        gallery_layout.add_widget(load_more_button)

        # Pulsante per tornare alla dashboard
        back_button = Button(text="Torna alla Dashboard", size_hint_y=None, height=50)
        back_button.bind(on_press=lambda instance: self.show_dashboard())
        gallery_layout.add_widget(back_button)

        scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        scroll_view.add_widget(gallery_layout)
        self.add_widget(scroll_view)

    def delete_image_and_update_gallery(self, project_name, img_path):
        # Chiama la funzione delete_image di ImageManager
        self.image_manager.delete_image(project_name, img_path)
        # Aggiorna la galleria per riflettere l'eliminazione
        self.show_image_gallery(project_name)

    def load_more_images(self, project_name, remaining_slots):
        result = self.image_manager.load_images_for_project(project_name, remaining_slots)
        
        # Aggiorna la galleria dopo aver caricato altre immagini
        if "Errore" in result:
            show_error_popup("Errore", result)
        else:
            show_info_popup("Successo", result)
            self.show_image_gallery(project_name)

    def create_empty_srt(self, file_path):
        """Funzione per creare un file .srt vuoto."""
        with open(file_path, 'w') as srt_file:
            srt_file.write("")
    
    def export_audioguide(self, error_message_label):
        if error_message_label.text:  # Se esiste un messaggio di errore, interrompi l'esportazione
            return

        # Directory di esportazione principale
        export_base_dir = os.path.join(base_path, "projects")

        # Se la directory non esiste, creala
        if not os.path.exists(export_base_dir):
            os.makedirs(export_base_dir)

        # Verifica se esistono directory già presenti
        existing_dirs = [d for d in os.listdir(export_base_dir) if os.path.isdir(os.path.join(export_base_dir, d))]

        # Se ci sono directory esistenti, mostra un popup di conferma
        if existing_dirs:
            self.show_delete_confirmation_popup(export_base_dir)
        else:
            self.perform_export()

    def show_delete_confirmation_popup(self, export_base_dir):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Lista delle directory già esistenti con lingua e livello completi
        dir_descriptions = []

        # Itera sulle directory di lingua
        for language_dir in os.listdir(export_base_dir):
            language_path = os.path.join(export_base_dir, language_dir)
            if os.path.isdir(language_path):
                # Itera sulle sottodirectory dei livelli
                for level_dir in os.listdir(language_path):
                    level_path = os.path.join(language_path, level_dir)
                    if os.path.isdir(level_path):
                        # Ottieni i nomi completi di lingua e livello
                        language_full = iso_639_1_languages.get(language_dir, language_dir)
                        level_full = level_mapping.get(level_dir, level_dir)

                        # Aggiungi la descrizione completa alla lista
                        dir_descriptions.append(f"{language_full}, livello {level_full}")

        # Testo che avvisa l'utente delle directory esistenti
        if dir_descriptions:
            content.add_widget(Label(text=f"Sono presenti vecchie audioguide nelle seguenti lingue e livelli:\n{', '.join(dir_descriptions)}"))
            content.add_widget(Label(text="Vuoi cancellare queste audioguide e procedere con l'esportazione?"))

            # Pulsante di conferma
            confirm_button = Button(text="Procedi", size_hint_y=None, height=50)
            confirm_button.bind(on_press=lambda _: self.confirm_delete_and_export())
            content.add_widget(confirm_button)

            # Pulsante di annullamento
            cancel_button = Button(text="Annulla", size_hint_y=None, height=50)
            cancel_button.bind(on_press=lambda _: self.cancel_export())
            content.add_widget(cancel_button)

            # Crea e mostra il popup
            popup = Popup(title="Conferma Eliminazione Audioguide", content=content, size_hint=(0.75, 0.5))
            popup.open()
            self.confirmation_popup = popup
        else:
            # Non ci sono directory esistenti, procedi con l'esportazione direttamente
            self.perform_export()

    def confirm_delete_and_export(self):
        # Cancella le vecchie directory di esportazione
        export_base_dir = os.path.join(base_path, "projects")
        for dir_name in os.listdir(export_base_dir):
            dir_path = os.path.join(export_base_dir, dir_name)
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path)

        # Procedi con l'esportazione
        self.perform_export()
        
        # Chiudi il popup di conferma
        self.confirmation_popup.dismiss()

    def cancel_export(self):
        # Chiudi il popup senza fare nulla
        self.confirmation_popup.dismiss()

    def perform_export(self):
        # Il codice esistente per l'esportazione delle audioguide
        export_base_dir = os.path.join(base_path, "projects")

        for project_name, project in self.project_manager.projects.items():
            # Codice della lingua
            language_code = None
            for code, name in iso_639_1_languages.items():
                if name == project['general']['language']:
                    language_code = code
                    break
            
            if language_code is None:
                show_error_popup("Errore", f"Codice lingua non trovato per '{project['general']['language']}'")
                return

            # Directory per la lingua
            language_dir = os.path.join(export_base_dir, language_code)
            if not os.path.exists(language_dir):
                os.makedirs(language_dir)
            
            # Codice del livello
            level_code = None
            for code, level in level_mapping.items():
                if level == project['general']['level']:
                    level_code = code
                    break
            
            if level_code is None:
                show_error_popup("Errore", f"Codice livello non trovato per '{project['general']['level']}'")
                return

            level_dir = os.path.join(language_dir, level_code)
            if not os.path.exists(level_dir):
                os.makedirs(level_dir)
            
            # Inizializza la lista delle tracce per il file JSON
            tracks_json = []

            # Gestione della traccia introduttiva
            track_number = 1
            if project['intro_track']:
                # Traccia introduttiva personalizzata
                intro_audio_dest = os.path.join(level_dir, f"{track_number}.mp3")
                shutil.copy(project['intro_track']['audio_file'], intro_audio_dest)
                if project['intro_track']['subtitle_file']:
                    shutil.copy(project['intro_track']['subtitle_file'], os.path.join(level_dir, f"{track_number}.srt"))
                else:
                    # Crea un file .srt vuoto se il sottotitolo non è presente
                    self.create_empty_srt(os.path.join(level_dir, f"{track_number}.srt"))
                
                tracks_json.append({
                    "track_number": track_number,
                    "title": "Introduzione",
                    "subtitle_file": f"{track_number}.srt"
                })
            else:
                # Usa la traccia e il sottotitolo predefiniti
                default_intro_audio = os.path.join(base_path, "assets", "audio", "1.mp3")
                default_intro_srt = os.path.join(base_path, "assets", "audio", "1.srt")
                
                shutil.copy(default_intro_audio, os.path.join(level_dir, f"{track_number}.mp3"))
                if os.path.exists(default_intro_srt):
                    shutil.copy(default_intro_srt, os.path.join(level_dir, f"{track_number}.srt"))
                else:
                    self.create_empty_srt(os.path.join(level_dir, f"{track_number}.srt"))

                tracks_json.append({
                    "track_number": track_number,
                    "title": "Introduzione",
                    "subtitle_file": f"{track_number}.srt"
                })
            
            track_number += 1

            # Gestione delle altre tracce dell'audioguida
            for track in sorted(project["tracks"], key=lambda t: t["track_number"]):
                audio_dest = os.path.join(level_dir, f"{track_number}.mp3")
                shutil.copy(track['audio_file'], audio_dest)
                
                if track['subtitle_file']:
                    shutil.copy(track['subtitle_file'], os.path.join(level_dir, f"{track_number}.srt"))
                else:
                    # Crea un file .srt vuoto se il sottotitolo non è presente
                    self.create_empty_srt(os.path.join(level_dir, f"{track_number}.srt"))
                
                tracks_json.append({
                    "track_number": track_number,
                    "title": track['title'],
                    "subtitle_file": f"{track_number}.srt"
                })
                
                track_number += 1
            
            # Aggiungi la traccia 99 (sempre inclusa)
            track_99_audio = os.path.join(base_path, "assets", "audio", "99.mp3")
            shutil.copy(track_99_audio, os.path.join(level_dir, "99.mp3"))
            
            track_99_subtitle = os.path.join(base_path, "assets", "audio", "99.srt")
            if os.path.exists(track_99_subtitle):
                shutil.copy(track_99_subtitle, os.path.join(level_dir, "99.srt"))
            else:
                self.create_empty_srt(os.path.join(level_dir, "99.srt"))

            tracks_json.append({
                "track_number": 99,
                "title": "Attenzione!",
                "subtitle_file": "99.srt"
            })

            # Creazione del file description.json
            description_json = {
                "title": project_name,
                "author": project['general']['author'],
                "level": project['general']['level'],
                "level_description": level_mapping[level_code],  # Utilizza il livello descritto dalla mappa
                "tracks": tracks_json,
                "images": [{"id": str(i+1), "image": img} for i, img in enumerate(project.get("images", []))]
            }

            with open(os.path.join(level_dir, "description.json"), 'w') as json_file:
                json.dump(description_json, json_file, indent=4)

            # Esportazione delle immagini del progetto nella directory img
            img_dir = os.path.join(level_dir, "img")
            if not os.path.exists(img_dir):
                os.makedirs(img_dir)

            # Copia e rinumera le immagini da 1 a 10
            for i, image_path in enumerate(project.get("images", [])[:10], start=1):
                source_image = os.path.join(self.project_manager.project_base_dir, project_name, image_path)
                dest_image = os.path.join(img_dir, f"image_{i}{os.path.splitext(image_path)[1]}")
                shutil.copy(source_image, dest_image)

        show_info_popup("Esportazione", "Esportazione completata con successo!")
        self.export_popup.dismiss()
