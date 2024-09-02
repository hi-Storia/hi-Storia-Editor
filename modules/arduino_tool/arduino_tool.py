from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.modalview import ModalView
from kivy.uix.codeinput import CodeInput
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Rectangle, Color, Line
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from pygments.lexers import ArduinoLexer
import threading
from .arduino_cli import check_arduino_cli, install_core_and_libraries, compile_and_upload, create_sketch, find_arduino_port

import sys
import os

# Funzione per convertire un colore esadecimale in formato RGBA per Kivy
def hex_to_rgba(hex_color, alpha=1.0):
    hex_color = hex_color.lstrip('#')
    return [int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4)] + [alpha]

class StepperControl(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'horizontal'

        # Bottone per diminuire il numero
        self.decrease_button = Button(
            text="-", size_hint_x=0.3, size_hint_y=None, height=60,
            background_normal="", background_color=hex_to_rgba("#ECEDFB"),
            color=hex_to_rgba("#006D7B")
        )
        self.decrease_button.bind(on_press=self.decrease_value)
        self.add_widget(self.decrease_button)

        # Label per visualizzare il numero corrente
        self.current_value_label = Label(text="1", size_hint_x=0.4, size_hint_y=None, height=60)
        self.add_widget(self.current_value_label)

        # Bottone per aumentare il numero
        self.increase_button = Button(
            text="+", size_hint_x=0.3, size_hint_y=None, height=60,
            background_normal="", background_color=hex_to_rgba("#ECEDFB"),
            color=hex_to_rgba("#006D7B")
        )
        self.increase_button.bind(on_press=self.increase_value)
        self.add_widget(self.increase_button)

        self.min_value = 1
        self.max_value = 11

    def increase_value(self, instance):
        current_value = int(self.current_value_label.text)
        if current_value < self.max_value:
            current_value += 1
            self.current_value_label.text = str(current_value)
            self.app.update_sensor_pins_stepper(current_value)
            self.app.update_activator_label(current_value)

    def decrease_value(self, instance):
        current_value = int(self.current_value_label.text)
        if current_value > self.min_value:
            current_value -= 1
            self.current_value_label.text = str(current_value)
            self.app.update_sensor_pins_stepper(current_value)
            self.app.update_activator_label(current_value)

class BorderedSpinner(RelativeLayout):
    def __init__(self, spinner, border_color, dynamic_height=None, **kwargs):
        super().__init__(**kwargs)
        self.spinner = spinner
        self.border_color = border_color
        self.size_hint_y = None
        self.height = dynamic_height if dynamic_height else 60
        self.add_widget(self.spinner)

        with self.canvas.after:
            Color(*self.border_color)
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)

        self.bind(pos=self.update_border, size=self.update_border)

    def update_border(self, *args):
        self.border.rectangle = (self.x, self.y, self.width, self.height)

class ArduinoToolScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
         # Determina il percorso delle risorse
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        # Percorsi delle immagini
        bg_image_path = os.path.join(base_path, "assets", "images", "background-arduino.png")
        arduino_image_path = os.path.join(base_path, "assets", "images", "arduino.png")

        # Usare FloatLayout come contenitore principale del layout
        root = FloatLayout()

        # Sfondo
        with root.canvas.before:
            self.bg_image = Image(source=bg_image_path)
            self.bg_rect = Rectangle(texture=self.bg_image.texture, size=self.size, pos=self.pos)
            self.bind(size=self.update_bg, pos=self.update_bg)

        # Layout principale a 3 colonne
        main_layout = GridLayout(cols=3, padding=10)

        # Colonna sinistra
        self.left_layout = GridLayout(cols=2, padding=10, spacing=10, size_hint=(1, None))
        self.left_layout.bind(minimum_height=self.left_layout.setter('height'))

        self.activator_label = Label(text="Attivatori: 1", color=(0, 0, 0, 1), size_hint_y=None, height=60)
        self.left_layout.add_widget(self.activator_label)

        self.stepper_control = StepperControl(app=self, size_hint_y=None, height=60)
        self.left_layout.add_widget(self.stepper_control)

        # Pin per ogni sensore
        self.sensor_pin_selectors = []
        self.update_sensor_pins_stepper(1)

        left_scrollview = ScrollView(size_hint=(1, 1))
        left_scrollview.add_widget(self.left_layout)
        main_layout.add_widget(left_scrollview)

        # Colonna centrale
        center_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        arduino_image = Image(source=arduino_image_path)
        center_layout.add_widget(arduino_image)

        self.error_label = Label(text="", color=(1, 0, 0, 1), size_hint_y=None, height=60)
        center_layout.add_widget(self.error_label)

        main_layout.add_widget(center_layout)

        # Colonna destra
        right_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        baud_rate_layout = GridLayout(cols=2, size_hint_y=None, height=40)
        baud_rate_layout.add_widget(Label(text="Baud Rate:", color=(0, 0, 0, 1), size_hint_x=0.5, height=40))
        self.baud_rate_input = TextInput(text="115200", multiline=False, size_hint_x=0.5, size_hint_y=None, height=40)
        baud_rate_layout.add_widget(self.baud_rate_input)
        right_layout.add_widget(baud_rate_layout)

        threshold_layout = GridLayout(cols=2, size_hint_y=None, height=40)
        threshold_layout.add_widget(Label(text="Soglia:", color=(0, 0, 0, 1), size_hint_x=0.5, height=40))
        self.threshold_input = TextInput(text="900", multiline=False, size_hint_x=0.5, size_hint_y=None, height=40)
        threshold_layout.add_widget(self.threshold_input)
        right_layout.add_widget(threshold_layout)

        self.show_code_button = Button(text="Guarda il codice", background_normal="", background_color=hex_to_rgba("#A1B0B3"), color=(1, 1, 1, 1), size_hint_y=None, height=50)
        self.show_code_button.bind(on_press=self.show_sketch_code)
        right_layout.add_widget(self.show_code_button)

        self.upload_button = Button(text="Carica su Arduino", background_normal="", background_color=hex_to_rgba("#33CCAA"), color=(1, 1, 1, 1), size_hint_y=None, height=50)
        self.upload_button.bind(on_press=self.start_upload_thread)
        right_layout.add_widget(self.upload_button)

        self.connection_label = Label(text="Non connesso", color=(0, 0, 0, 1), size_hint_y=None, height=40)
        right_layout.add_widget(self.connection_label)

        self.log_label = Label(text="Log del processo:", color=(0, 0, 0, 1), size_hint_y=None, height=40)
        right_layout.add_widget(self.log_label)

        self.log_scrollview = ScrollView(size_hint=(1, 0.3))
        self.log_text = Label(text="", size_hint_y=None, color=(0, 0, 0, 1))
        self.log_text.bind(texture_size=self.update_scroll)
        self.log_scrollview.add_widget(self.log_text)
        right_layout.add_widget(self.log_scrollview)

        main_layout.add_widget(right_layout)

        # Aggiungi il layout principale a root
        root.add_widget(main_layout)
        self.add_widget(root)

    def update_scroll(self, *args):
        self.log_text.text_size = (self.log_scrollview.width, None)
        self.log_scrollview.scroll_y = 0

    def update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def update_sensor_pins_stepper(self, sensor_count):
        available_height = 400  # Altezza fissa per evitare problemi di layout dinamico
        max_height_per_spinner = 60
        min_height_per_spinner = 30
        dynamic_height = max(min_height_per_spinner, min(max_height_per_spinner, available_height // (sensor_count + 2)))

        self.left_layout.clear_widgets()
        self.left_layout.add_widget(self.activator_label)
        self.left_layout.add_widget(self.stepper_control)

        self.sensor_pin_selectors.clear()

        for i in range(sensor_count):
            label = Label(text=f"Pin Sensore {i + 1}:", color=(0, 0, 0, 1), size_hint_y=None, height=dynamic_height)
            pin_spinner = Spinner(
                text=str(i + 2),
                values=[str(j) for j in range(2, 14)],
                background_normal="",
                background_color=hex_to_rgba("#ECEDFB"),
                color=hex_to_rgba("#006D7B"),
                size_hint_y=None,
                height=dynamic_height
            )
            pin_spinner.bind(text=self.validate_pins)
            bordered_spinner = BorderedSpinner(pin_spinner, border_color=hex_to_rgba("#006D7B"), dynamic_height=dynamic_height)
            self.sensor_pin_selectors.append((label, pin_spinner))
            self.left_layout.add_widget(label)
            self.left_layout.add_widget(bordered_spinner)

        self.common_pin_label = Label(text="Pin Comune:", color=(0, 0, 0, 1), size_hint_y=None, height=dynamic_height)
        self.common_pin_spinner = Spinner(
            text='13',
            values=[str(i) for i in range(2, 14)],
            background_normal="",
            background_color=hex_to_rgba("#248598"),
            color=hex_to_rgba("#FFFFFF"),
            size_hint_y=None,
            height=dynamic_height
        )
        bordered_common_spinner = BorderedSpinner(self.common_pin_spinner, border_color=hex_to_rgba("#212121"), dynamic_height=dynamic_height)

        self.left_layout.add_widget(self.common_pin_label)
        self.left_layout.add_widget(bordered_common_spinner)

    def update_activator_label(self, sensor_count):
        self.activator_label.text = f"Attivatori: {sensor_count}"

    def validate_pins(self, instance, value):
        selected_pins = [pin_spinner.text for _, pin_spinner in self.sensor_pin_selectors]
        duplicates = [pin for pin in selected_pins if selected_pins.count(pin) > 1]

        common_pin = self.common_pin_spinner.text
        if common_pin in selected_pins:
            duplicates.append(common_pin)

        if duplicates:
            self.error_label.text = "Stai usando lo stesso PIN per due attivatori, scegli un PIN diverso."
        else:
            self.error_label.text = ""

        for label, pin_spinner in self.sensor_pin_selectors:
            if pin_spinner.text in duplicates:
                pin_spinner.background_color = (1, 0, 0, 1)
            else:
                pin_spinner.background_color = hex_to_rgba("#ECEDFB")

        if self.common_pin_spinner.text in duplicates:
            self.common_pin_spinner.background_color = (1, 0, 0, 1)
        else:
            self.common_pin_spinner.background_color = hex_to_rgba("#248598")

    def start_upload_thread(self, instance):
        self.upload_button.disabled = True
        self.upload_button.background_color = (0.5, 0.5, 0.5, 1)
        threading.Thread(target=self.upload_sketch).start()

    def upload_sketch(self):
        self.log_text.text += "Inizio caricamento su Arduino...\n"

        port = find_arduino_port()
        if port:
            self.connection_label.text = f"Connesso a: {port}"
            arduino_cli_path = check_arduino_cli()
            if arduino_cli_path:
                install_core_and_libraries(arduino_cli_path)

                common_pin = int(self.common_pin_spinner.text)
                sensor_count = int(self.stepper_control.current_value_label.text)
                sensor_pins = [int(pin_spinner.text) for _, pin_spinner in self.sensor_pin_selectors]
                serial_baud = int(self.baud_rate_input.text)
                threshold = int(self.threshold_input.text)

                if len(sensor_pins) != len(set(sensor_pins)) or common_pin in sensor_pins:
                    self.error_label.text = "Ci sono pin duplicati. Ogni sensore deve avere un pin unico."
                    self.reset_upload_button()
                    return

                sketch_path = create_sketch(sensor_pins, common_pin, serial_baud, threshold)

                self.log_text.text += "Compilazione in corso...\n"
                success = compile_and_upload(sketch_path, arduino_cli_path, port)
                if success:
                    self.log_text.text += "Caricamento completato con successo!\n"
                else:
                    self.log_text.text += "Errore durante il caricamento.\n"
            else:
                self.log_text.text += "Arduino CLI non trovato.\n"
        else:
            self.connection_label.text = "Non connesso"
            self.log_text.text += "Arduino non trovato. Per favore collega una scheda Arduino.\n"

        self.reset_upload_button()

    def reset_upload_button(self):
        self.upload_button.disabled = False
        self.upload_button.background_color = (0.2, 0.8, 0.7, 1)
        self.upload_button.text = "Carica su Arduino"

    def show_sketch_code(self, instance):
        sensor_count = int(self.stepper_control.current_value_label.text)
        sensor_pins = [int(pin_spinner.text) for _, pin_spinner in self.sensor_pin_selectors]
        common_pin = int(self.common_pin_spinner.text)
        serial_baud = int(self.baud_rate_input.text)
        threshold = int(self.threshold_input.text)

        sketch_path = create_sketch(sensor_pins, common_pin, serial_baud, threshold)

        with open(sketch_path, 'r') as sketch_file:
            sketch_code = sketch_file.read()

        modal_view = ModalView(size_hint=(0.8, 0.8))
        modal_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        code_input = CodeInput(lexer=ArduinoLexer(), text=sketch_code, readonly=True)
        modal_layout.add_widget(code_input)

        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        copy_button = Button(text="Copia negli appunti", size_hint_x=0.5, background_color=hex_to_rgba("#A1B0B3"), color=(1, 1, 1, 1))
        copy_button.bind(on_press=lambda x: self.copy_to_clipboard(sketch_code, modal_layout))
        button_layout.add_widget(copy_button)

        close_button = Button(text="X", size_hint_x=0.5, background_color=hex_to_rgba("#FF5555"), color=(1, 1, 1, 1))
        close_button.bind(on_press=modal_view.dismiss)
        button_layout.add_widget(close_button)

        modal_layout.add_widget(button_layout)
        modal_view.add_widget(modal_layout)
        modal_view.open()

    def copy_to_clipboard(self, text, modal_layout):
        Clipboard.copy(text)
        message_label = Label(text="Codice copiato negli appunti", color=(0, 1, 0, 1), size_hint_y=None, height=30)
        modal_layout.add_widget(message_label)
        Clock.schedule_once(lambda dt: modal_layout.remove_widget(message_label), 2)
