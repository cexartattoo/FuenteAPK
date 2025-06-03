from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup


class BarraSuperior(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 50
        self.padding = 10
        self.spacing = 10

        titulo = Label(
            text="Mi Aplicación",
            font_size=18,
            size_hint_x=0.9,
            color=(1, 1, 1, 1)
        )

        boton_info = Button(
            text="ℹ️",
            size_hint_x=0.1
        )
        boton_info.bind(on_press=self.mostrar_info)

        self.add_widget(titulo)
        self.add_widget(boton_info)

    def mostrar_info(self, instance):
        contenido = BoxLayout(orientation='vertical', padding=10, spacing=10)
        contenido.add_widget(Label(
            text="Mi Aplicación v1.0\n\nDesarrollado por Ramiro\n© 2025 Todos los derechos reservados",
            halign='center'
        ))

        btn_cerrar = Button(text="Cerrar", size_hint_y=None, height=40)
        popup = Popup(title="Información", content=contenido,
                      size_hint=(None, None), size=(300, 300),
                      auto_dismiss=False)

        btn_cerrar.bind(on_press=popup.dismiss)
        contenido.add_widget(btn_cerrar)
        popup.open()


class MiApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        barra = BarraSuperior()
        layout.add_widget(barra)

        # Aquí iría el resto de tu contenido principal:
        layout.add_widget(Label(text="Contenido principal", font_size=16))

        return layout


if __name__ == '__main__':
    MiApp().run()
