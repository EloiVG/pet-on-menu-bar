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
import shutil
import webbrowser
try:
    from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
    NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
except ImportError:
    pass

FEED_NINTENDO = "https://www.nintenderos.com/feed/"
IDIOMA_NOTICIAS = "es"  # Cambia esto a "en" para inglés, "cat" para catalán, "de" para alemán
ARCHIVO_NOTICIAS = "noticias_vistas.json"
ARCHIVO_PALABRAS = "palabras_clave.json"
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
        "buscar_noticias": "Buscar noticias de Nintendo",
        "nueva_noticia": "Nueva noticia de Nintendo",
        "no_hay_noticias": "No hay nuevas noticias",
        "noticias_guardadas": "Noticias guardadas",
        "borrar_historial": "Borrar historial",
        "abrir_web": "Abrir web de noticias",
        "ultima_noticia": "Última noticia",
        "palabras": "Palabras clave",

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
        "buscar_noticias": "Search for Nintendo news",
        "nueva_noticia": "New Nintendo news",
        "no_hay_noticias": "No new news",
        "noticias_guardadas": "Saved news",
        "borrar_historial": "Clear history",
        "abrir_web": "Open Nintendo news",
        "ultima_noticia": "Latest news",
        "palabras": "keywords",
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
        "buscar_noticias": "Buscar notícies de Nintendo",
        "nueva_noticia": "Nova notícia de Nintendo",
        "no_hay_noticias": "No hi ha notícies noves",
        "noticias_guardadas": "Notícies guardades",
        "borrar_historial": "Esborrar historial",
        "abrir_web": "Obrir web de notícies de Nintendo",
        "ultima_noticia": "Última notícia",
        "palabras": "Paraules clau",

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
        "buscar_noticias": "Nach Nintendo-News suchen",
        "nueva_noticia": "Neue Nintendo-Nachricht",
        "no_hay_noticias": "Keine neuen Nachrichten",
        "noticias_guardadas": "Gespeicherte Nachrichten",
        "borrar_historial": "Verlauf löschen",
        "abrir_web": "Nintendo-Website öffnen",
        "ultima_noticia": "Neueste Nachricht",
        "palabras": "Schlüsselwörter",
    }
}
idioma_actual = "es"

def t(clave):
    return TEXTOS[idioma_actual][clave]

def ultima_noticia_titulo():
    try:
        feed = feedparser.parse(FEED_NINTENDO)
        if feed.entries:
            titulo = feed.entries[0].title
            return titulo if len(titulo) <= 45 else titulo[:45] + "..."
    except Exception:
        pass
    return None

def borrar_historial(icon, _):
    if os.path.exists(ARCHIVO_NOTICIAS):
        os.remove(ARCHIVO_NOTICIAS)
    notificar("Nintendo News Center", f"{t('noticias_guardadas')}: 0")

def notificar(titulo, mensaje, enlace=None):
    if platform.system() == "Darwin":
            subprocess.Popen(["osascript", "-e", f'display notification "{mensaje}" with title "{titulo}"'])
            return
    try:
        from plyer import notification
        notification.notify(title=titulo, message=mensaje, timeout=8)
    except Exception as e:
        print("Error al notificar:", e)

def cambiar_idioma(codigo):
    def _cambiar(icon, _):
        global idioma_actual
        idioma_actual = codigo
        icon.update_menu()
    return _cambiar

def revision_automatica():
    while not stop_event.is_set():
        nuevas_noticias = verificar_nuevas_noticias()
        actualizar_ultima_titulo()
        for noticia in nuevas_noticias:
                    titulo = traducir_titulo(noticia.title)
                    notificar(t("nueva_noticia"), titulo, noticia.link)
                    time.sleep(1)
        stop_event.wait(1800)

def menu_idiomas():
    return pystray.Menu(
        item("Español", cambiar_idioma("es"), radio=True, checked=lambda item: idioma_actual == "es"),
        item("English", cambiar_idioma("en"), radio=True, checked=lambda item: idioma_actual == "en"),
        item("Català", cambiar_idioma("cat"), radio=True, checked=lambda item: idioma_actual == "cat"),
        item("Deutsch", cambiar_idioma("de"), radio=True, checked=lambda item: idioma_actual == "de")
    )

def cargar_palabras_clave():
    if not os.path.exists(ARCHIVO_PALABRAS):
        return []
    try:
        with open(ARCHIVO_PALABRAS, "r", encoding="utf-8") as f:
            return [p.lower() for p in json.load(f)]
    except Exception:
        return[]

PALABRAS_DISPONIBLES = ["switch 2", "mario", "zelda", "pokémon"]
palabras_activas = set(cargar_palabras_clave())

def alternar_palabra(palabra):
    def _alternar(icon, _):
        if palabra in palabras_activas:
            palabras_activas.remove(palabra)
        else:
            palabras_activas.add(palabra)
    return _alternar

def guardar_palabras():
    with open(ARCHIVO_PALABRAS, "w", encoding="utf-8") as f:
        json.dump(sorted(palabras_activas), f, ensure_ascii=False, indent=4)

def pedir_palabra(icon, _):
    try:
        r = subprocess.run(
            ["osascript", "-e", 'tell application "System Events" to text returned of (display dialog "Escribe una palabra clave:" default answer "" with title "Nintendo News Center")'],
            capture_output=True, text=True)
        palabra = r.stdout.strip().lower()
        if r.returncode == 0 and palabra:
            palabras_activas.add(palabra)
            guardar_palabras()
    except Exception as e:
        print("Error al pedir palabra", e)

def menu_palabras():
    items = [item(p, alternar_palabra(p), checked=lambda item, p=p: p in palabras_activas)
                for p in sorted(set(PALABRAS_DISPONIBLES) | palabras_activas)]
    items.append(pystray.Menu.SEPARATOR)
    items.append(item("Añadir palabra clave...", pedir_palabra))
    return pystray.Menu(*items)

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

def coincide_palabra(titulo, palabras):
    if not palabras:
        return True
    titulo = titulo.lower()
    return any(p in titulo for p in palabras)

def cargar_noticias_vistas():
    if not os.path.exists(ARCHIVO_NOTICIAS):
        return []
    try:
        with open(ARCHIVO_NOTICIAS, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def total_noticias_vistas():
    return len(cargar_noticias_vistas())

def guardar_noticias_vistas(lista):
    with open(ARCHIVO_NOTICIAS, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=4)

def verificar_nuevas_noticias():
    try:
        feed = feedparser.parse(FEED_NINTENDO)
        if feed.bozo:
            raise Exception("Error al analizar el feed")
        noticias_vistas = cargar_noticias_vistas()
        palabras = list(palabras_activas)
        nuevas_noticias = []
        for entry in feed.entries[:5]:
            if entry.id not in noticias_vistas:
                noticias_vistas.append(entry.id)
                if coincide_palabra(entry.title, palabras):
                    nuevas_noticias.append(entry)
        guardar_noticias_vistas(noticias_vistas[-30:])
        return nuevas_noticias
    except Exception as e:
        print(f"Error al verificar nuevas noticias: {e}")
        return[]

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

def traducir_titulo(titulo):
    time.sleep(2)
    if idioma_actual == "es":
        return titulo
    codigos = {"es":"es", "en":"en", "cat": "ca", "de": "de"}
    try:
        return GoogleTranslator(source="auto", target=codigos[idioma_actual]).translate(titulo)
    except Exception as e:
        print("Error al traducir:", e)
        return titulo

def generar_imagen_por_defecto():
    image = Image.new('RGB', (64, 64), color=(0, 255, 0))  # Verde por defecto
    dc = ImageDraw.Draw(image)
    dc.ellipse([16, 16, 48, 48], fill=(255, 255, 255))
    return image

def cargar_imagenes():
    try:
        return hacer_blanca(Image.open("pet_feliz.png")), hacer_blanca(Image.open("pet_cansado.png"))
    except FileNotFoundError:
        return generar_imagen_por_defecto(), generar_imagen_por_defecto()  # Verde para feliz, Azul para cansado

def hacer_blanca(imagen):
    imagen = imagen.convert("RGBA")
    imagen = imagen.resize((200, 200), Image.LANCZOS)
    lienzo = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    lienzo.paste(imagen, (28, 28), imagen)
    blanca = Image.new("RGBA", lienzo.size, (255, 255, 255, 0))
    blanca.putalpha(lienzo.getchannel("A"))
    return blanca

def salir(icon, _):
    stop_event.set()
    icon.stop()

imagen_feliz, imagen_cansado = cargar_imagenes()

def forzar_revision_noticias(icon, _):
    nuevas_noticias = verificar_nuevas_noticias()
    if nuevas_noticias:
        for noticia in nuevas_noticias:
            titulo = traducir_titulo(noticia.title)
            notificar(t("nueva_noticia"), titulo, noticia.link)
            time.sleep(4)
    else:
        notificar("Nintendo News Center", t("no_hay_noticias"))

ultima_titulo_cache = None

def actualizar_ultima_titulo():
    global ultima_titulo_cache
    ultima_titulo_cache = ultima_noticia_titulo()
            
menu = pystray.Menu(
    item(lambda _: t("buscar_noticias"), forzar_revision_noticias),
    item(lambda _: f"{t('noticias_guardadas')}: {total_noticias_vistas()}", None, enabled=False),
    item(lambda _: t("borrar_historial"), borrar_historial),
    item(lambda _: t("abrir_web"), lambda icon, _: webbrowser.open("https://www.nintenderos.com")),
    item(lambda _: t("palabras"), menu_palabras()),
    pystray.Menu.SEPARATOR,
    item(lambda _: f"{t('ultima_noticia')} {ultima_titulo_cache or ''}", None, enabled=False),
    pystray.Menu.SEPARATOR,
    item(lambda _: t("idiomas"), menu_idiomas()),
    pystray.Menu.SEPARATOR,
    item(lambda _: t("salir"), salir)
)

icon = pystray.Icon("NintendoNews", imagen_feliz, "Nintendo News Center", menu)

def preparar_icono(icon):
    icon.visible = True
    threading.Thread(target=revision_automatica, daemon=True).start()
    notificar("Nintendo News Center", t("nueva_noticia"))

icon.run(preparar_icono)
