
import os
import json
import sqlite3
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.core.window import Window

Window.clearcolor = (0.94, 0.96, 0.98, 1)


class ControlVentasApp(App):

    def build(self):
        self.campos = {}
        self.parqueos = []
        self.ultimo_calculo = None

        # Crear base de datos SQLite
        self.db_path = os.path.join(
            self.user_data_dir,
            "control_ventas.db"
        )

        self.inicializar_bd()

        scroll = ScrollView()

        self.contenedor = GridLayout(
            cols=1,
            spacing=10,
            padding=15,
            size_hint_y=None
        )

        self.contenedor.bind(
            minimum_height=self.contenedor.setter("height")
        )

        scroll.add_widget(self.contenedor)

        self.titulo("CONTROL DE VENTAS")
        self.titulo("LECTURAS INICIALES - GASOLINA")

        for i in range(1, 5):
            self.agregar_campo(
                f"Entrada gasolina {i}",
                f"eg{i}"
            )

        self.titulo("LECTURAS INICIALES - DIESEL")

        for i in range(1, 3):
            self.agregar_campo(
                f"Entrada diesel {i}",
                f"ed{i}"
            )

        self.titulo("LECTURAS FINALES - GASOLINA")

        for i in range(1, 5):
            self.agregar_campo(
                f"Salida gasolina {i}",
                f"sg{i}"
            )

        self.titulo("LECTURAS FINALES - DIESEL")

        for i in range(1, 3):
            self.agregar_campo(
                f"Salida diesel {i}",
                f"sd{i}"
            )

        self.titulo("OTROS INGRESOS")

        self.agregar_campo(
            "Valor total de aditivos",
            "aditivos"
        )

        self.agregar_campo(
            "Cantidad de parqueos",
            "cantidad_parqueos"
        )

        self.boton(
            "CREAR CAMPOS DE PARQUEOS",
            self.crear_parqueos
        )

        self.lista_parqueos = GridLayout(
            cols=1,
            spacing=5,
            size_hint_y=None
        )

        self.lista_parqueos.bind(
            minimum_height=self.lista_parqueos.setter("height")
        )

        self.contenedor.add_widget(self.lista_parqueos)

        self.titulo("FORMAS DE PAGO")

        self.agregar_campo("Dinero en monedas", "monedas")
        self.agregar_campo("Venta por datafono", "datafono")

        self.titulo("DESCUENTOS")

        self.contenedor.add_widget(
            Label(
                text="¿Hubo descuento?",
                color=(0, 0, 0, 1),
                size_hint_y=None,
                height=35
            )
        )

        self.respuesta_descuento = Spinner(
            text="No",
            values=("No", "Si"),
            size_hint_y=None,
            height=45
        )

        self.contenedor.add_widget(
            self.respuesta_descuento
        )

        self.agregar_campo(
            "Valor del descuento",
            "descuento"
        )

        self.boton(
            "CALCULAR VENTAS",
            self.calcular
        )

        self.boton(
            "GUARDAR CIERRE",
            self.guardar_cierre
        )

        self.boton(
            "VER HISTORIAL",
            self.ver_historial
        )

        self.resultado = Label(
            text="Aquí aparecerá el resumen de ventas",
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=250
        )

        self.contenedor.add_widget(self.resultado)

        return scroll

    # ---------------------------------
    # BASE DE DATOS SQLITE
    # ---------------------------------

    def inicializar_bd(self):

        conexion = sqlite3.connect(self.db_path)

        cursor = conexion.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cierres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                datos TEXT NOT NULL
            )
        """)

        conexion.commit()
        conexion.close()

    # ---------------------------------
    # ELEMENTOS DE INTERFAZ
    # ---------------------------------

    def titulo(self, texto):

        etiqueta = Label(
            text=texto,
            bold=True,
            color=(0.05, 0.25, 0.40, 1),
            size_hint_y=None,
            height=45
        )

        self.contenedor.add_widget(etiqueta)

    def agregar_campo(self, nombre, clave):

        caja = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=75,
            spacing=3
        )

        etiqueta = Label(
            text=nombre,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=30
        )

        entrada = TextInput(
            hint_text="Ingrese el valor",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=40
        )

        caja.add_widget(etiqueta)
        caja.add_widget(entrada)

        self.contenedor.add_widget(caja)

        self.campos[clave] = entrada

    def boton(self, texto, funcion):

        btn = Button(
            text=texto,
            size_hint_y=None,
            height=50,
            background_normal="",
            background_color=(0.05, 0.40, 0.65, 1)
        )

        btn.bind(on_press=funcion)

        self.contenedor.add_widget(btn)

    def obtener(self, clave):

        valor = self.campos[clave].text.strip()

        if valor == "":
            return 0

        return float(valor)

    # ---------------------------------
    # REGISTRO DE PARQUEOS
    # ---------------------------------

    def crear_parqueos(self, instancia):

        try:

            cantidad = int(
                self.obtener("cantidad_parqueos")
            )

            if cantidad < 0 or cantidad > 100:
                raise ValueError

            self.lista_parqueos.clear_widgets()
            self.parqueos = []

            for i in range(1, cantidad + 1):

                caja = BoxLayout(
                    orientation="vertical",
                    size_hint_y=None,
                    height=70
                )

                caja.add_widget(
                    Label(
                        text=f"Valor del parqueo {i}",
                        color=(0, 0, 0, 1)
                    )
                )

                entrada = TextInput(
                    hint_text="Valor en pesos",
                    multiline=False,
                    input_filter="float",
                    size_hint_y=None,
                    height=40
                )

                caja.add_widget(entrada)

                self.lista_parqueos.add_widget(caja)

                self.parqueos.append(entrada)

        except ValueError:

            self.resultado.text = (
                "Ingrese una cantidad valida de parqueos."
            )

    # ---------------------------------
    # CALCULAR VENTAS
    # ---------------------------------

    def calcular(self, instancia):

        try:

            gasolina = 0
            diesel = 0

            for i in range(1, 5):

                gasolina += abs(
                    self.obtener(f"sg{i}") -
                    self.obtener(f"eg{i}")
                )

            for i in range(1, 3):

                diesel += abs(
                    self.obtener(f"sd{i}") -
                    self.obtener(f"ed{i}")
                )

            total_gasolina = gasolina * 15790
            total_diesel = diesel * 10750

            aditivos = self.obtener("aditivos")

            valores_parqueos = [
                float(p.text) if p.text.strip() else 0
                for p in self.parqueos
            ]

            total_parqueos = sum(valores_parqueos)

            total_ventas = (
                total_gasolina +
                total_diesel +
                aditivos +
                total_parqueos
            )

            monedas = self.obtener("monedas")
            datafono = self.obtener("datafono")

            descuento = 0

            if self.respuesta_descuento.text == "Si":
                descuento = self.obtener("descuento")

            total_final = (
                total_ventas -
                monedas -
                datafono -
                descuento
            )

            # Preparar datos para guardar
            self.ultimo_calculo = {
                "lecturas": {
                    clave: self.obtener(clave)
                    for clave in self.campos
                    if clave.startswith(("eg", "ed", "sg", "sd"))
                },
                "gasolina": gasolina,
                "diesel": diesel,
                "total_gasolina": total_gasolina,
                "total_diesel": total_diesel,
                "aditivos": aditivos,
                "parqueos": valores_parqueos,
                "total_parqueos": total_parqueos,
                "total_ventas": total_ventas,
                "monedas": monedas,
                "datafono": datafono,
                "descuento": descuento,
                "total_final": total_final
            }

            self.resultado.text = (
                "RESUMEN DE VENTAS\n\n"
                f"Gasolina: {gasolina:.2f} galones\n"
                f"Diesel: {diesel:.2f} galones\n\n"
                f"Venta gasolina: ${total_gasolina:,.0f}\n"
                f"Venta diesel: ${total_diesel:,.0f}\n"
                f"Aditivos: ${aditivos:,.0f}\n"
                f"Parqueos: ${total_parqueos:,.0f}\n\n"
                f"Total ventas: ${total_ventas:,.0f}\n"
                f"Monedas: ${monedas:,.0f}\n"
                f"Datafono: ${datafono:,.0f}\n"
                f"Descuento: ${descuento:,.0f}\n\n"
                f"TOTAL A ENTREGAR:\n"
                f"${total_final:,.0f} COP"
            )

        except ValueError:

            self.ultimo_calculo = None

            self.resultado.text = (
                "Error: revise que todos los valores "
                "ingresados sean numeros validos."
            )

    # ---------------------------------
    # GUARDAR CIERRE EN SQLITE
    # ---------------------------------

    def guardar_cierre(self, instancia):

        if self.ultimo_calculo is None:

            self.mensaje(
                "Primero debe calcular las ventas."
            )

            return

        try:

            fecha = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            datos = json.dumps(
                self.ultimo_calculo,
                ensure_ascii=False
            )

            conexion = sqlite3.connect(self.db_path)

            cursor = conexion.cursor()

            cursor.execute(
                """
                INSERT INTO cierres (fecha, datos)
                VALUES (?, ?)
                """,
                (fecha, datos)
            )

            conexion.commit()
            conexion.close()

            self.mensaje(
                "El cierre se guardo correctamente."
            )

        except Exception as error:

            self.mensaje(
                f"No se pudo guardar el cierre:\n{error}"
            )

    # ---------------------------------
    # CONSULTAR HISTORIAL
    # ---------------------------------

    def ver_historial(self, instancia):

        conexion = sqlite3.connect(self.db_path)

        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT id, fecha, datos
            FROM cierres
            ORDER BY id DESC
            LIMIT 50
            """
        )

        registros = cursor.fetchall()

        conexion.close()

        if not registros:

            texto = "Todavia no hay cierres guardados."

        else:

            texto = ""

            for registro in registros:

                identificador = registro[0]
                fecha = registro[1]
                datos = json.loads(registro[2])

                texto += (
                    f"CIERRE #{identificador}\n"
                    f"Fecha: {fecha}\n"
                    f"Gasolina: {datos['gasolina']:.2f} galones\n"
                    f"Diesel: {datos['diesel']:.2f} galones\n"
                    f"Total: ${datos['total_final']:,.0f} COP\n"
                    "----------------------------\n\n"
                )

        contenido = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=10
        )

        campo = TextInput(
            text=texto,
            readonly=True,
            multiline=True,
            size_hint_y=1
        )

        cerrar = Button(
            text="CERRAR",
            size_hint_y=None,
            height=50
        )

        contenido.add_widget(campo)
        contenido.add_widget(cerrar)

        ventana = Popup(
            title="HISTORIAL DE CIERRES",
            content=contenido,
            size_hint=(0.95, 0.85)
        )

        cerrar.bind(
            on_press=ventana.dismiss
        )

        ventana.open()

    # ---------------------------------
    # MENSAJES
    # ---------------------------------

    def mensaje(self, texto):

        contenido = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=10
        )

        etiqueta = Label(text=texto)

        cerrar = Button(
            text="ACEPTAR",
            size_hint_y=None,
            height=45
        )

        contenido.add_widget(etiqueta)
        contenido.add_widget(cerrar)

        ventana = Popup(
            title="CONTROL DE VENTAS",
            content=contenido,
            size_hint=(0.85, 0.35)
        )

        cerrar.bind(
            on_press=ventana.dismiss
        )

        ventana.open()


if __name__ == "__main__":
    ControlVentasApp().run()
        
