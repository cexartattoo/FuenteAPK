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

if __name__ == '__main__':
    PermisoApp().run()
