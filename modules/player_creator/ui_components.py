from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.checkbox import CheckBox
from tkinter import Tk, filedialog

def show_add_track_popup(screen):
    content = BoxLayout(orientation='vertical', padding=10, spacing=10)

    # Campo per il nome della traccia
    track_name_input = TextInput(hint_text="Nome Traccia", multiline=False)
    content.add_widget(track_name_input)

    # Label per il file audio selezionato
    file_path_label = Label(text="Nessun file audio selezionato")
    content.add_widget(file_path_label)

    # Pulsante per selezionare file audio
    filechooser_button = Button(text="Seleziona File Audio", size_hint_y=None, height=40)
    filechooser_button.bind(on_press=lambda _: show_file_chooser_popup(file_path_label, "audio"))
    content.add_widget(filechooser_button)

    # Checkbox per selezionare se si desidera aggiungere un sottotitolo
    add_subtitle_checkbox = CheckBox()
    checkbox_label = Label(text="Vuoi aggiungere un sottotitolo?")
    checkbox_layout = BoxLayout(orientation='horizontal', spacing=10)
    checkbox_layout.add_widget(add_subtitle_checkbox)
    checkbox_layout.add_widget(checkbox_label)
    content.add_widget(checkbox_layout)

    # Label per il file di sottotitolo selezionato o messaggio di sottotitolo vuoto
    subtitle_file_label = Label(text="Nessun sottotitolo selezionato (verrà creato un sottotitolo vuoto)")
    content.add_widget(subtitle_file_label)

    # Mostra il file chooser per selezionare il file sottotitolo solo se la checkbox è selezionata
    def on_checkbox_active(checkbox, value):
        if value:
            show_file_chooser_popup(subtitle_file_label, "subtitle")
        else:
            subtitle_file_label.text = "Nessun sottotitolo selezionato (verrà creato un sottotitolo vuoto)"

    add_subtitle_checkbox.bind(active=on_checkbox_active)

    # Pulsante per salvare la traccia
    save_button = Button(text="Salva", size_hint_y=None, height=50)
    save_button.bind(on_press=lambda _: save_track(screen, track_name_input.text, file_path_label.text, subtitle_file_label.text))
    content.add_widget(save_button)

    popup = Popup(title="Aggiungi Traccia", content=content, size_hint=(0.75, 0.75))
    popup.open()
    screen.popup = popup  # Referenzia il popup per chiuderlo successivamente


def show_error_popup(title, message):
    content = BoxLayout(orientation='vertical', padding=10, spacing=10)
    content.add_widget(Label(text=message))
    popup = Popup(title=title, content=content, size_hint=(0.75, 0.5))
    popup.open()

def show_info_popup(title, message):
    content = BoxLayout(orientation='vertical', padding=10, spacing=10)
    content.add_widget(Label(text=message))
    close_button = Button(text="Chiudi", size_hint_y=None, height=40)
    content.add_widget(close_button)
    
    popup = Popup(title=title, content=content, size_hint=(0.75, 0.5))
    close_button.bind(on_press=popup.dismiss)
    popup.open()

def show_edit_track_popup(screen, track):
    content = BoxLayout(orientation='vertical', padding=10, spacing=10)

    # Campo per il nome della traccia precompilato
    track_name_input = TextInput(text=track['title'], multiline=False)
    content.add_widget(track_name_input)

    # Label per il file audio selezionato
    file_path_label = Label(text=track['audio_file'])
    content.add_widget(file_path_label)

    # Pulsante per selezionare file audio
    filechooser_button = Button(text="Cambia File Audio", size_hint_y=None, height=40)
    filechooser_button.bind(on_press=lambda _: show_file_chooser_popup(file_path_label, "audio"))
    content.add_widget(filechooser_button)

    # Checkbox per selezionare se si desidera aggiungere un sottotitolo
    add_subtitle_checkbox = CheckBox(active=bool(track['subtitle_file']))
    checkbox_label = Label(text="Vuoi aggiungere un sottotitolo?")
    checkbox_layout = BoxLayout(orientation='horizontal', spacing=10)
    checkbox_layout.add_widget(add_subtitle_checkbox)
    checkbox_layout.add_widget(checkbox_label)
    content.add_widget(checkbox_layout)

    # Label per il file di sottotitolo selezionato o messaggio di sottotitolo vuoto
    subtitle_file_label = Label(text=track['subtitle_file'] if track['subtitle_file'] else "Nessun sottotitolo selezionato (verrà creato un sottotitolo vuoto)")
    content.add_widget(subtitle_file_label)

    def on_checkbox_active(checkbox, value):
        if value:
            show_file_chooser_popup(subtitle_file_label, "subtitle")
        else:
            subtitle_file_label.text = "Nessun sottotitolo selezionato (verrà creato un sottotitolo vuoto)"

    add_subtitle_checkbox.bind(active=on_checkbox_active)

    # Pulsante per salvare la traccia modificata
    save_button = Button(text="Salva Modifiche", size_hint_y=None, height=50)
    save_button.bind(on_press=lambda _: save_track(screen, track_name_input.text, file_path_label.text, subtitle_file_label.text, track))
    content.add_widget(save_button)

    popup = Popup(title="Modifica Traccia", content=content, size_hint=(0.75, 0.75))
    popup.open()
    screen.popup = popup  # Referenzia il popup per chiuderlo successivamente

def show_add_intro_track_popup(screen, on_popup_dismiss=None):
    content = BoxLayout(orientation='vertical', padding=10, spacing=10)

    # Label per il file audio selezionato
    file_path_label = Label(text="Nessun file audio selezionato")
    content.add_widget(file_path_label)

    # Pulsante per selezionare file audio
    filechooser_button = Button(text="Seleziona File Audio", size_hint_y=None, height=40)
    filechooser_button.bind(on_press=lambda _: show_file_chooser_popup(file_path_label, "audio"))
    content.add_widget(filechooser_button)

    # Label per il file di sottotitolo selezionato o messaggio di sottotitolo vuoto
    subtitle_file_label = Label(text="Nessun sottotitolo selezionato (verrà creato un sottotitolo vuoto)")
    content.add_widget(subtitle_file_label)

    # Checkbox per selezionare se si desidera aggiungere un sottotitolo
    add_subtitle_checkbox = CheckBox()
    checkbox_label = Label(text="Vuoi aggiungere un sottotitolo?")
    checkbox_layout = BoxLayout(orientation='horizontal', spacing=10)
    checkbox_layout.add_widget(add_subtitle_checkbox)
    checkbox_layout.add_widget(checkbox_label)
    content.add_widget(checkbox_layout)

    def on_checkbox_active(checkbox, value):
        if value:
            show_file_chooser_popup(subtitle_file_label, "subtitle")
        else:
            subtitle_file_label.text = "Nessun sottotitolo selezionato (verrà creato un sottotitolo vuoto)"

    add_subtitle_checkbox.bind(active=on_checkbox_active)

    # Pulsante per salvare la traccia
    save_button = Button(text="Salva", size_hint_y=None, height=50)
    save_button.bind(on_press=lambda _: save_intro_track(screen, file_path_label.text, subtitle_file_label.text))
    content.add_widget(save_button)

    popup = Popup(title="Aggiungi Traccia Introduttiva", content=content, size_hint=(0.75, 0.5))
    
    # Aggiungi un callback per il dismiss del popup per controllare se nulla è stato caricato
    if on_popup_dismiss:
        popup.bind(on_dismiss=lambda _: on_popup_dismiss())
    
    popup.open()
    screen.popup = popup  # Referenzia il popup per chiuderlo successivamente

def save_intro_track(screen, file_path, subtitle_path):
    if file_path == "Nessun file audio selezionato":
        show_error_popup("Errore", "Seleziona un file audio per la traccia introduttiva.")
    else:
        # Salva i file corretti per la traccia introduttiva
        subtitle_file = subtitle_path if "Nessun sottotitolo selezionato" not in subtitle_path else ""
        
        # Aggiorna la traccia introduttiva nel project manager
        screen.project_manager.save_intro_track(screen.current_project, file_path, subtitle_file)
        
        # Dopo aver salvato la traccia, aggiorna l'interfaccia utente
        screen.introduction_track_custom = True
        screen.edit_project(screen.current_project)  # Ricarica l'editor
        screen.popup.dismiss()

def show_file_chooser_popup(file_label, file_type):
    # Usa il selettore di file nativo del sistema operativo
    Tk().withdraw()  # Nasconde la finestra Tkinter
    if file_type == "audio":
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav")])
    else:
        file_path = filedialog.askopenfilename(filetypes=[("Subtitle Files", "*.srt;*.vtt")])

    if file_path:
        file_label.text = file_path  # Mostra il file selezionato nel layout del parent


def show_edit_intro_track_popup(screen):
    content = BoxLayout(orientation='vertical', padding=10, spacing=10)

    # Ottieni la traccia introduttiva dal project manager
    intro_track = screen.project_manager.get_intro_track(screen.current_project)

    # Verifica se la traccia introduttiva contiene i dati e stampa per debug
    print(f"Traccia introduttiva caricata: {intro_track}")

    # Label per il file audio selezionato
    if intro_track and intro_track.get('audio_file'):
        file_path_label = Label(text=f"File Audio: {intro_track['audio_file']}")
    else:
        file_path_label = Label(text="Nessun file audio selezionato")

    content.add_widget(file_path_label)

    # Pulsante per selezionare file audio (opzionale, non obbligatorio)
    filechooser_button = Button(text="Cambia File Audio", size_hint_y=None, height=40)
    filechooser_button.bind(on_press=lambda _: show_file_chooser_popup(file_path_label, "audio"))
    content.add_widget(filechooser_button)

    # Label per il file di sottotitolo selezionato o messaggio di sottotitolo vuoto
    if intro_track and intro_track.get('subtitle_file'):
        subtitle_file_label = Label(text=f"File Sottotitolo: {intro_track['subtitle_file']}")
    else:
        subtitle_file_label = Label(text="Nessun sottotitolo selezionato (verrà creato un sottotitolo vuoto)")

    content.add_widget(subtitle_file_label)

    # Checkbox per selezionare se si desidera aggiungere un sottotitolo
    add_subtitle_checkbox = CheckBox(active=bool(intro_track and intro_track.get('subtitle_file')))
    checkbox_label = Label(text="Vuoi aggiungere un sottotitolo?")
    checkbox_layout = BoxLayout(orientation='horizontal', spacing=10)
    checkbox_layout.add_widget(add_subtitle_checkbox)
    checkbox_layout.add_widget(checkbox_label)
    content.add_widget(checkbox_layout)

    def on_checkbox_active(checkbox, value):
        if value:
            show_file_chooser_popup(subtitle_file_label, "subtitle")
        else:
            subtitle_file_label.text = "Nessun sottotitolo selezionato (verrà creato un sottotitolo vuoto)"

    add_subtitle_checkbox.bind(active=on_checkbox_active)

    # Pulsante per salvare la traccia modificata
    save_button = Button(text="Salva Modifiche", size_hint_y=None, height=50)
    save_button.bind(on_press=lambda _: save_intro_track(screen, file_path_label.text, subtitle_file_label.text))
    content.add_widget(save_button)

    popup = Popup(title="Modifica Traccia Introduttiva", content=content, size_hint=(0.75, 0.5))
    popup.open()
    screen.popup = popup  # Referenzia il popup per chiuderlo successivamente

def save_track(screen, track_name, file_path, subtitle_path, existing_track=None):
    if not track_name or file_path == "Nessun file audio selezionato":
        show_error_popup("Errore", "Inserisci sia il titolo della traccia che un file audio.")
    else:
        # Controlla se un sottotitolo è stato selezionato dall'utente
        subtitle_file = subtitle_path if "Nessun sottotitolo selezionato" not in subtitle_path else ""

        if existing_track:
            # Modifica la traccia esistente
            existing_track['title'] = track_name
            existing_track['audio_file'] = file_path
            existing_track['subtitle_file'] = subtitle_file  # Associa il file srt manualmente
        else:
            # Aggiungi una nuova traccia al progetto
            screen.project_manager.add_track(screen.current_project, track_name, file_path, subtitle_file)

        # Salva il progetto modificato
        screen.project_manager.save_projects_to_file()
        
        # Aggiorna l'editor dopo il salvataggio
        screen.edit_project(screen.current_project)
        screen.popup.dismiss()  # Chiudi il popup

def show_error_popup(title, message):
    content = BoxLayout(orientation='vertical', padding=10, spacing=10)
    content.add_widget(Label(text=message))
    popup = Popup(title=title, content=content, size_hint=(0.75, 0.5))
    popup.open()

def show_export_confirmation(screen, export_callback):
    content = BoxLayout(orientation='vertical', padding=10, spacing=10)

    # Scorri i progetti e crea il riepilogo
    summary_text = ""
    main_project_name = None
    main_project_tracks = None
    error_message_label = Label(text="", color=(1, 0, 0, 1))  # Messaggio di errore vuoto, testo rosso

    for project_name, project in screen.project_manager.projects.items():
        if main_project_name is None:
            main_project_name = project_name
            main_project_tracks = len(project['tracks']) + (1 if project['intro_track'] else 0)
        else:
            variant_tracks = len(project['tracks']) + (1 if project['intro_track'] else 0)
            if variant_tracks != main_project_tracks:
                error_message_label.text = (
                    f"Attenzione: la variante '{project_name}' non ha lo stesso numero di tracce "
                    f"dell'audioguida principale!"
                )

        intro_status = "con introduzione" if project['intro_track'] else "senza introduzione"
        summary_text += f"- {len(project['tracks'])} tracce audio + l'introduzione in {project['general']['language']}, livello {project['general']['level']}\n"

    # Aggiungi il riepilogo al contenuto del popup
    content.add_widget(Label(text=f"Stai creando un'audioguida con:\n{summary_text}", size_hint_y=None, height=200))

    # Aggiungi il messaggio di errore
    error_message_label.text_size = (screen.width * 0.6, None)  # Imposta la larghezza massima e lascia che il testo vada a capo
    content.add_widget(error_message_label)

    # Pulsante di conferma
    confirm_button = Button(text="Conferma", size_hint_y=None, height=50)
    confirm_button.bind(on_press=lambda _: export_callback(error_message_label))
    content.add_widget(confirm_button)

    # Crea il popup e mostralo
    export_popup = Popup(title="Conferma Esportazione", content=content, size_hint=(0.75, 0.75))
    export_popup.open()
    screen.export_popup = export_popup