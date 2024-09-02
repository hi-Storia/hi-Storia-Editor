import os
import sys
import json
import shutil


class ProjectManager:
    def __init__(self):
        # Determina il percorso base del progetto in base all'ambiente
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        self.projects = {}
        self.project_base_dir = os.path.join(base_path, "temp_projects")

        if not os.path.exists(self.project_base_dir):
            os.makedirs(self.project_base_dir)

    def load_projects_from_file(self):
        file_path = os.path.join(self.project_base_dir, "projects.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                self.projects = json.load(file)

    def save_projects_to_file(self):
        file_path = os.path.join(self.project_base_dir, "projects.json")
        with open(file_path, 'w') as file:
            json.dump(self.projects, file, indent=4)

    def create_new_project(self, name, author, language, level, is_variant=False):
        project_name_variant = f"{name}_{language}_{level}" if is_variant else name

        project_folder = os.path.join(self.project_base_dir, project_name_variant)
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)
        
        self.projects[project_name_variant] = {
            "general": {
                "author": author,
                "image": "assets/images/default.jpg",
                "level": level,
                "language": language
            },
            "tracks": [],
            "languages": [language],
            "levels": [level],
            "intro_track": None,
            "images": []  # Inizializza l'elenco delle immagini come una lista vuota
        }
        self.save_projects_to_file()

    def get_levels_and_languages(self, project_name):
        project = self.projects.get(project_name, {})
        levels = project.get("levels", [])
        languages = project.get("languages", [])
        return {level: languages for level in levels}

    def add_track(self, project_name, track_name, file_path, subtitle_file):
        # Aggiunge una nuova traccia al progetto esistente
        if project_name in self.projects:
            project = self.projects[project_name]
            # Determina il numero della traccia, con il numero 1 riservato a una traccia speciale
            track_number = len(project["tracks"]) + 2  # Numero 1 è riservato alla traccia speciale
            project["tracks"].append({
                "track_number": track_number,
                "title": track_name,
                "audio_file": file_path,
                "subtitle_file": subtitle_file
            })
            self.save_projects_to_file()

    def save_intro_track(self, project_name, file_path, subtitle_file):
        # Salva la traccia introduttiva personalizzata
        if project_name in self.projects:
            self.projects[project_name]["intro_track"] = {
                "audio_file": file_path,
                "subtitle_file": subtitle_file
            }
            self.save_projects_to_file()
            # Stampa per debug
            print(f"Traccia introduttiva salvata per {project_name}: {self.projects[project_name]['intro_track']}")

    def delete_intro_track(self, project_name):
        # Elimina la traccia introduttiva personalizzata e ripristina quella predefinita
        if project_name in self.projects:
            self.projects[project_name]["intro_track"] = None
            self.save_projects_to_file()

    def get_intro_track(self, project_name):
        # Restituisce la traccia introduttiva, se esiste
        if project_name in self.projects:
            return self.projects[project_name].get("intro_track", None)
        return None

    def delete_project(self, project_name):
        # Elimina un progetto completamente, inclusi i file associati
        if project_name in self.projects:
            # Elimina la cartella associata al progetto
            project_folder = os.path.join(self.project_base_dir, project_name)
            if os.path.exists(project_folder):
                shutil.rmtree(project_folder)  # Elimina l'intera cartella e il suo contenuto
            
            # Elimina il progetto dalla lista
            del self.projects[project_name]
            self.save_projects_to_file()

