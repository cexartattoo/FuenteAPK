'''
from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)
'''

from plyer import filechooser

from kivy.uix.widget import Widget

from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import requests
import threading
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.properties import BooleanProperty
import os

from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from android.permissions import request_permissions, check_permission, Permission
from jnius import autoclass

# Para mostrar Toasts
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Toast = autoclass('android.widget.Toast')

class MainWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.boton_verificar = Button(text="Verificar permisos")
        self.boton_verificar.bind(on_press=self.verificar_permisos)
        self.add_widget(self.boton_verificar)

        self.boton_reintentar = Button(text="Volver a pedir permisos", disabled=True)
        self.boton_reintentar.bind(on_press=self.pedir_permisos)
        self.add_widget(self.boton_reintentar)

    def mostrar_toast(self, mensaje):
        Toast.makeText(PythonActivity.mActivity, mensaje, Toast.LENGTH_LONG).show()

    def verificar_permisos(self, instance):
        if check_permission(Permission.READ_EXTERNAL_STORAGE):
            self.mostrar_toast("✅ Permisos otorgados")
            self.boton_reintentar.disabled = True
        else:
            self.mostrar_toast("❌ Permisos denegados. Debes aceptarlos.")
            self.boton_reintentar.disabled = False

    def pedir_permisos(self, instance=None):
        request_permissions(
            [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE],
            self.callback_permiso
        )

    def callback_permiso(self, permisos, resultados):
        if all(resultados):
            self.mostrar_toast("✅ Permisos aceptados")
            self.boton_reintentar.disabled = True
        else:
            self.mostrar_toast("❌ Aún no se otorgaron permisos")
            self.boton_reintentar.disabled = False

class PermisoApp(App):
    def build(self):
        return MainWidget()



def mostrar_popup(titulo, mensaje):
    box = BoxLayout(orientation='vertical', padding=10, spacing=10)
    box.add_widget(Label(text=mensaje))

    btn_cerrar = Button(text='Cerrar', size_hint=(1, 0.3))
    box.add_widget(btn_cerrar)

    popup = Popup(title=titulo, content=box,
                  size_hint=(None, None), size=(300, 200),
                  auto_dismiss=False)
    btn_cerrar.bind(on_press=popup.dismiss)
    popup.open()


class Elemento(FloatLayout):
    dragging = BooleanProperty(False)

    def __init__(self, tipo="imagen", **kwargs):
        super().__init__(size_hint_y=None, height=100, **kwargs)
        self.tipo = tipo

        # Botón eliminar: fijo a la derecha, inicialmente visible pero estará "detrás" del contenido
        self.eliminar_btn = Button(
            text="Eliminar",
            size_hint=(0.1, 1),
            pos_hint={'right': 1, 'y': 0},
            background_color=(1, 0, 0, 1)
        )
        self.eliminar_btn.bind(on_press=self.eliminar)
        self.add_widget(self.eliminar_btn)


        self.contenido = BoxLayout(orientation='horizontal', size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})
        self.add_widget(self.contenido)

        # Iconox
        if os.path.isfile(tipo):
            self.icono = Image(source=tipo, size_hint=(0.2, 1))
        else:
            self.icono = Image(source=f"{tipo}.png", size_hint=(0.2, 1))
        self.contenido.add_widget(self.icono)

        # Inputs y botón para drag
        self.tiempo_input = TextInput(hint_text="Segundos", size_hint=(0.2, 1), input_filter='int')
        self.contenido.add_widget(self.tiempo_input)

        self.repeticiones_input = TextInput(hint_text="Repeticiones", size_hint=(0.2, 1), input_filter='int')
        self.contenido.add_widget(self.repeticiones_input)

        self.drag_handle = Button(
                background_normal='iconos/desplazarse_inv.png',
                background_down='iconos/boton_usado.png',
                size_hint=(0.1, 1),
            )
        self.drag_handle.bind(on_touch_down=self.verificar_presion)
        self.contenido.add_widget(self.drag_handle)

        self.long_press_trigger = None
        #pedir_permisos()

    def verificar_presion(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.long_press_trigger = Clock.schedule_once(lambda dt: self.empezar_arrastrar(touch), 0.3)

    def empezar_arrastrar(self, touch):
        if not self.parent:
            return
        self.dragging = True
        self.drag_start_y = touch.y
        self.original_index = self.parent.children.index(self)
        self.height *= 1.1
        self.opacity = 0.7

    def on_touch_move(self, touch):
        if self.dragging:
            # Lógica para drag vertical (ordenar elementos)
            self.center_y = touch.y
            self.actualizar_indice()
        elif self.collide_point(*touch.pos):
            # Swipe horizontal para mostrar boton eliminar
            dx = touch.x - touch.ox
            if abs(dx) > 10:
                # Limitar el desplazamiento a la anchura del boton eliminar
                new_x = max(-self.eliminar_btn.width, min(0, dx))
                # Posición relativa para pos_hint
                self.contenido.pos_hint = {'x': new_x / self.width, 'y': 0}
                self.contenido.canvas.ask_update()
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.dragging:
            self.dragging = False
            self.height /= 1.1
            self.opacity = 1
            self.actualizar_indice(final=True)
        elif self.collide_point(*touch.pos):
            current_offset = self.contenido.pos_hint.get('x', 0) * self.width
            umbral = -20  # umbral en píxeles para mostrar/ocultar botón

            if current_offset < umbral:
                # Mostrar completamente el botón eliminarr
                self.contenido.pos_hint = {'x': -self.eliminar_btn.width / self.width, 'y': 0}
            else:
                # Volver a la posición original (ocultar botón)
                self.contenido.pos_hint = {'x': 0, 'y': 0}
            self.contenido.canvas.ask_update()

        if self.long_press_trigger:
            self.long_press_trigger.cancel()
        return super().on_touch_up(touch)

    def actualizar_indice(self, *args, final=False):
        if not self.parent:
            return
        lista = self.parent
        elementos = lista.children[:]
        if self in elementos:
            elementos.remove(self)

        nueva_pos = 0
        for i, w in enumerate(reversed(elementos)):
            if self.center_y > w.center_y:
                nueva_pos = len(elementos) - i
                break
        else:
            nueva_pos = 0

        if final:
            elementos.insert(nueva_pos, self)
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

        botones = BoxLayout(size_hint=(1, 0.1), padding=10)

        def crear_boton(ruta_icono, accion):
            btn = Button(
                background_normal=ruta_icono,
                background_down='iconos/aceptar.png',
                size_hint=(None, 1),
            )
            btn.bind(on_press=accion)
            return btn

        # Espaciadores y botones intercalados
        botones.add_widget(Widget())  # Espacio al inicio

        botones.add_widget(crear_boton('iconos/imagen_inv.png', self.seleccionar_imagen))
        botones.add_widget(Widget())

        botones.add_widget(crear_boton('iconos/hora_inv.png', lambda x: self.agregar_elemento("reloj")))
        botones.add_widget(Widget())

        botones.add_widget(crear_boton('iconos/calendario_inv.png', lambda x: self.agregar_elemento("fecha")))
        botones.add_widget(Widget())

        botones.add_widget(crear_boton('iconos/enviar_inv.png', self.enviar_configuracion))
        botones.add_widget(Widget())  # Espacio al final



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
        filechooser.open_file(on_selection=self.agregar_elemento_personalizado)

    def agregar_elemento_personalizado(self, seleccion):
        ruta = seleccion[0]
        if seleccion and len(seleccion) > 0:

            mostrar_popup("Imagen seleccionada", ruta)

            self.lista.add_widget(Elemento(tipo=ruta))
        else:
            mostrar_popup("error", ruta)

    @staticmethod
    def mostrar_error(titulo, mensaje):
        contenido = BoxLayout(orientation='vertical')
        contenido.add_widget(Label(text=mensaje))

        btn_cerrar = Button(text='Cerrar', size_hint=(1, 0.2))
        contenido.add_widget(btn_cerrar)

        popup = Popup(title=titulo, content=contenido, size_hint=(0.8, 0.4))
        btn_cerrar.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    PermisoApp().run()
    FuenteControlApp().run()
