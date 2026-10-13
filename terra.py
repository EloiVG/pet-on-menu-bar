from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import time
import threading
def generar_imagen(color_fondo):
    image = Image.new('RGB', (64, 64), color=(color_fondo))
    dc = ImageDraw.Draw(image)
    dc.ellipse([16, 16, 48, 48], fill=(255, 255, 255))
    return image
imagen_feliz = Image.open("pet_feliz.png")
imagen_cansado = Image.open("pet_cansado.png")
estado_texto = "Estado: Feliz"
def cambiar_icono(icon, item):
    global estado_texto
    if icon.icon == imagen_feliz:
        icon.icon = imagen_cansado
        icon.title = "Mi mascota (Cansada Zzz)"
        estado_texto = "Estado: Cansado"
    else:
        icon.icon = imagen_feliz
        icon.title = "Mi mascota (Feliz)"
        estado_texto = "Estado: Feliz"
    icon.menu = pystray.Menu(
        item(estado_texto, lambda: None),
        item('Cambiar icono', cambiar_icono),
        item('Salir', salir)
    )
def despertar(icon, item):
    global estado_texto
    icon.icon = imagen_feliz
    icon.title = "Mi mascota (Muy feliz)"
    estado_texto = "Estado: energia al 100%"
def dar_de_comer(icon, item):
    global estado_texto
    icon.icon = imagen_feliz
    icon.title = "mi mascota (ñam ñam)"
    estado_texto = "estado: ¡Alimentado y feliz"
def dormir(icon, item):
    global estado_texto
    icon.icon = imagen_cansado
    icon.title = "mi mascota (Zzz... Durmiendo)"
    estado_texto = "Estado: Durmiendo (Zzz)"
def ejecutar_cuenta_atras(icon):
    global estado_texto
    tiempo_restante = 25 * 2
    while tiempo_restante > 0:
        minutos, segundos = divmod(tiempo_restante, 60)
        estado_texto = f"Estado: Pomodoro en progreso - {minutos:02d}:{segundos:02d}"
        icon.title = f"Pomodoro - {minutos:02d}:{segundos:02d}"
        time.sleep(1)
        tiempo_restante -= 1
    estado_texto = "Estado: Pomodoro completado"
    icon.title = "Pomodoro terminado"
def iniciar_pomodoro(icon, item):
    global estado_texto
    estado_texto = "Estado: Pomodoro iniciado..."
    threading.Thread(target=ejecutar_cuenta_atras, args=(icon,), daemon=True).start()
def salir(icon, item):
    icon.stop()
menu = pystray.Menu(
item(lambda item: estado_texto, lambda: None),
item('Cambiar icono', cambiar_icono),
item('Dar un mimo', despertar),
item('Dormir', dormir),
item('Dar de comer', dar_de_comer),
item('Iniciar Pomodoro (25m)', iniciar_pomodoro),
item('Salir', salir)
)
icon = pystray.Icon("name", imagen_feliz, "Mi mascota", menu)
icon.run()