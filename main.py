import csv
import os
from datetime import date

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import platform

# Solo cambia tamaño en escritorio
if platform != 'android':
    Window.size = (360, 640)

ARCHIVO = "gastos_familia.csv"
CATEGORIAS_INGRESO = ["Sueldo","Negocio","Freelance","Arriendo","Regalo","Otro"]
CATEGORIAS_GASTO   = ["Comida","Servicios","Transporte","Salud","Educacion","Ropa","Entretenimiento","Otro"]
MESES = ["Todos","01-Enero","02-Febrero","03-Marzo","04-Abril","05-Mayo","06-Junio",
         "07-Julio","08-Agosto","09-Septiembre","10-Octubre","11-Noviembre","12-Diciembre"]

# ─────────────────────────────────────────
# DATOS
# ─────────────────────────────────────────

def get_ruta():
    if platform == 'android':
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), "gastos_familia.csv")
    return ARCHIVO

def inicializar_csv():
    ruta = get_ruta()
    if not os.path.exists(ruta):
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["tipo","descripcion","categoria","monto","fecha"])

def guardar_movimiento(tipo, descripcion, categoria, monto, fecha=None):
    if fecha is None:
        fecha = str(date.today())
    with open(get_ruta(), "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([tipo, descripcion, categoria, monto, fecha])

def leer_todos():
    todos = []
    with open(get_ruta(), "r", encoding="utf-8") as f:
        lector = csv.reader(f)
        next(lector)
        for idx, fila in enumerate(lector):
            if len(fila) == 4:
                tipo, desc, monto, fecha = fila; categoria = "Otro"
            else:
                tipo, desc, categoria, monto, fecha = fila
            todos.append((idx, tipo, desc, categoria, float(monto), fecha))
    return todos

def borrar_movimiento(indice):
    todos = leer_todos()
    with open(get_ruta(), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tipo","descripcion","categoria","monto","fecha"])
        for idx, tipo, desc, cat, monto, fecha in todos:
            if idx != indice:
                w.writerow([tipo, desc, cat, monto, fecha])

def editar_movimiento(indice, tipo, desc, cat, monto, fecha):
    todos = leer_todos()
    with open(get_ruta(), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tipo","descripcion","categoria","monto","fecha"])
        for row in todos:
            if row[0] == indice:
                w.writerow([tipo, desc, cat, monto, fecha])
            else:
                w.writerow([row[1], row[2], row[3], row[4], row[5]])

def cargar_movimientos(filtro_mes="Todos"):
    todos = leer_todos()
    ing_total = sum(m for _,t,_,_,m,_ in todos if t=="INGRESO")
    gas_total = sum(m for _,t,_,_,m,_ in todos if t=="GASTO")
    if filtro_mes == "Todos":
        return todos, ing_total, gas_total, 0.0, ing_total, gas_total
    numero_mes = filtro_mes[:2]
    movs_mes = []; ing_mes = gas_mes = saldo_ant = 0.0
    for row in todos:
        idx, tipo, desc, cat, monto, fecha = row
        mes_mov = fecha[5:7]
        if mes_mov < numero_mes:
            saldo_ant += monto if tipo=="INGRESO" else -monto
        elif mes_mov == numero_mes:
            movs_mes.append(row)
            if tipo=="INGRESO": ing_mes += monto
            else:               gas_mes += monto
    return movs_mes, ing_mes, gas_mes, saldo_ant, ing_total, gas_total

def saldo_global():
    todos = leer_todos()
    ing = sum(m for _,t,_,_,m,_ in todos if t=="INGRESO")
    gas = sum(m for _,t,_,_,m,_ in todos if t=="GASTO")
    return round(ing - gas, 2)

def cargar_categorias(filtro_mes="Todos"):
    movs, *_ = cargar_movimientos(filtro_mes)
    totales = {}
    for _, tipo, _, cat, monto, _ in movs:
        clave = f"{tipo}|{cat}"
        totales[clave] = totales.get(clave, 0) + monto
    return totales, movs

# ─────────────────────────────────────────
# DISEÑO
# ─────────────────────────────────────────

COLOR_FONDO    = (0.07, 0.07, 0.10, 1)
COLOR_TARJETA  = (0.13, 0.13, 0.18, 1)
COLOR_VERDE    = (0.20, 0.78, 0.56, 1)
COLOR_ROJO     = (0.93, 0.35, 0.35, 1)
COLOR_TEXTO    = (0.95, 0.95, 0.95, 1)
COLOR_GRIS     = (0.55, 0.55, 0.60, 1)
COLOR_BOTON    = (0.18, 0.18, 0.25, 1)
COLOR_AZUL     = (0.25, 0.55, 0.95, 1)
COLOR_AMARILLO = (0.95, 0.80, 0.25, 1)
COLOR_BORRAR   = (0.55, 0.12, 0.12, 1)
COLOR_EDITAR   = (0.20, 0.40, 0.70, 1)
RADIO          = [14]

COLORES_CATEGORIA = {
    "Comida":(0.95,0.65,0.20,1),"Servicios":(0.40,0.70,0.95,1),
    "Transporte":(0.55,0.45,0.95,1),"Salud":(0.95,0.40,0.40,1),
    "Educacion":(0.30,0.85,0.75,1),"Ropa":(0.95,0.45,0.75,1),
    "Entretenimiento":(0.95,0.80,0.25,1),"Sueldo":(0.20,0.78,0.56,1),
    "Negocio":(0.30,0.90,0.60,1),"Freelance":(0.25,0.75,0.50,1),
    "Arriendo":(0.20,0.65,0.45,1),"Regalo":(0.85,0.55,0.95,1),
    "Otro":(0.55,0.55,0.60,1),
}

def fondo(widget):
    with widget.canvas.before:
        Color(*COLOR_FONDO)
        widget._bg = Rectangle(pos=widget.pos, size=widget.size)
    widget.bind(pos=lambda i,v: setattr(i._bg,"pos",v))
    widget.bind(size=lambda i,v: setattr(i._bg,"size",v))

def tarjeta_redondeada(widget, color=None, radio=None):
    color = color or COLOR_TARJETA
    radio = radio or RADIO
    with widget.canvas.before:
        Color(*color)
        widget._rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=radio)
    widget.bind(pos=lambda i,v: setattr(i._rect,"pos",v))
    widget.bind(size=lambda i,v: setattr(i._rect,"size",v))

def hacer_label(texto, tamanio=15, color=None, bold=False, halign="left"):
    color = color or COLOR_TEXTO
    lbl = Label(text=texto, font_size=tamanio, color=color,
                bold=bold, halign=halign, valign="middle", size_hint_y=None)
    lbl.bind(texture_size=lambda i,v: setattr(i,"height",v[1]+8))
    lbl.bind(width=lambda i,v: setattr(i,"text_size",(v,None)))
    return lbl

def hacer_boton(texto, color_bg=None, on_press=None, altura=50, radio=14):
    btn = Button(text=texto, font_size=14, bold=True,
                 background_normal="", background_color=(0,0,0,0),
                 color=COLOR_TEXTO, size_hint_y=None, height=altura)
    color_bg = color_bg or COLOR_BOTON
    with btn.canvas.before:
        Color(*color_bg)
        btn._rect = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[radio])
    btn.bind(pos=lambda i,v: setattr(i._rect,"pos",v))
    btn.bind(size=lambda i,v: setattr(i._rect,"size",v))
    if on_press:
        btn.bind(on_press=on_press)
    return btn

def hacer_input(hint):
    contenedor = BoxLayout(size_hint_y=None, height=46, padding=[2,2])
    tarjeta_redondeada(contenedor, color=COLOR_BOTON, radio=[10])
    inp = TextInput(hint_text=hint, font_size=15,
                    background_normal="", background_color=(0,0,0,0),
                    foreground_color=COLOR_TEXTO,
                    hint_text_color=COLOR_GRIS,
                    cursor_color=COLOR_VERDE,
                    multiline=False, padding=[12,10])
    contenedor.add_widget(inp)
    contenedor.input = inp
    return contenedor

def hacer_spinner(valores, seleccion=""):
    sp = Spinner(text=seleccion or valores[0], values=valores,
                 font_size=13, background_normal="",
                 background_color=(0,0,0,0),
                 color=COLOR_TEXTO, size_hint_y=None, height=44)
    with sp.canvas.before:
        Color(*COLOR_BOTON)
        sp._rect = RoundedRectangle(pos=sp.pos, size=sp.size, radius=[10])
    sp.bind(pos=lambda i,v: setattr(i._rect,"pos",v))
    sp.bind(size=lambda i,v: setattr(i._rect,"size",v))
    return sp

def tarjeta_box(titulo, valor, color):
    caja = BoxLayout(orientation="vertical", padding=6)
    tarjeta_redondeada(caja, radio=[10])
    caja.add_widget(Label(text=titulo, font_size=10, color=COLOR_GRIS, size_hint_y=0.4))
    caja.add_widget(Label(text=valor,  font_size=14, bold=True, color=color, size_hint_y=0.6))
    return caja

def mostrar_popup(titulo, mensaje, color=None):
    color = color or COLOR_TEXTO
    contenido = BoxLayout(orientation="vertical", padding=16, spacing=10)
    tarjeta_redondeada(contenido)
    contenido.add_widget(hacer_label(mensaje, tamanio=14, color=color, halign="center"))
    btn = hacer_boton("Cerrar", color_bg=COLOR_BOTON)
    contenido.add_widget(btn)
    popup = Popup(title=titulo, content=contenido, size_hint=(0.85,0.38),
                  background_color=COLOR_TARJETA, title_color=COLOR_TEXTO, title_size=15)
    btn.bind(on_press=popup.dismiss)
    popup.open()

def confirmar_borrado(desc, monto, on_confirm):
    contenido = BoxLayout(orientation="vertical", padding=16, spacing=12)
    tarjeta_redondeada(contenido)
    contenido.add_widget(hacer_label(
        f"Seguro que quieres borrar?\n\n{desc}\n${monto:,.0f}",
        tamanio=14, color=COLOR_TEXTO, halign="center"))
    bots = BoxLayout(orientation="horizontal", size_hint_y=None, height=48, spacing=10)
    btn_si = hacer_boton("Si, borrar", color_bg=COLOR_BORRAR, altura=48)
    btn_no = hacer_boton("Cancelar",   color_bg=COLOR_BOTON,  altura=48)
    bots.add_widget(btn_si); bots.add_widget(btn_no)
    contenido.add_widget(bots)
    popup = Popup(title="Borrar movimiento", content=contenido, size_hint=(0.85,0.44),
                  background_color=COLOR_TARJETA, title_color=COLOR_ROJO, title_size=15)
    btn_si.bind(on_press=lambda x: [popup.dismiss(), on_confirm()])
    btn_no.bind(on_press=popup.dismiss)
    popup.open()

def popup_editar(row, on_guardar):
    idx, tipo, desc, cat, monto, fecha = row
    categorias = CATEGORIAS_INGRESO if tipo=="INGRESO" else CATEGORIAS_GASTO
    contenido = BoxLayout(orientation="vertical", padding=16, spacing=10)
    tarjeta_redondeada(contenido)
    contenido.add_widget(hacer_label("Editar movimiento", tamanio=16,
                                     bold=True, halign="center", color=COLOR_AZUL))
    contenido.add_widget(hacer_label("Descripcion:", tamanio=12, color=COLOR_GRIS))
    campo_desc = hacer_input("Descripcion")
    campo_desc.input.text = desc
    contenido.add_widget(campo_desc)
    contenido.add_widget(hacer_label("Categoria:", tamanio=12, color=COLOR_GRIS))
    sp_cat = hacer_spinner(categorias, cat if cat in categorias else categorias[0])
    contenido.add_widget(sp_cat)
    contenido.add_widget(hacer_label("Monto:", tamanio=12, color=COLOR_GRIS))
    campo_monto = hacer_input("Monto")
    campo_monto.input.text = str(monto)
    contenido.add_widget(campo_monto)
    bots = BoxLayout(orientation="horizontal", size_hint_y=None, height=48, spacing=10)
    btn_ok = hacer_boton("Guardar cambios", color_bg=COLOR_AZUL,  altura=48)
    btn_no = hacer_boton("Cancelar",        color_bg=COLOR_BOTON, altura=48)
    bots.add_widget(btn_ok); bots.add_widget(btn_no)
    contenido.add_widget(bots)
    popup = Popup(title="Editar", content=contenido, size_hint=(0.92,0.80),
                  background_color=COLOR_TARJETA, title_color=COLOR_AZUL, title_size=15)
    def guardar(inst):
        nuevo_desc = campo_desc.input.text.strip()
        nueva_cat  = sp_cat.text
        try:
            nuevo_monto = float(campo_monto.input.text.strip())
            if nuevo_monto <= 0: raise ValueError
        except ValueError:
            mostrar_popup("Error", "Monto invalido.", COLOR_ROJO); return
        if not nuevo_desc:
            mostrar_popup("Error", "Escribe una descripcion.", COLOR_ROJO); return
        popup.dismiss()
        on_guardar(idx, tipo, nuevo_desc, nueva_cat, nuevo_monto, fecha)
    btn_ok.bind(on_press=guardar)
    btn_no.bind(on_press=popup.dismiss)
    popup.open()

# ─────────────────────────────────────────
# PANTALLAS
# ─────────────────────────────────────────

class PantallaMenu(Screen):
    def on_enter(self):
        self.clear_widgets()
        self._construir()

    def _construir(self):
        raiz = BoxLayout(orientation="vertical", padding=24, spacing=14)
        fondo(raiz)
        raiz.add_widget(Label(size_hint_y=None, height=28))
        raiz.add_widget(hacer_label("Gastos Familiares", tamanio=24, bold=True, halign="center"))
        raiz.add_widget(hacer_label("Controla tus finanzas facilmente",
                                    tamanio=13, color=COLOR_GRIS, halign="center"))
        saldo = saldo_global()
        color_saldo = COLOR_VERDE if saldo >= 0 else COLOR_ROJO
        signo = "+" if saldo >= 0 else ""
        caja_saldo = BoxLayout(size_hint_y=None, height=62, padding=[0,6])
        tarjeta_redondeada(caja_saldo, color=(0.10,0.22,0.16,1), radio=[14])
        caja_saldo.add_widget(Label(
            text=f"Saldo disponible:  {signo}${saldo:,.0f}",
            font_size=18, bold=True, color=color_saldo,
            halign="center", valign="middle"))
        raiz.add_widget(caja_saldo)
        raiz.add_widget(Label(size_hint_y=None, height=6))
        raiz.add_widget(hacer_boton("+ Registrar Ingreso", color_bg=COLOR_VERDE,
                        on_press=lambda x: self.ir("ingreso")))
        raiz.add_widget(hacer_boton("- Registrar Gasto", color_bg=COLOR_ROJO,
                        on_press=lambda x: self.ir("gasto")))
        raiz.add_widget(hacer_boton("Ver Resumen",
                        on_press=lambda x: self.ir("resumen")))
        raiz.add_widget(hacer_boton("Resumen por Categoria", color_bg=COLOR_AZUL,
                        on_press=lambda x: self.ir("categorias")))
        raiz.add_widget(Label())
        self.add_widget(raiz)

    def ir(self, p):
        self.manager.current = p

class PantallaRegistro(Screen):
    def __init__(self, tipo="INGRESO", **kw):
        super().__init__(**kw)
        self.tipo = tipo
        color_acento = COLOR_VERDE if tipo=="INGRESO" else COLOR_ROJO
        categorias   = CATEGORIAS_INGRESO if tipo=="INGRESO" else CATEGORIAS_GASTO
        raiz = BoxLayout(orientation="vertical", padding=24, spacing=12)
        fondo(raiz)
        raiz.add_widget(Label(size_hint_y=None, height=16))
        raiz.add_widget(hacer_label(f"Registrar {tipo.capitalize()}",
                                    tamanio=20, bold=True, color=color_acento, halign="center"))
        raiz.add_widget(Label(size_hint_y=None, height=8))
        raiz.add_widget(hacer_label("Descripcion", tamanio=12, color=COLOR_GRIS))
        self.campo_desc = hacer_input("Ej: Sueldo quincenal, Mercado...")
        raiz.add_widget(self.campo_desc)
        raiz.add_widget(hacer_label("Categoria", tamanio=12, color=COLOR_GRIS))
        self.spinner_cat = hacer_spinner(categorias)
        raiz.add_widget(self.spinner_cat)
        raiz.add_widget(hacer_label("Monto", tamanio=12, color=COLOR_GRIS))
        self.campo_monto = hacer_input("Ej: 8000")
        raiz.add_widget(self.campo_monto)
        raiz.add_widget(Label(size_hint_y=None, height=8))
        raiz.add_widget(hacer_boton(f"Guardar {tipo.capitalize()}",
                        color_bg=color_acento, on_press=self.guardar))
        raiz.add_widget(hacer_boton("Volver", on_press=lambda x: self.volver()))
        raiz.add_widget(Label())
        self.add_widget(raiz)

    def guardar(self, *args):
        desc = self.campo_desc.input.text.strip()
        monto_txt = self.campo_monto.input.text.strip()
        cat = self.spinner_cat.text
        if not desc:
            mostrar_popup("Error","Escribe una descripcion.",COLOR_ROJO); return
        if not monto_txt:
            mostrar_popup("Error","Escribe un monto.",COLOR_ROJO); return
        try:
            monto = float(monto_txt)
            if monto <= 0: raise ValueError
        except ValueError:
            mostrar_popup("Error","El monto debe ser mayor a 0.",COLOR_ROJO); return
        guardar_movimiento(self.tipo, desc, cat, monto)
        self.campo_desc.input.text = ""; self.campo_monto.input.text = ""
        mostrar_popup("Guardado", f"{self.tipo.capitalize()} de ${monto:.2f}\nCategoria: {cat}", COLOR_VERDE)

    def volver(self):
        self.manager.current = "menu"

class PantallaResumen(Screen):
    def on_enter(self):
        self.clear_widgets(); self.construir()

    def construir(self, filtro_mes="Todos"):
        movs, ing_mes, gas_mes, saldo_ant, ing_total, gas_total = cargar_movimientos(filtro_mes)
        saldo_mes   = round(ing_mes - gas_mes, 2)
        saldo_acum  = round(saldo_ant + saldo_mes, 2)
        saldo_total = round(ing_total - gas_total, 2)
        es_filtrado = filtro_mes != "Todos"
        raiz = BoxLayout(orientation="vertical", padding=18, spacing=8)
        fondo(raiz)
        raiz.add_widget(Label(size_hint_y=None, height=8))
        raiz.add_widget(hacer_label("Resumen Financiero", tamanio=20, bold=True, halign="center"))
        raiz.add_widget(hacer_label("Filtrar por mes:", tamanio=12, color=COLOR_GRIS))
        spinner = hacer_spinner(MESES, filtro_mes)
        spinner.bind(text=lambda i,v: self.cambiar_mes(v))
        raiz.add_widget(spinner)
        raiz.add_widget(Label(size_hint_y=None, height=4))
        if es_filtrado:
            bloque_ant = BoxLayout(orientation="horizontal", size_hint_y=None, height=44, padding=[12,6])
            tarjeta_redondeada(bloque_ant)
            c_ant = COLOR_VERDE if saldo_ant >= 0 else COLOR_ROJO
            bloque_ant.add_widget(Label(text="Saldo arrastrado:", font_size=12, color=COLOR_GRIS,
                                        halign="left", text_size=(None,None), size_hint_x=0.6))
            bloque_ant.add_widget(Label(text=f"${saldo_ant:,.0f}", font_size=14,
                                        bold=True, color=c_ant, size_hint_x=0.4))
            raiz.add_widget(bloque_ant)
            raiz.add_widget(hacer_label(f"Movimientos de {filtro_mes[3:]}:", tamanio=12, color=COLOR_GRIS))
            grilla = GridLayout(cols=3, size_hint_y=None, height=72, spacing=6)
            grilla.add_widget(tarjeta_box("Ingresos",  f"${ing_mes:,.0f}", COLOR_VERDE))
            grilla.add_widget(tarjeta_box("Gastos",    f"${gas_mes:,.0f}", COLOR_ROJO))
            c_mes = COLOR_VERDE if saldo_mes >= 0 else COLOR_ROJO
            grilla.add_widget(tarjeta_box("Saldo mes", f"${saldo_mes:,.0f}", c_mes))
            raiz.add_widget(grilla)
            bloque_acum = BoxLayout(orientation="horizontal", size_hint_y=None, height=50, padding=[12,6])
            tarjeta_redondeada(bloque_acum, color=(0.10,0.10,0.16,1))
            c_acum = COLOR_VERDE if saldo_acum >= 0 else COLOR_ROJO
            bloque_acum.add_widget(Label(text="Saldo acumulado hasta este mes:",
                                         font_size=12, color=COLOR_TEXTO,
                                         halign="left", text_size=(None,None), size_hint_x=0.6))
            bloque_acum.add_widget(Label(text=f"${saldo_acum:,.0f}", font_size=17,
                                         bold=True, color=c_acum, size_hint_x=0.4))
            raiz.add_widget(bloque_acum)
        else:
            grilla = GridLayout(cols=3, size_hint_y=None, height=76, spacing=6)
            grilla.add_widget(tarjeta_box("Ingresos",    f"${ing_total:,.0f}", COLOR_VERDE))
            grilla.add_widget(tarjeta_box("Gastos",      f"${gas_total:,.0f}", COLOR_ROJO))
            c = COLOR_VERDE if saldo_total >= 0 else COLOR_ROJO
            grilla.add_widget(tarjeta_box("Saldo total", f"${saldo_total:,.0f}", c))
            raiz.add_widget(grilla)
        saldo_ref = saldo_acum if es_filtrado else saldo_total
        if saldo_ref > 0:    estado, c_est = "Finanzas saludables",         COLOR_VERDE
        elif saldo_ref == 0: estado, c_est = "Justo a mano",                COLOR_AMARILLO
        else:                estado, c_est = "Gastos mayores que ingresos", COLOR_ROJO
        raiz.add_widget(hacer_label(estado, tamanio=13, color=c_est, halign="center"))
        raiz.add_widget(hacer_label(f"Movimientos: {len(movs)}", tamanio=12, color=COLOR_GRIS, halign="center"))
        raiz.add_widget(hacer_label("Editar / Borrar con los botones:", tamanio=11, color=COLOR_GRIS))
        scroll = ScrollView(size_hint=(1,1))
        lista  = BoxLayout(orientation="vertical", size_hint_y=None, spacing=6)
        lista.bind(minimum_height=lista.setter("height"))
        for row in reversed(movs[-50:]):
            lista.add_widget(self._fila(row, filtro_mes))
        if not movs:
            lista.add_widget(hacer_label("No hay movimientos.", color=COLOR_GRIS, halign="center"))
        scroll.add_widget(lista)
        raiz.add_widget(scroll)
        raiz.add_widget(hacer_boton("Volver al menu",
                        on_press=lambda x: setattr(self.manager,"current","menu"), altura=44))
        self.add_widget(raiz)

    def cambiar_mes(self, mes):
        self.clear_widgets(); self.construir(mes)

    def _fila(self, row, filtro_mes):
        idx, tipo, desc, cat, monto, fecha = row
        fila = BoxLayout(orientation="horizontal", size_hint_y=None, height=58, spacing=5, padding=[8,5])
        tarjeta_redondeada(fila)
        color_tipo = COLOR_VERDE if tipo=="INGRESO" else COLOR_ROJO
        simbolo    = "+" if tipo=="INGRESO" else "-"
        color_cat  = COLORES_CATEGORIA.get(cat, COLOR_GRIS)
        col = BoxLayout(orientation="vertical", size_hint_x=0.48)
        col.add_widget(Label(text=desc, font_size=12, color=COLOR_TEXTO, halign="left", text_size=(None,None)))
        col.add_widget(Label(text=cat,  font_size=10, color=color_cat,   halign="left", text_size=(None,None)))
        lbl_monto = Label(text=f"${monto:,.0f}", font_size=13, bold=True, color=color_tipo, size_hint_x=0.24)
        btn_editar = Button(text="Edit", font_size=12, bold=True,
                            background_normal="", background_color=(0,0,0,0),
                            color=COLOR_TEXTO, size_hint_x=0.15, size_hint_y=None, height=36)
        with btn_editar.canvas.before:
            Color(*COLOR_EDITAR)
            btn_editar._rect = RoundedRectangle(pos=btn_editar.pos, size=btn_editar.size, radius=[8])
        btn_editar.bind(pos=lambda i,v: setattr(i._rect,"pos",v))
        btn_editar.bind(size=lambda i,v: setattr(i._rect,"size",v))
        btn_borrar = Button(text="X", font_size=13, bold=True,
                            background_normal="", background_color=(0,0,0,0),
                            color=COLOR_TEXTO, size_hint_x=0.13, size_hint_y=None, height=36)
        with btn_borrar.canvas.before:
            Color(*COLOR_BORRAR)
            btn_borrar._rect = RoundedRectangle(pos=btn_borrar.pos, size=btn_borrar.size, radius=[8])
        btn_borrar.bind(pos=lambda i,v: setattr(i._rect,"pos",v))
        btn_borrar.bind(size=lambda i,v: setattr(i._rect,"size",v))
        def on_editar(inst, _row=row, _mes=filtro_mes):
            popup_editar(_row, lambda i,t,d,c,m,f: self._ejecutar_edicion(i,t,d,c,m,f,_mes))
        def on_borrar(inst, _idx=idx, _desc=desc, _monto=monto, _mes=filtro_mes):
            confirmar_borrado(_desc, _monto, lambda: self._ejecutar_borrado(_idx, _mes))
        btn_editar.bind(on_press=on_editar)
        btn_borrar.bind(on_press=on_borrar)
        fila.add_widget(Label(text=simbolo, font_size=16, color=color_tipo, size_hint_x=0.07))
        fila.add_widget(col)
        fila.add_widget(lbl_monto)
        fila.add_widget(btn_editar)
        fila.add_widget(btn_borrar)
        return fila

    def _ejecutar_borrado(self, idx, filtro_mes):
        borrar_movimiento(idx); self.clear_widgets(); self.construir(filtro_mes)

    def _ejecutar_edicion(self, idx, tipo, desc, cat, monto, fecha, filtro_mes):
        editar_movimiento(idx, tipo, desc, cat, monto, fecha)
        self.clear_widgets(); self.construir(filtro_mes)

class PantallaCategorias(Screen):
    def on_enter(self):
        self.clear_widgets(); self.construir()

    def construir(self, filtro_mes="Todos"):
        totales, movimientos = cargar_categorias(filtro_mes)
        raiz = BoxLayout(orientation="vertical", padding=20, spacing=8)
        fondo(raiz)
        raiz.add_widget(Label(size_hint_y=None, height=10))
        raiz.add_widget(hacer_label("Resumen por Categoria", tamanio=20, bold=True, halign="center"))
        raiz.add_widget(hacer_label("Filtrar por mes:", tamanio=12, color=COLOR_GRIS))
        spinner = hacer_spinner(MESES, filtro_mes)
        spinner.bind(text=lambda i,v: self.cambiar_mes(v))
        raiz.add_widget(spinner)
        raiz.add_widget(Label(size_hint_y=None, height=6))
        scroll = ScrollView(size_hint=(1,1))
        lista  = BoxLayout(orientation="vertical", size_hint_y=None, spacing=6)
        lista.bind(minimum_height=lista.setter("height"))
        lista.add_widget(hacer_label("INGRESOS", tamanio=13, color=COLOR_VERDE, bold=True))
        hay = False
        for clave, total in sorted(totales.items()):
            if clave.startswith("INGRESO|"):
                lista.add_widget(self._barra(clave.split("|")[1], total, COLOR_VERDE)); hay=True
        if not hay: lista.add_widget(hacer_label("Sin ingresos.", color=COLOR_GRIS))
        lista.add_widget(Label(size_hint_y=None, height=10))
        lista.add_widget(hacer_label("GASTOS", tamanio=13, color=COLOR_ROJO, bold=True))
        hay = False
        for clave, total in sorted(totales.items()):
            if clave.startswith("GASTO|"):
                lista.add_widget(self._barra(clave.split("|")[1], total, COLOR_ROJO)); hay=True
        if not hay: lista.add_widget(hacer_label("Sin gastos.", color=COLOR_GRIS))
        if not movimientos:
            lista.add_widget(hacer_label("No hay datos.", color=COLOR_GRIS, halign="center"))
        scroll.add_widget(lista)
        raiz.add_widget(scroll)
        raiz.add_widget(hacer_boton("Volver al menu",
                        on_press=lambda x: setattr(self.manager,"current","menu"), altura=44))
        self.add_widget(raiz)

    def cambiar_mes(self, mes):
        self.clear_widgets(); self.construir(mes)

    def _barra(self, categoria, total, color):
        fila = BoxLayout(orientation="horizontal", size_hint_y=None, height=44, spacing=8, padding=[12,4])
        tarjeta_redondeada(fila)
        color_cat = COLORES_CATEGORIA.get(categoria, COLOR_GRIS)
        fila.add_widget(Label(text=categoria, font_size=13, color=color_cat,
                               halign="left", text_size=(None,None), size_hint_x=0.55))
        fila.add_widget(Label(text=f"${total:,.0f}", font_size=14,
                               bold=True, color=color, size_hint_x=0.45))
        return fila

# ─────────────────────────────────────────
# APP PRINCIPAL
# ─────────────────────────────────────────

class GastosFamiliaApp(App):
    def build(self):
        inicializar_csv()
        sm = ScreenManager()
        sm.add_widget(PantallaMenu(name="menu"))
        sm.add_widget(PantallaRegistro(tipo="INGRESO", name="ingreso"))
        sm.add_widget(PantallaRegistro(tipo="GASTO",   name="gasto"))
        sm.add_widget(PantallaResumen(name="resumen"))
        sm.add_widget(PantallaCategorias(name="categorias"))
        return sm

if __name__ == "__main__":
    GastosFamiliaApp().run()
