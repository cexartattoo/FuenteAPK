from PIL import Image, ImageOps

def invertir_colores_png(input_path, output_path):
    # Abrir la imagen y asegurar que tenga canal alfa
    imagen = Image.open(input_path).convert("RGBA")

    # Separar los canales
    r, g, b, a = imagen.split()

    # Invertir solo los canales RGB
    rgb_invertido = ImageOps.invert(Image.merge("RGB", (r, g, b)))

    # Volver a unir los canales RGB invertidos con el canal alfa original
    imagen_invertida = Image.merge("RGBA", (*rgb_invertido.split(), a))

    # Guardar la imagen invertida
    imagen_invertida.save(output_path, format="PNG")

# Ejemplo de uso
invertir_colores_png("iconos/desplazarse.png", "iconos/desplazarse_inv.png")
