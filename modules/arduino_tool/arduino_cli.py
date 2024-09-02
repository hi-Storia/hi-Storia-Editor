import sys
import os
import subprocess
import serial.tools.list_ports
import shutil

def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino" in port.description or "Genuino" in port.description:
            return port.device
    return None

def check_arduino_cli():
    # Controlla se l'app è impacchettata con PyInstaller
    if hasattr(sys, '_MEIPASS'):
        script_dir = sys._MEIPASS  # Directory temporanea PyInstaller
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))

    # Determina il percorso di arduino-cli in base al sistema operativo
    arduino_cli_path = os.path.join(script_dir, "arduino", "arduino-cli.exe")

    if os.name == "posix":  # macOS o Linux
        arduino_cli_path = os.path.join(script_dir, "arduino", "arduino-cli")

    if not os.path.exists(arduino_cli_path):
        print("arduino-cli non trovato, download in corso...")
        # Logica per scaricare e installare arduino-cli

    return arduino_cli_path

def install_core_and_libraries(arduino_cli_path):
    subprocess.run(f'"{arduino_cli_path}" core install arduino:avr', shell=True)
    subprocess.run(f'"{arduino_cli_path}" lib install CapacitiveSensor', shell=True)

def create_sketch(sensor_pins, common_pin, serial_baud, threshold):
    # Gestisci il percorso dinamico per la directory temporanea o di lavoro
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Percorso per la cartella sketch
    sketch_dir = os.path.join(base_path, "sketch")
    os.makedirs(sketch_dir, exist_ok=True)  # Crea la cartella se non esiste

    # Percorso del file sketch.ino
    sketch_path = os.path.join(sketch_dir, "sketch.ino")

    # Contenuto dello sketch
    sensor_count = len(sensor_pins)
    capacitive_sensors_str = ',\n    '.join([f'CapacitiveSensor({common_pin}, {pin})' for pin in sensor_pins])

    sketch_content = f"""
#include <CapacitiveSensor.h>

const int threshold = {threshold};
const int delayVal = 40;
const int sensorCount = {sensor_count};

const int sensorPins[sensorCount] = {{{', '.join(map(str, sensor_pins))}}};
CapacitiveSensor capSensors[sensorCount] = {{
    {capacitive_sensors_str}
}};

int currentTrack = 0;

void setup() {{
    Serial.begin({serial_baud});
}}

void loop() {{
    for (int i = 0; i < sensorCount; i++) {{
        long sensorValue = capSensors[i].capacitiveSensor(3);
        if (sensorValue > threshold) {{
            if (currentTrack != i + 2) {{
                Serial.write(i + 2);
                currentTrack = i + 2;
            }}
        }}
    }}

    if (Serial.available()) {{
        char val = Serial.read();
        if (val == 'h') {{
            // Implement handshake handling if necessary
        }} else if (val == 'r') {{
            currentTrack = 0;
        }}
    }}

    delay(delayVal);
}}
    """

    with open(sketch_path, "w") as sketch_file:
        sketch_file.write(sketch_content)
    
    return sketch_path

def compile_and_upload(sketch_path, arduino_cli_path, port):
    fqbn = "arduino:avr:uno"
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_build")
    os.makedirs(temp_dir, exist_ok=True)

    if compile_sketch(sketch_path, arduino_cli_path, fqbn, temp_dir):
        upload_cmd = f'"{arduino_cli_path}" upload -p {port} --fqbn {fqbn} --input-dir "{temp_dir}" "{sketch_path}"'
        process = subprocess.Popen(upload_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            print("Caricamento completato con successo")
            print(stdout.decode(errors='ignore'))
            clean_temp_directory(temp_dir)
            return True
        else:
            print(f"Errore durante il caricamento: {stderr.decode(errors='ignore')}")
            print(f"Output: {stdout.decode(errors='ignore')}")
            return False
    else:
        print("Compilazione fallita, caricamento annullato.")
        return False

def compile_sketch(sketch_path, arduino_cli_path, fqbn, temp_dir):
    compile_cmd = f'"{arduino_cli_path}" compile --fqbn {fqbn} --build-path "{temp_dir}" "{sketch_path}" --verbose'
    process = subprocess.Popen(compile_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        print("Compilazione completata con successo")
        return True
    else:
        print(f"Errore durante la compilazione: {stderr.decode(errors='ignore')}")
        return False

def clean_temp_directory(temp_dir):
    try:
        shutil.rmtree(temp_dir)
        print(f"Cartella temporanea {temp_dir} rimossa con successo.")
    except Exception as e:
        print(f"Errore durante la rimozione della cartella temporanea: {e}")
