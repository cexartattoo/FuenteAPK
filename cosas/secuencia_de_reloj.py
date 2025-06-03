from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

# Asegúrate de tener una fuente ttf adecuada
FUENTE = "C:/Windows/Fonts/arial.ttf"  # Windows  # Cambia esto si estás en Windows o quieres otra fuente
ANCHO = 200
CARPETA_SALIDA = "imagenes_hora"
os.makedirs(CARPETA_SALIDA, exist_ok=True)

def crear_imagen(texto, nombre_archivo, tamaño, alto=200):
    imagen = Image.new("RGB", (ANCHO, alto), color="black")
    draw = ImageDraw.Draw(imagen)

    # Fuente y tamaño
    fuente = ImageFont.truetype(FUENTE, tamaño)

    # Centrado del texto
    bbox = draw.textbbox((0, 0), texto, font=fuente)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    posicion = (((ANCHO - w) // 2), ((alto - h) // 2)-40)

    draw.text(posicion, texto, fill="white", font=fuente)
    imagen.save(os.path.join(CARPETA_SALIDA, nombre_archivo))

def crear_imagen_hora_actual():
    ahora = datetime.now()
    hora = ahora.strftime("%I")  # Hora en formato 12h
    minutos = ahora.strftime("%M")
    ampm = ahora.strftime("%p")
    completa = ahora.strftime("%I:%M")

    crear_imagen(hora, "1_hora.png",180)
    crear_imagen(minutos, "2_minutos.png",180)
    crear_imagen(ampm, "3_ampm.png",130)
    crear_imagen(completa, "4_completa.png",80)
    crear_imagen(ampm, "5_ampm.png", 130)

def agregar_logos():
    # Ajusta la ruta a tus logos
    logos = [("logo_universidad.png", "6_logo_universidad.png"),
             ("logo_64.png", "7_logo_carrera.png")]

    for entrada, salida in logos:
        logo = Image.open(entrada).convert("RGB")
        w, h = logo.size
        nuevo_alto = int(h * (ANCHO / w))
        logo = logo.resize((ANCHO, nuevo_alto))
        logo.save(os.path.join(CARPETA_SALIDA, salida))

# Ejecutar
crear_imagen_hora_actual()
agregar_logos()
print("¡Imágenes generadas!")
