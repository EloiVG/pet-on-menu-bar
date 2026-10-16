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
import feedparser
from deep_translator import GoogleTranslator
import json

FEED_NINTENDO = "https://www.nintenderos.com/feed/"
IDIOMA_NOTICIAS = "es"  # Cambia esto a "en" para inglés, "cat" para catalán, "de" para alemán
ARCHIVO_NOTICIAS = "noticias_vistas.json"
stop_event = threading.Event()

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
ARCHIVO_NOTICIAS = "noticias_vistas.json"

def cargar_noticias_vistas():
    if not os.path.exists(ARCHIVO_NOTICIAS):
        return []
    try:
        with open(ARCHIVO_NOTICIAS, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def guardar_noticias_vistas(lista):
    with open(ARCHIVO_NOTICIAS, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=4)

def guardar_noticias_vistas(lista):
    with open(ARCHIVO_NOTICIAS, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=4)

def verificar_nuevas_noticias():
    try:
        feed = feedparser.parse(FEED_NINTENDO)
        if feed.bozo:
            raise Exception("Error al analizar el feed")
        noticias_vistas = cargar_noticias_vistas()
        nuevas_noticias = []
        for entry in feed.entries[:5]:  
            if entry.id not in noticias_vistas:
                nuevas_noticias.append(entry)
                noticias_vistas.append(entry.id)
        if nuevas_noticias:
            guardar_noticias_vistas(noticias_vistas[-30:])  # Guardar solo las últimas 30 noticias vistas
            return nuevas_noticias
        return []
    except Exception as e:
        print(f"Error al verificar nuevas noticias: {e}")
        return []

def configurar_inicio_automatico():
    if platform.system() == "Darwin":
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
        try:
            with open(plist_path, "w") as plist_file:
                plist_file.write(plist_content)
        except Exception as e:
            print(f"Error al configurar el inicio automático: {e}")

configurar_inicio_automatico()

def generar_imagen_por_defecto():
    image = Image.new('RGB', (64, 64), color=(0, 255, 0))  # Verde por defecto
    dc = ImageDraw.Draw(image)
    dc.ellipse([16, 16, 48, 48], fill=(255, 255, 255))
    return image

def cargar_imagenes():
    try:
        return Image.open("pet_feliz.png"), Image.open("pet_cansado.png")
    except FileNotFoundError:
        return generar_imagen_por_defecto(), generar_imagen_por_defecto()  # Verde para feliz, Azul para cansado

def salir(icon, _):
    stop_event.set()
    icon.stop()

imagen_feliz, imagen_cansado = cargar_imagenes()

def forzar_revision_noticias(icon, _):
    nuevas_noticias = verificar_nuevas_noticias()
    if nuevas_noticias:
        for noticia in nuevas_noticias:
            print(f"Nueva noticia: {noticia.title}")
            if platform.system() == "Darwin":
                subprocess.run(["osascript", "-e", f'display notification "{noticia.title}" with title "Nueva noticia de Nintendo"'])
                time.sleep(2)
    else:
        print("No hay nuevas noticias.")
        if platform.system() == "Darwin":
            script = f'display notification "No hay nuevas noticias." with title "Nintendo News Center"'
            subprocess.run(["osascript", "-e", script])
            
menu = pystray.Menu(
    item("Buscar noticias de Nintendo", forzar_revision_noticias),
    pystray.Menu.SEPARATOR,
    item("Salir", salir)
)

icon = pystray.Icon("NintendoNews", imagen_feliz, "Nintendo News Center", menu)

def preparar_icono(icon):
    icon.visible = True

icon.run(preparar_icono)
