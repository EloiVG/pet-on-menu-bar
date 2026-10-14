from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import time
import threading
import random
import subprocess
import os
import sys
import platform
import psutil
import datetime

stats_sistema = "CPU: 0% | Memoria: 0%"
estado_texto = "Estado: Feliz"
stop_event = threading.Event()
def tomar_decision(icon, item):
    global estado_texto
    decision = random.choice(["¡Hora de jugar!", "¡Hora de comer!", "¡Hora de dormir!"])
    estado_texto = f"Estado: {decision}"
    icon.title = f"Mi mascota dice: {decision}"
def ejecutar_descanso(icon):
    global estado_texto
    tiempo_descanso = 5 * 60
    while tiempo_descanso > 0:
        minutos, segundos = divmod(tiempo_descanso, 60)
        estado_texto = f"Estado: Descanso en progreso - {minutos:02d}:{segundos:02d}"
        icon.title = f"Descanso - {minutos:02d}:{segundos:02d}"
        time.sleep(1)
        tiempo_descanso -= 1
    if not stop_event.is_set():
        with open("descanso_completado.txt", "a") as f:
            f.write(f"¡Descanso completado! - {datetime.datetime.now()}\n")
        estado_texto = "Estado: Descanso completado"
        icon.title = "Descanso terminado"
        actualizar_menu(icon)
def mostrar_hora_actual(icon):
    global estado_texto
    while not stop_event.is_set():
        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
        estado_texto = f"Estado: Hora actual - {hora_actual}"
        icon.title = f"Hora actual - {hora_actual}"
        time.sleep(1)
def configurar_inicio_automatico():
    if platform.system() == "Windows":
        import winreg
        script_path = os.path.abspath(sys.argv[0])
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "MiMascota", 0, winreg.REG_SZ, script_path)
        winreg.CloseKey(key)
    elif platform.system() == "Darwin":
        script_path = os.path.abspath(sys.argv[0])
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mi.mascota</string>
    <key>ProgramArguments</key>
    <array>
        <string>{script_path}</string> 
        <string>--background</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>'''
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.mi.mascota.plist")
        with open(plist_path, "w") as plist_file:
            plist_file.write(plist_content)
configurar_inicio_automatico()

def monitorizar_sistema(icon):
    global stats_sistema
    while not stop_event.is_set():
        cpu_percent = psutil.cpu_percent(interval=1)
        memoria = psutil.virtual_memory()
        stats_sistema = f"CPU: {cpu_percent}% | Memoria: {memoria.percent}%"
        time.sleep(3)
    
PERSONAJES = {
    "Kirby": {
        "frases": [
            "¡Poyo!",
            "Tengo un hambre voraz, ¡a comer!",
            "Hora de dormir, ¡buenas noches!",
            "¡Estoy lleno de energía!",
        ]
    }
}
personaje_actual = "Kirby"

def generar_imagen(color_fondo):
    image = Image.new('RGB', (64, 64), color=(color_fondo))
    dc = ImageDraw.Draw(image)
    dc.ellipse([16, 16, 48, 48], fill=(255, 255, 255))
    return image
def cargar_imagenes():
    try:
        return Image.open("pet_feliz.png"), Image.open("pet_cansado.png")
    except FileNotFoundError:
        return generar_imagen((0, 255, 0)), generar_imagen((0, 0, 255))  # Verde para feliz, Azul para cansado
imagen_feliz, imagen_cansado = cargar_imagenes()
estado_texto = "Estado: Feliz"
def cambiar_icono(icon, item):
    global estado_texto, esta_feliz
    esta_feliz = not esta_feliz
    if esta_feliz:
        icon.icon = imagen_feliz
        icon.title = "Mi mascota (Feliz)"
        estado_texto = "Estado: Feliz"
    else:
        icon.icon = imagen_cansado
        icon.title = "Mi mascota (Cansado)"
        estado_texto = "Estado: Cansado"
    icon.menu = pystray.Menu(
        item(estado_texto, lambda: None),
        item('Cambiar icono', cambiar_icono),
        item('Salir', salir)
    )
def despertar(icon, item):
    global estado_texto, esta_feliz
    esta_feliz = True
    icon.icon = imagen_feliz
    icon.title = "Mi mascota (Muy feliz)"
    estado_texto = "Estado: energia al 100%"
def dar_de_comer(icon, item):
    global estado_texto, esta_feliz
    esta_feliz = True
    icon.icon = imagen_feliz
    icon.title = "mi mascota (ñam ñam)"
    estado_texto = "estado: ¡Alimentado y feliz"
def dormir(icon, item):
    global estado_texto, esta_feliz
    esta_feliz = False
    icon.icon = imagen_cansado
    icon.title = "mi mascota (Zzz... Durmiendo)"
    estado_texto = "Estado: Durmiendo (Zzz)"
stop_event = threading.Event()
def ejecutar_cuenta_atras(icon):
    global estado_texto
    tiempo_restante = 25 * 60
    while tiempo_restante > 0:
        minutos, segundos = divmod(tiempo_restante, 60)
        estado_texto = f"Estado: Pomodoro en progreso - {minutos:02d}:{segundos:02d}"
        icon.title = f"Pomodoro - {minutos:02d}:{segundos:02d}"
        time.sleep(1)
        tiempo_restante -= 1
    if not stop_event.is_set():
        with open("pomodoro_completado.txt", "a") as f:
            f.write(f"¡Pomodoro completado! - {datetime.datetime.now()}\n")
        estado_texto = "Estado: Pomodoro completado"
        icon.title = "Pomodoro terminado"
        actualizar_menu(icon)
    estado_texto = "Estado: Pomodoro completado"
    icon.title = "Pomodoro terminado"
def iniciar_pomodoro(icon, item):
    global estado_texto
    estado_texto = "Estado: Pomodoro iniciado..."
    threading.Thread(target=ejecutar_cuenta_atras, args=(icon,), daemon=True).start()
def salir(icon, item):
    stop_event.set()
    icon.stop()
def decir_frase_aleatoria(icon):
    frase_elegida = random.choice(PERSONAJES[personaje_actual]["frases"])
    script = f'display notification "{frase_elegida}" with title "Mi mascota dice:"'
    subprocess.run(["osascript", "-e", script])
menu = pystray.Menu(
item(lambda item: f"{stats_sistema}", lambda: None),
item(lambda item: estado_texto, lambda: None),
item('Cambiar icono', cambiar_icono),
item('Dar un mimo', despertar),
item('Dormir', dormir),
item('Dar de comer', dar_de_comer),
item('Iniciar Pomodoro (25m)', iniciar_pomodoro),
item('Decir frase', decir_frase_aleatoria),
item('Salir', salir),
item('Descanso (5m)', ejecutar_descanso)
)
icon = pystray.Icon("name", imagen_feliz, "Mi mascota", menu)
icon.run()
