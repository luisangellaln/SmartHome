import tkinter as tk 
from tuya_connector import TuyaOpenAPI
import json
import requests
import paho.mqtt.client as mqtt
import datetime

# Credenciales y configuración
ACCESS_ID = '9mrmwaeauv4v4arpdrxf'
ACCESS_KEY = '450883843d904cf582ad7a3bdfac65cd'
DEVICE_ID = 'eb47e36b0f9b13c19cawq8'

API_ENDPOINT = 'https://openapi.tuyaus.com'

# Conexión a la API de Tuya
openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
response = openapi.connect()
print("Conexión a la API de Tuya:", response)

# Función para enviar comandos
def send_command(command_code, value):
    commands = {'commands': [{'code': command_code, 'value': value}]}
    response = openapi.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands', commands)
    print(f"Respuesta de la API al enviar {command_code}: {response}")

#Función para enviar mensaje al bot de telegram
def send_telegram_message():
    url = "http://192.168.0.100:8010/send_message"
    current_time = datetime.datetime.now().strftime(" %Y-%m-%dT%H:%M:%S")
    payload = {
        "mensaje": "Se podría necesitar Ayuda!",
        "hora": current_time,
        "tipo_alerta": "Botón de emergencia presionado"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Mensaje enviado al bot de Telegram. Respuesta: {response.status_code}")
    except Exception as e:
        print(f"Error al enviar mensaje al bot: {e}")



# Configuración del broker MQTT
BROKER_ADDRESS = "192.168.0.100"
BROKER_PORT = 1883
TOPIC = "boton"

# Función que maneja los mensajes recibidos del tópico
def on_message(client, userdata, message):
    msg = message.payload.decode("utf-8").strip()  # Decodificar el mensaje y eliminar espacios
    print(f"Mensaje recibido en el tópico {message.topic}: {msg}")
    
    if msg.endswith(":1"):  # Detecta el formato del mensaje
        print("Modo alerta activado.")
        scene_alert()  # Mantiene la funcionalidad existente
        send_telegram_message()  # Envía el mensaje al bot
    elif msg == "0":
        send_command("switch_led", False)
    elif msg == "10":
        change_work_mode("colour")
    elif msg == "11":
        scene_reading()
    elif msg == "100":
        scene_work()
    elif msg == "101":
        scene_alert()
    elif msg == "110":
        scene_sleep()
    elif msg == "111":
        change_work_mode("music")
    elif msg == "1000":
        update_colour_data(0, 1000, 1000)  # Rojo
    elif msg == "1001":
        update_colour_data(120, 1000, 1000)  # Verde
    elif msg == "1010":
        update_colour_data(240, 1000, 1000)  # Azul
    elif msg == "1011":
        update_colour_data(60, 1000, 1000)  # Amarillo
    elif msg == "1100":
        update_colour_data(180, 1000, 1000)  # Cian
    elif msg == "1101":
        update_colour_data(300, 1000, 1000)  # Magenta
    elif msg == "1110":
        update_colour_data(0, 0, 1000)  # Blanco


# Configuración del cliente MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER_ADDRESS, BROKER_PORT)
mqtt_client.subscribe(TOPIC)
mqtt_client.loop_start()

# Crear la ventana principal
root = tk.Tk()
root.title("Control de Dispositivo Tuya")

# Configurar el tamaño de la ventana
root.geometry("400x600")

# Crear un Frame y un Canvas para la barra desplazadora
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=1)

canvas = tk.Canvas(main_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Crear un Frame secundario dentro del canvas
second_frame = tk.Frame(canvas)

# Añadir el frame secundario a una ventana dentro del canvas
canvas.create_window((0, 0), window=second_frame, anchor="nw")

# Etiqueta de título
label = tk.Label(second_frame, text="Controla tu dispositivo", font=("Arial", 16, "bold"))
label.grid(row=0, column=0, columnspan=2, pady=20)

# Botones para encender y apagar
on_button = tk.Button(second_frame, text="Encender", font=("Arial", 14), width=10, command=lambda: send_command("switch_led", True))
on_button.grid(row=1, column=0, padx=10, pady=5)

off_button = tk.Button(second_frame, text="Apagar", font=("Arial", 14), width=10, command=lambda: send_command("switch_led", False))
off_button.grid(row=1, column=1, padx=10, pady=5)

# ----------------- Apartado Modos de Trabajo -----------------
mode_label = tk.Label(second_frame, text="Modos de trabajo", font=("Arial", 14), fg="blue", pady=10)
mode_label.grid(row=2, column=0, columnspan=2)

# Función para cambiar el modo de trabajo
def change_work_mode(mode):
    send_command("work_mode", mode)

# Botones de modos de trabajo
white_button = tk.Button(second_frame, text="Blanco", font=("Arial", 12), width=10, command=lambda: change_work_mode("white"))
white_button.grid(row=3, column=0, padx=10, pady=5)

colour_button = tk.Button(second_frame, text="Color", font=("Arial", 12), width=10, command=lambda: change_work_mode("colour"))
colour_button.grid(row=3, column=1, padx=10, pady=5)

scene_button = tk.Button(second_frame, text="Escena", font=("Arial", 12), width=10, command=lambda: change_work_mode("scene"))
scene_button.grid(row=4, column=0, padx=10, pady=5)

music_button = tk.Button(second_frame, text="Música", font=("Arial", 12), width=10, command=lambda: change_work_mode("music"))
music_button.grid(row=4, column=1, padx=10, pady=5)

# ----------------- Separación visual -----------------
separator = tk.Frame(second_frame, height=2, bd=1, relief=tk.SUNKEN)
separator.grid(row=5, column=0, columnspan=2, pady=15, sticky="ew")

# ----------------- Apartado de Colores -----------------
colour_label = tk.Label(second_frame, text="Colores predefinidos", font=("Arial", 14), fg="green", pady=10)
colour_label.grid(row=6, column=0, columnspan=2)

# Función para actualizar el color basado en H, S, V
def update_colour_data(h, s, v):
    colour_data = {
        "h": h,
        "s": s,
        "v": v
    }
    send_command("colour_data_v2", colour_data)

# Botones para colores predefinidos
colors = [
    ("Rojo", 0, 1000, 1000),      # Rojo: H=0, S=1000, V=1000
    ("Verde", 120, 1000, 1000),   # Verde: H=120, S=1000, V=1000
    ("Azul", 240, 1000, 1000),    # Azul: H=240, S=1000, V=1000
    ("Amarillo", 60, 1000, 1000), # Amarillo: H=60, S=1000, V=1000
    ("Cian", 180, 1000, 1000),    # Cian: H=180, S=1000, V=1000
    ("Magenta", 300, 1000, 1000), # Magenta: H=300, S=1000, V=1000
    ("Blanco", 0, 0, 1000)        # Blanco: H=0, S=0, V=1000
]

# Crear los botones de colores
for index, (color_name, h, s, v) in enumerate(colors):
    row = 7 + index // 2
    col = index % 2
    color_button = tk.Button(second_frame, text=color_name, font=("Arial", 12), width=10,
                             command=lambda h=h, s=s, v=v: update_colour_data(h, s, v))
    color_button.grid(row=row, column=col, padx=10, pady=5)

# ----------------- Apartado de Escenas -----------------
scene_label = tk.Label(second_frame, text="Escenas", font=("Arial", 14), fg="purple", pady=10)
scene_label.grid(row=11, column=0, columnspan=2)

# Funciones para las escenas
def scene_reading():
    update_colour_data(60, 1000, 300)  # Luz suave amarilla

def scene_work():
    update_colour_data(0, 0, 1000)  # Luz blanca fuerte

def scene_alert():
    send_command("work_mode", "colour")
    
    # Cambiar entre rojo y azul
    def alternate_colors(count):
        if count > 0:
            if count % 2 == 0:
                update_colour_data(0, 1000, 1000)  # Rojo
            else:
                update_colour_data(240, 1000, 1000)  # Azul
            root.after(500, alternate_colors, count - 1)
        else:
            # Después de 10 segundos (20 cambios), volver a blanco
            update_colour_data(0, 0, 1000)  # Blanco
            root.after(2000, turn_off)  # Esperar 2 segundos antes de apagar

    # Función para apagar el dispositivo
    def turn_off():
        send_command("switch_led", False)

    alternate_colors(20)  # 20 cambios (10 segundos)


def scene_sleep():
    update_colour_data(240, 1000, 50)  # Luz azul muy baja

# Botones para las escenas
reading_button = tk.Button(second_frame, text="Lectura", font=("Arial", 12), width=10, command=scene_reading)
reading_button.grid(row=12, column=0, padx=10, pady=5)

work_button = tk.Button(second_frame, text="Trabajo", font=("Arial", 12), width=10, command=scene_work)
work_button.grid(row=12, column=1, padx=10, pady=5)

alert_button = tk.Button(second_frame, text="Alerta", font=("Arial", 12), width=10, command=scene_alert)
alert_button.grid(row=13, column=0, padx=10, pady=5)

sleep_button = tk.Button(second_frame, text="Dormir", font=("Arial", 12), width=10, command=scene_sleep)
sleep_button.grid(row=13, column=1, padx=10, pady=5)

# Ejecutar el bucle principal de la ventana
root.mainloop()
