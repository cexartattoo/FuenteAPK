

from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label

from kivy.clock import Clock

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
import requests
import threading
import os


class Elemento(BoxLayout):
    def __init__(self, tipo="imagen", **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=100, **kwargs)
        self.tipo = tipo

        if os.path.isfile(tipo):
            self.icono = Image(source=tipo, size_hint=(0.2, 1))
        else:
            self.icono = Image(source=f"{tipo}.png", size_hint=(0.2, 1))


        self.add_widget(self.icono)

        self.tiempo_input = TextInput(hint_text="Segundos", size_hint=(0.2, 1), input_filter='int')
        self.add_widget(self.tiempo_input)

        self.repeticiones_input = TextInput(hint_text="Repeticiones", size_hint=(0.2, 1), input_filter='int')
        self.add_widget(self.repeticiones_input)

        self.subir_btn = Button(text="UP", size_hint=(0.1, 1))
        self.subir_btn.bind(on_press=self.mover_arriba)
        self.add_widget(self.subir_btn)

        self.bajar_btn = Button(text="DO", size_hint=(0.1, 1))
        self.bajar_btn.bind(on_press=self.mover_abajo)
        self.add_widget(self.bajar_btn)

        self.eliminar_btn = Button(text="DEL", size_hint=(0.1, 1))
        self.eliminar_btn.bind(on_press=self.eliminar)
        self.add_widget(self.eliminar_btn)

    def mover_arriba(self, instance):
        lista = self.parent
        index = lista.children.index(self)
        if index < len(lista.children) - 1:
            elementos = lista.children[:]  # copia segura
            elementos[index], elementos[index + 1] = elementos[index + 1], elementos[index]
            lista.clear_widgets()
            for child in reversed(elementos):
                lista.add_widget(child)

    def mover_abajo(self, instance):
        lista = self.parent
        index = lista.children.index(self)
        if index > 0:
            elementos = lista.children[:]  # copia segura
            elementos[index], elementos[index - 1] = elementos[index - 1], elementos[index]
            lista.clear_widgets()
            for child in reversed(elementos):
                lista.add_widget(child)

    def eliminar(self, instance):
        self.parent.remove_widget(self)


class FuenteControlApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical')

        self.lista = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.lista.bind(minimum_height=self.lista.setter('height'))

        scroll = ScrollView(size_hint=(1, 0.8))
        scroll.add_widget(self.lista)

        root.add_widget(scroll)

        botones = BoxLayout(size_hint=(1, 0.2), spacing=10)

        agregar_imagen = Button(text="Agregar Imagen")
        agregar_imagen.bind(on_press=self.seleccionar_imagen)
        botones.add_widget(agregar_imagen)

        agregar_reloj = Button(text="Agregar Reloj")
        agregar_reloj.bind(on_press=lambda x: self.agregar_elemento("reloj"))
        botones.add_widget(agregar_reloj)

        agregar_fecha = Button(text="Agregar Fecha")
        agregar_fecha.bind(on_press=lambda x: self.agregar_elemento("fecha"))
        botones.add_widget(agregar_fecha)

        enviar = Button(text="Enviar")
        enviar.bind(on_press=self.enviar_configuracion)
        botones.add_widget(enviar)

        root.add_widget(botones)
        return root

    def agregar_elemento(self, tipo):
        self.lista.add_widget(Elemento(tipo=tipo))

    def enviar_configuracion(self, instance):
        secuencia = []
        for elem in reversed(self.lista.children):  # Revertido por cómo se agregan en GridLayout
            secuencia.append({
                'tipo': elem.tipo,
                'tiempo': elem.tiempo_input.text,
                'repeticiones': elem.repeticiones_input.text
            })
        print("Configuración enviada:", secuencia)
        # Aquí puedes enviar vía socket o HTTP a la Raspberry o PC

        # Enviar imágenes primero (en un hilo para no bloquear UI)
        threading.Thread(target=self.enviar_imagenes_y_config, args=(secuencia,)).start()

    def enviar_imagenes_y_config(self, secuencia):
        url_base = "http://fuente-control.local:5000"
        # Enviar cada imagen al servidor (evitar repetir si hay muchas iguales)
        imagenes_enviadas = set()
        for elem in secuencia:
            if elem['tipo'] == "imagen" and elem['imagen_nombre'] not in imagenes_enviadas:
                ruta = None
                # Buscar ruta local en los widgets
                for widget in self.lista.children:
                    if getattr(widget, 'ruta_imagen', None) and os.path.basename(widget.ruta_imagen) == elem[
                        'imagen_nombre']:
                        ruta = widget.ruta_imagen
                        break
                if ruta:
                    try:
                        print(f"Enviando imagen {elem['imagen_nombre']}...")
                        with open(ruta, 'rb') as f:
                            files = {'imagen': (elem['imagen_nombre'], f, 'image/png')}
                            res = requests.post(f"{url_base}/subir-imagen", files=files)
                            print(res.json())
                        imagenes_enviadas.add(elem['imagen_nombre'])
                        # Envío de imagen
                    except Exception as e:
                        print(f"Error al enviar imagen {elem['imagen_nombre']}: {e}")
                        Clock.schedule_once(lambda dt: self.mostrar_error(
                            "Error al enviar imagen",
                            f"No se pudo enviar la imagen '{elem['imagen_nombre']}'.\n\n"
                            f"Verifica:\n• Que la Raspberry esté encendida.\n"
                            f"• Que esté conectada a la misma red Wi-Fi.\n"
                            f"• Que el servidor esté ejecutándose en la Raspberry."
                        ))
        # Luego enviar configuración
        try:
            print("Enviando configuración JSON...")
            res = requests.post(f"{url_base}/configuracion", json=secuencia)
            print("Respuesta configuración:", res.json())
        # Envío de configuración
        except Exception as e:
            print("Error al enviar configuración:", e)

            Clock.schedule_once(lambda dt: self.mostrar_error(
                "Error al enviar configuración",
                "No se pudo conectar con la Raspberry Pi para enviar la configuración.\n\n"
                "Posibles soluciones:\n"
                "• Asegúrate de que el celular y la Raspberry estén en la misma red Wi-Fi.\n"
                "• Verifica que el servidor esté corriendo en la Raspberry.\n"
            ))

    def seleccionar_imagen(self, instance):
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView(path=os.getcwd(), filters=["*.png", "*.jpg", "*.jpeg"])
        content.add_widget(filechooser)

        btns = BoxLayout(size_hint_y=None, height=40)
        btn_aceptar = Button(text="Aceptar")
        btn_cancelar = Button(text="Cancelar")
        btns.add_widget(btn_aceptar)
        btns.add_widget(btn_cancelar)
        content.add_widget(btns)

        popup = Popup(title="Seleccionar imagen", content=content, size_hint=(0.9, 0.9))

        def aceptar(instance):
            if filechooser.selection:
                imagen_path = filechooser.selection[0]
                self.agregar_elemento_personalizado(imagen_path)
                popup.dismiss()

        def cancelar(instance):
            popup.dismiss()

        btn_aceptar.bind(on_press=aceptar)
        btn_cancelar.bind(on_press=cancelar)

        popup.open()

    def agregar_elemento_personalizado(self, ruta):
        self.lista.add_widget(Elemento(tipo=ruta))


    def mostrar_error(self, titulo, mensaje):
        contenido = BoxLayout(orientation='vertical')
        contenido.add_widget(Label(text=mensaje))

        btn_cerrar = Button(text='Cerrar', size_hint=(1, 0.2))
        contenido.add_widget(btn_cerrar)

        popup = Popup(title=titulo, content=contenido, size_hint=(0.8, 0.4))
        btn_cerrar.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    FuenteControlApp().run()
