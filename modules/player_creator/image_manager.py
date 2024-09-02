import os
import shutil
from tkinter import Tk, filedialog

class ImageManager:
    def __init__(self, project_manager):
        self.project_manager = project_manager

    def load_images_for_project(self, project_name, remaining_slots=None):
        # Assicurati che la chiave "images" esista
        if "images" not in self.project_manager.projects[project_name]:
            self.project_manager.projects[project_name]["images"] = []

        # Imposta il valore predefinito per gli slot rimanenti
        if remaining_slots is None:
            remaining_slots = 10  # Default al massimo se non specificato

        # Nascondi la finestra Tkinter
        Tk().withdraw()

        # Selettore di file per immagini
        file_paths = filedialog.askopenfilenames(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")], 
            title=f"Seleziona fino a {remaining_slots} immagini", 
            multiple=True
        )

        # Se l'utente non seleziona nulla, restituisci un messaggio adeguato
        if not file_paths:
            return "Nessuna immagine selezionata."

        # Verifica che non si superi il numero di immagini consentite
        if len(file_paths) > remaining_slots:
            return f"Errore: Puoi selezionare solo fino a {remaining_slots} immagini."

        # Se ci sono file selezionati, procedi con il caricamento
        if file_paths:
            # Creazione della directory del progetto per le immagini se non esiste
            project_folder = os.path.join(self.project_manager.project_base_dir, project_name, "images")
            if not os.path.exists(project_folder):
                os.makedirs(project_folder)

            # Contatore per le immagini attualmente presenti
            current_image_count = len(self.project_manager.projects[project_name]["images"])

            # Copia le immagini selezionate nella directory del progetto
            for i, file_path in enumerate(file_paths, start=current_image_count + 1):
                # Genera un nome unico per ogni immagine basato sull'indice
                file_name = f"image_{i}{os.path.splitext(file_path)[1]}"
                dest_path = os.path.join(project_folder, file_name)
                shutil.copy(file_path, dest_path)

                # Aggiungi il percorso dell'immagine alla lista del progetto
                self.project_manager.projects[project_name]["images"].append(f"images/{file_name}")

            # Salva i percorsi delle immagini nel file JSON del progetto
            self.project_manager.save_projects_to_file()

            return "Successo: Immagini caricate con successo."

    def delete_image(self, project_name, image_path):
        project = self.project_manager.projects.get(project_name)

        # Rimuovi il file dell'immagine
        full_image_path = os.path.join(self.project_manager.project_base_dir, project_name, image_path)
        if os.path.exists(full_image_path):
            os.remove(full_image_path)

        # Aggiorna il JSON per rimuovere l'immagine
        project["images"].remove(image_path)
        self.project_manager.save_projects_to_file()
