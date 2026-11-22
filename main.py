from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.core.window import Window

Window.clearcolor = (0.94, 0.96, 0.98, 1)


class ControlVentasApp(App):

    def build(self):
        self.campos = {}
        self.parqueos = []

        scroll = ScrollView()

        self.contenedor = GridLayout(
            cols=1,
            spacing=10,
            padding=15,
            size_hint_y=None
        )
        self.contenedor.bind(
            minimum_height=self.contenedor.setter('height')
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
            minimum_height=self.lista_parqueos.setter('height')
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

        self.resultado = Label(
            text="Aquí aparecerá el resumen de ventas",
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=250
        )

        self.contenedor.add_widget(self.resultado)

        return scroll

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
            self.resultado.text = "Ingrese una cantidad valida de parqueos."

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

            total_parqueos = sum(
                float(p.text) if p.text.strip() else 0
                for p in self.parqueos
            )

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
            self.resultado.text = (
                "Error: revise que todos los valores "
                "ingresados sean numeros validos."
            )


if __name__ == "__main__":
    ControlVentasApp().run()
