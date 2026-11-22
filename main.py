
import os
import json
import sqlite3
from datetime import datetime

from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup


# COLORES DE LA INTERFAZ
AZUL_FONDO = (0.035, 0.055, 0.10, 1)
AZUL_TARJETA = (0.075, 0.105, 0.17, 1)
NARANJA = (1, 0.43, 0.12, 1)
BLANCO = (0.95, 0.96, 0.98, 1)
GRIS = (0.68, 0.73, 0.81, 1)
VERDE = (0.18, 0.68, 0.43, 1)

Window.clearcolor = AZUL_FONDO


class ControlVentasApp(App):

    def build(self):
        self.campos = {}
        self.parqueos = []
        self.ultimo_calculo = None
        self.cierre_guardado = False

        # Base de datos local
        self.db_path = os.path.join(
            self.user_data_dir,
            "control_ventas.db"
        )

        self.inicializar_bd()

        # Contenedor desplazable
        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(5)
        )

        self.contenedor = BoxLayout(
            orientation="vertical",
            spacing=dp(14),
            padding=[dp(15), dp(18), dp(15), dp(25)],
            size_hint_y=None
        )

        self.contenedor.bind(
            minimum_height=self.contenedor.setter("height")
        )

        scroll.add_widget(self.contenedor)

        # ENCABEZADO
        encabezado = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(105),
            spacing=dp(5)
        )

        encabezado.add_widget(
            Label(
                text="[b]CONTROL DE VENTAS[/b]",
                markup=True,
                font_size="25sp",
                color=NARANJA,
                halign="left",
                valign="middle"
            )
        )

        encabezado.add_widget(
            Label(
                text="Registro y cierre de ventas",
                font_size="14sp",
                color=GRIS,
                halign="left",
                valign="middle"
            )
        )

        self.contenedor.add_widget(encabezado)

        # LECTURAS INICIALES
        self.crear_seccion(
            "LECTURAS INICIALES - GASOLINA"
        )

        for i in range(1, 5):
            self.agregar_campo(
                f"Entrada gasolina {i}",
                f"eg{i}"
            )

        self.crear_seccion(
            "LECTURAS INICIALES - DIESEL"
        )

        for i in range(1, 3):
            self.agregar_campo(
                f"Entrada diesel {i}",
                f"ed{i}"
            )

        # LECTURAS FINALES
        self.crear_seccion(
            "LECTURAS FINALES - GASOLINA"
        )

        for i in range(1, 5):
            self.agregar_campo(
                f"Salida gasolina {i}",
                f"sg{i}"
            )

        self.crear_seccion(
            "LECTURAS FINALES - DIESEL"
        )

        for i in range(1, 3):
            self.agregar_campo(
                f"Salida diesel {i}",
                f"sd{i}"
            )

        # OTROS INGRESOS
        self.crear_seccion("OTROS INGRESOS")

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

        self.lista_parqueos = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8)
        )

        self.lista_parqueos.bind(
            minimum_height=self.lista_parqueos.setter("height")
        )

        self.contenedor.add_widget(self.lista_parqueos)

        # FORMAS DE PAGO
        self.crear_seccion("FORMAS DE PAGO")

        self.agregar_campo(
            "Dinero recibido en monedas",
            "monedas"
        )

        self.agregar_campo(
            "Venta por datáfono",
            "datafono"
        )

        # DESCUENTOS
        self.crear_seccion("DESCUENTOS")

        self.contenedor.add_widget(
            Label(
                text="¿Hubo descuento?",
                color=BLANCO,
                size_hint_y=None,
                height=dp(30),
                halign="left"
            )
        )

        self.respuesta_descuento = Spinner(
            text="No",
            values=("No", "Si"),
            size_hint_y=None,
            height=dp(48),
            background_normal="",
            background_color=AZUL_TARJETA,
            color=BLANCO
        )

        self.contenedor.add_widget(
            self.respuesta_descuento
        )

        self.agregar_campo(
            "Valor del descuento",
            "descuento"
        )

        # BOTÓN CALCULAR
        self.boton(
            "CALCULAR VENTAS",
            self.calcular,
            color=NARANJA
        )

        # RESULTADO
        self.crear_seccion("RESUMEN DEL CIERRE")

        self.resultado = Label(
            text="Aquí aparecerá el resumen de ventas.",
            color=BLANCO,
            font_size="15sp",
            halign="left",
            valign="top",
            size_hint_y=None,
            height=dp(100)
        )

        self.resultado.bind(
            width=self.actualizar_ancho_resultado
        )

        self.resultado.bind(
            texture_size=self.actualizar_alto_resultado
        )

        self.contenedor.add_widget(self.resultado)

        # GUARDAR
        self.boton(
            "GUARDAR CIERRE",
            self.guardar_cierre,
            color=VERDE
        )

        # HISTORIAL
        self.boton(
            "VER HISTORIAL",
            self.ver_historial
        )

        return scroll

    # BASE DE DATOS
    def inicializar_bd(self):
        conexion = sqlite3.connect(self.db_path)

        cursor = conexion.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cierres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                datos TEXT
            )
        """)

        conexion.commit()
        conexion.close()

    # SECCIONES VISUALES
    def crear_seccion(self, titulo):
        tarjeta = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(14),
            size_hint_y=None
        )

        with tarjeta.canvas.before:
            Color(*AZUL_TARJETA)
            fondo = RoundedRectangle(
                pos=tarjeta.pos,
                size=tarjeta.size,
                radius=[dp(14)]
            )

        tarjeta.bind(
            pos=lambda instancia, valor:
            setattr(fondo, "pos", valor)
        )

        tarjeta.bind(
            size=lambda instancia, valor:
            setattr(fondo, "size", valor)
        )

        tarjeta.bind(
            minimum_height=tarjeta.setter("height")
        )

        etiqueta = Label(
            text=f"[b]{titulo}[/b]",
            markup=True,
            color=NARANJA,
            font_size="16sp",
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(32)
        )

        tarjeta.add_widget(etiqueta)

        self.contenedor.add_widget(tarjeta)

        self.tarjeta_actual = tarjeta

    # CAMPOS DE ENTRADA
    def agregar_campo(self, nombre, clave):
        caja = BoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_y=None,
            height=dp(76)
        )

        etiqueta = Label(
            text=nombre,
            color=GRIS,
            font_size="14sp",
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(25)
        )

        entrada = TextInput(
            hint_text="Ingrese el valor",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(45),
            font_size="16sp",
            padding=[dp(12), dp(10)],
            background_normal="",
            background_active="",
            background_color=(0.12, 0.16, 0.23, 1),
            foreground_color=BLANCO,
            cursor_color=NARANJA,
            hint_text_color=GRIS
        )

        caja.add_widget(etiqueta)
        caja.add_widget(entrada)

        self.tarjeta_actual.add_widget(caja)

        self.campos[clave] = entrada

    # BOTONES
    def boton(self, texto, funcion, color=None):
        if color is None:
            color = (0.13, 0.23, 0.36, 1)

        btn = Button(
            text=texto,
            size_hint_y=None,
            height=dp(52),
            background_normal="",
            background_down="",
            background_color=color,
            color=BLANCO,
            font_size="15sp",
            bold=True
        )

        btn.bind(on_press=funcion)

        self.contenedor.add_widget(btn)

        return btn

    # OBTENER VALORES
    def obtener(self, clave):
        valor = self.campos[clave].text.strip()

        if valor == "":
            return 0

        return float(valor)

    # CREAR CAMPOS DE PARQUEOS
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
                    spacing=dp(4),
                    size_hint_y=None,
                    height=dp(76)
                )

                etiqueta = Label(
                    text=f"Valor del parqueo {i}",
                    color=GRIS,
                    font_size="14sp",
                    halign="left",
                    size_hint_y=None,
                    height=dp(25)
                )

                entrada = TextInput(
                    hint_text="Valor en pesos",
                    multiline=False,
                    input_filter="float",
                    size_hint_y=None,
                    height=dp(45),
                    font_size="16sp",
                    background_normal="",
                    background_active="",
                    background_color=(0.12, 0.16, 0.23, 1),
                    foreground_color=BLANCO,
                    cursor_color=NARANJA
                )

                caja.add_widget(etiqueta)
                caja.add_widget(entrada)

                self.lista_parqueos.add_widget(caja)
                self.parqueos.append(entrada)

            self.mensaje(
                "Parqueos",
                f"Se crearon {cantidad} campos de parqueo."
            )

        except ValueError:
            self.mensaje(
                "Error",
                "Ingrese una cantidad válida entre 0 y 100."
            )

    # ACTUALIZAR TAMAÑO DEL RESULTADO
    def actualizar_ancho_resultado(self, instancia, ancho):
        instancia.text_size = (ancho, None)

    def actualizar_alto_resultado(self, instancia, tamano):
        instancia.height = max(
            dp(100),
            tamano[1] + dp(15)
        )

    # CALCULAR VENTAS
    def calcular(self, instancia):
        try:
            gasolina = 0
            diesel = 0

            # GASOLINA
            for i in range(1, 5):
                gasolina += abs(
                    self.obtener(f"sg{i}") -
                    self.obtener(f"eg{i}")
                )

            # DIESEL
            for i in range(1, 3):
                diesel += abs(
                    self.obtener(f"sd{i}") -
                    self.obtener(f"ed{i}")
                )

            total_gasolina = gasolina * 15790
            total_diesel = diesel * 10750

            aditivos = self.obtener("aditivos")

            cantidad_parqueos = int(
                self.obtener("cantidad_parqueos")
            )

            if cantidad_parqueos != len(self.parqueos):
                self.mensaje(
                    "Parqueos",
                    "Primero cree los campos de parqueos."
                )
                return

            total_parqueos = sum(
                float(p.text.strip()) if p.text.strip() else 0
                for p in self.parqueos
            )

            valores_parqueos = [
                float(p.text.strip()) if p.text.strip() else 0
                for p in self.parqueos
            ]

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

            # GUARDAR TODOS LOS DATOS DEL CIERRE
            datos = {
                "lecturas_iniciales": {
                    f"eg{i}": self.obtener(f"eg{i}")
                    for i in range(1, 5)
                },
                "lecturas_finales": {
                    f"sg{i}": self.obtener(f"sg{i}")
                    for i in range(1, 5)
                },
                "diesel_inicial": {
                    f"ed{i}": self.obtener(f"ed{i}")
                    for i in range(1, 3)
                },
                "diesel_final": {
                    f"sd{i}": self.obtener(f"sd{i}")
                    for i in range(1, 3)
                },
                "gasolina": gasolina,
                "diesel": diesel,
                "total_gasolina": total_gasolina,
                "total_diesel": total_diesel,
                "aditivos": aditivos,
                "cantidad_parqueos": cantidad_parqueos,
                "valores_parqueos": valores_parqueos,
                "total_parqueos": total_parqueos,
                "total_ventas": total_ventas,
                "monedas": monedas,
                "datafono": datafono,
                "descuento": descuento,
                "total_final": total_final
            }

            self.ultimo_calculo = datos
            self.cierre_guardado = False

            self.resultado.text = (
                "[b]RESUMEN DE VENTAS[/b]\n\n"
                f"Gasolina: {gasolina:.2f} galones\n"
                f"Diesel: {diesel:.2f} galones\n\n"
                f"Venta gasolina: ${total_gasolina:,.0f}\n"
                f"Venta diesel: ${total_diesel:,.0f}\n"
                f"Aditivos: ${aditivos:,.0f}\n"
                f"Parqueos: ${total_parqueos:,.0f}\n\n"
                f"[b]TOTAL VENTAS: ${total_ventas:,.0f}[/b]\n\n"
                f"Dinero en monedas: ${monedas:,.0f}\n"
                f"Venta por datáfono: ${datafono:,.0f}\n"
                f"Descuento: ${descuento:,.0f}\n\n"
                f"[b]TOTAL A ENTREGAR:\n"
                f"${total_final:,.0f} COP[/b]"
            )

        except (ValueError, TypeError):
            self.mensaje(
                "Error",
                "Revise que todos los valores ingresados sean números válidos."
            )

    # GUARDAR CIERRE
    def guardar_cierre(self, instancia):
        if self.ultimo_calculo is None:
            self.mensaje(
                "Atención",
                "Primero debe calcular las ventas."
            )
            return

        if self.cierre_guardado:
            self.mensaje(
                "Atención",
                "Este cierre ya fue guardado."
            )
            return

        try:
            fecha = datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"
            )

            conexion = sqlite3.connect(self.db_path)
            cursor = conexion.cursor()

            cursor.execute(
                "INSERT INTO cierres (fecha, datos) VALUES (?, ?)",
                (
                    fecha,
                    json.dumps(
                        self.ultimo_calculo,
                        ensure_ascii=False
                    )
                )
            )

            conexion.commit()
            conexion.close()

            self.cierre_guardado = True

            self.mensaje(
                "Cierre guardado",
                "El cierre se guardó correctamente en el historial."
            )

        except sqlite3.Error as error:
            self.mensaje(
                "Error de base de datos",
                str(error)
            )

    # VER HISTORIAL
    def ver_historial(self, instancia):
        try:
            conexion = sqlite3.connect(self.db_path)
            cursor = conexion.cursor()

            cursor.execute(
                "SELECT fecha, datos FROM cierres ORDER BY id DESC LIMIT 50"
            )

            registros = cursor.fetchall()
            conexion.close()

            if not registros:
                self.mensaje(
                    "Historial",
                    "Todavía no hay cierres guardados."
                )
                return

            texto = ""

            for fecha, datos_json in registros:
                datos = json.loads(datos_json)

                texto += (
                    f"FECHA: {fecha}\n\n"
                    f"Gasolina: {datos.get('gasolina', 0):.2f} galones\n"
                    f"Diesel: {datos.get('diesel', 0):.2f} galones\n\n"
                    f"Venta gasolina: ${datos.get('total_gasolina', 0):,.0f}\n"
                    f"Venta diesel: ${datos.get('total_diesel', 0):,.0f}\n"
                    f"Aditivos: ${datos.get('aditivos', 0):,.0f}\n"
                    f"Parqueos: ${datos.get('total_parqueos', 0):,.0f}\n\n"
                    f"Dinero en monedas: ${datos.get('monedas', 0):,.0f}\n"
                    f"Venta por datáfono: ${datos.get('datafono', 0):,.0f}\n"
                    f"Descuento: ${datos.get('descuento', 0):,.0f}\n\n"
                    f"TOTAL VENTAS: ${datos.get('total_ventas', 0):,.0f}\n"
                    f"TOTAL A ENTREGAR: ${datos.get('total_final', 0):,.0f} COP\n"
                    "------------------------------------\n\n"
                )

            contenido = BoxLayout(
                orientation="vertical",
                spacing=dp(10),
                padding=dp(12)
            )

            scroll = ScrollView(
                do_scroll_x=False
            )

            etiqueta = Label(
                text=texto,
                color=BLANCO,
                font_size="14sp",
                halign="left",
                valign="top",
                size_hint_y=None
            )

            etiqueta.bind(
                width=lambda instancia, ancho:
                setattr(instancia, "text_size", (ancho, None))
            )

            etiqueta.bind(
                texture_size=lambda instancia, tamano:
                setattr(instancia, "height", tamano[1] + dp(20))
            )

            scroll.add_widget(etiqueta)
            contenido.add_widget(scroll)

            popup = Popup(
                title="Historial de cierres",
                content=contenido,
                size_hint=(0.94, 0.85),
                separator_color=NARANJA,
                background_color=AZUL_FONDO
            )

            popup.open()

        except (sqlite3.Error, json.JSONDecodeError) as error:
            self.mensaje(
                "Error",
                f"No se pudo consultar el historial: {error}"
            )

    # MENSAJES
    def mensaje(self, titulo, texto):
        contenido = BoxLayout(
           
