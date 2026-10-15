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
TEXTOS = {
    "es": {
        "estado_feliz": "Estado: Feliz",
        "estado_cansado": "Estado: Cansado",
        "estado_durmiendo": "Estado: Durmiendo (Zzz)",
        "estado_alimentado": "Estado: ¡Alimentado y feliz!",
        "estado_pomodoro_iniciado": "Estado: Pomodoro iniciado...",
        "estado_pomodoro_completado": "Estado: Pomodoro completado",
        "estado_energia": "Estado: ¡Energía al 100%!",
        "estado_ñam": "Estado: ¡Ñam ñam!",
        "estado_durmiendo_zzz": "Estado: Zzz... Durmiendo",
        "estado_pomodoro_en_progreso": "Estado: Pomodoro en progreso - {minutos:02d}:{segundos:02d}",
        "idioma_cambiado": "Idioma cambiado a {idioma}",
        "salir": "Salir",
        "cambiar_icono": "Cambiar icono",
        "dormir": "Dormir",
        "dar_mimo": "Dar mimo",
        "dar_de_comer": "Dar de comer",
        "decir_frase_aleatoria": "Decir frase aleatoria",
        "iniciar_pomodoro": "Iniciar Pomodoro",
        "idiomas": "Idiomas",
},
    "en": {
        "estado_feliz": "State: Happy",
        "estado_cansado": "State: Tired",
        "estado_durmiendo": "State: Sleeping (Zzz)",
        "estado_alimentado": "State: Fed and happy!",
        "estado_pomodoro_iniciado": "State: Pomodoro started...",
        "estado_pomodoro_completado": "State: Pomodoro completed",
        "estado_energia": "State: Energy at 100%!",
        "estado_ñam": "State: Yum yum!",
        "estado_durmiendo_zzz": "State: Zzz... Sleeping",
        "estado_pomodoro_en_progreso": "State: Pomodoro in progress - {minutos:02d}:{segundos:02d}",
        "idioma_cambiado": "Language changed to {idioma}",
        "salir": "Exit",
        "cambiar_icono": "Change icon",
        "dormir": "Sleep",
        "dar_mimo": "Give a cuddle",
        "dar_de_comer": "Feed",
        "decir_frase_aleatoria": "Say a random phrase",
        "iniciar_pomodoro": "Start Pomodoro",
        "idiomas": "Languages",
    },
    "cat": {
        "estado_feliz": "Estat: Feliç",
        "estado_cansado": "Estat: Cansat",
        "estado_durmiendo": "Estat: Dormint (Zzz)",
        "estado_alimentado": "Estat: Alimentat i feliç!",
        "estado_pomodoro_iniciado": "Estat: Pomodoro iniciat...",
        "estado_pomodoro_completado": "Estat: Pomodoro completat",
        "estado_energia": "Estat: Energia al 100%!",
        "estado_ñam": "Estat: Ñam ñam!",
        "estado_durmiendo_zzz": "Estat: Zzz... Dormint",
        "estado_pomodoro_en_progreso": "Estat: Pomodoro en progrés - {minuts:02d}:{segons:02d}",
        "idioma_cambiado": "Idioma canviat a {idioma}",
        "salir": "Sortir",
        "cambiar_icono": "Canviar icona",
        "dormir": "Dormir",
        "dar_mimo": "Donar una abraçada",
        "dar_de_comer": "Donar menjar",
        "decir_frase_aleatoria": "Dir una frase aleatòria",
        "iniciar_pomodoro": "Iniciar Pomodoro",
        "idiomas": "Idiomes",
    },
    "de": {
        "estado_feliz": "Zustand: Glücklich",
        "estado_cansado": "Zustand: Müde",
        "estado_durmiendo": "Zustand: Schlafend (Zzz)",
        "estado_alimentado": "Zustand: Gefüttert und glücklich!",
        "estado_pomodoro_iniciado": "Zustand: Pomodoro gestartet...",
        "estado_pomodoro_completado": "Zustand: Pomodoro abgeschlossen",
        "estado_energia": "Zustand: Energie bei 100%!",
        "estado_ñam": "Zustand: Lecker lecker!",
        "estado_durmiendo_zzz": "Zustand: Zzz... Schlaf en",
        "estado_pomodoro_en_progreso": "Zustand: Pomodoro läuft - {minuten:02d}:{sekunden:02d}",
        "idioma_cambiado": "Sprache geändert zu {idioma}",
        "salir": "Beenden",
        "cambiar_icono": "Symbol ändern",
        "dormir": "Schlafen",
        "dar_mimo": "Kuscheln", 
        "dar_de_comer": "Füttern",
        "decir_frase_aleatoria": "Zufälligen Satz sagen",
        "iniciar_pomodoro": "Pomodoro starten",
        "idiomas": "Sprachen",
    }
}
idioma_actual = "es"

def t(clave):
    return TEXTOS[idioma_actual][clave]

def cambiar_idioma(codigo):
    def _cambiar(icon, _):
        global idioma_actual
        idioma_actual = codigo
        icon.update_menu()
    return _cambiar

def menu_idiomas():
    return pystray.Menu(
        item("Español", cambiar_idioma("es"), radio=True, checked=lambda item: idioma_actual == "es"),
        item("English", cambiar_idioma("en"), radio=True, checked=lambda item: idioma_actual == "en"),
        item("Català", cambiar_idioma("cat"), radio=True, checked=lambda item: idioma_actual == "cat"),
        item("Deutsch", cambiar_idioma("de"), radio=True, checked=lambda item: idioma_actual == "de")
    )

stats_sistema = "CPU: 0% | Memoria: 0%"
estado_texto = "Estado: Feliz"
esta_feliz = True
pomodoro_restante = 0
stop_event = threading.Event()
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
        cpu = psutil.cpu_percent(interval=1)
        memoria = psutil.virtual_memory().percent
        stats_sistema = f"CPU: {cpu}% | Memoria: {memoria}%"
        if pomodoro_restante > 0:
            minutos, segundos = divmod(pomodoro_restante, 60)
            stats_sistema += f" | Pomodoro: {minutos:02d}:{segundos:02d}"
        else:
            icon.title = stats_sistema
        time.sleep(2)

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
def cambiar_icono(icon, _):
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
def despertar(icon, _):
    global estado_texto, esta_feliz
    esta_feliz = True
    icon.icon = imagen_feliz
    icon.title = "Mi mascota (Muy feliz)"
    estado_texto = "Estado: energia al 100%"
def dar_de_comer(icon, _):
    global estado_texto, esta_feliz
    esta_feliz = True
    icon.icon = imagen_feliz
    icon.title = "mi mascota (ñam ñam)"
    estado_texto = "estado: ¡Alimentado y feliz"
def dormir(icon, _):
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
    estado_texto = "Estado: Pomodoro completado"
    icon.title = "Pomodoro terminado"
def iniciar_pomodoro(icon, _):
    global estado_texto
    estado_texto = "Estado: Pomodoro iniciado..."
    threading.Thread(target=ejecutar_cuenta_atras, args=(icon,), daemon=True).start()
def salir(icon, _):
    stop_event.set()
    icon.stop()
def dar_mimo(icon, _):
    global esta_feliz
    esta_feliz = True
    icon.icon = imagen_feliz
    icon.title = "Mi mascota (Feliz)"
    estado_texto = "Estado: Feliz"
def decir_frase_aleatoria(icon, _):
    frase_elegida = random.choice(PERSONAJES[personaje_actual]["frases"])
    script = f'display notification "{frase_elegida}" with title "Mi mascota dice:"'
    subprocess.run(["osascript", "-e", script])

menu = pystray.Menu(
    item(lambda _: stats_sistema, None, enabled=False),
    item(lambda _: estado_texto, None, enabled=False),
    pystray.Menu.SEPARATOR,
    item("Cambiar icono", cambiar_icono),
    item("Dormir", dormir),
    item("Dar mimo", dar_mimo),
    item("Dar de comer", dar_de_comer),
    pystray.Menu.SEPARATOR,
    item("Decir frase aleatoria", decir_frase_aleatoria),
    item("Iniciar Pomodoro", iniciar_pomodoro),
    pystray.Menu.SEPARATOR,
    item("Idiomas", menu_idiomas()),
    pystray.Menu.SEPARATOR,
    item("Salir", salir)
)
icon = pystray.Icon("MiMascota", imagen_feliz, "Mi Mascota", menu)
def preparar_icono(icon):
    icon.visible = True
    threading.Thread(target=monitorizar_sistema, args=(icon,), daemon=True).start()

icon.run(preparar_icono)
