import tkinter as tk
from tkinter import messagebox
import json
import matplotlib.pyplot as plt  # type: ignore
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore
from tkinter import ttk
import pandas as pd  # type: ignore
import os

from models.portfolio import Portfolio
from services.market_data import obtener_precios_actuales
from models.asset import Asset

CARTERA_ARCHIVO = "data/cartera.json"
DIVIDENDOS_ARCHIVO = "data/dividendos.json"
PATRIMONIO_ARCHIVO = "data/patrimonio.json"

portfolio = Portfolio(CARTERA_ARCHIVO)

ventana_saldos_ref = None  # Referencia global para poder actualizar la ventana si está abierta

def ventana_agregar_activos():
    ventana = tk.Toplevel()
    ventana.title("Agregar Nuevos Activos")
    ventana.geometry("600x400")

    tk.Label(ventana, text="Símbolo:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_simbolo = tk.Entry(ventana, width=15)
    entry_simbolo.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(ventana, text="Título:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
    entry_titulo = tk.Entry(ventana, width=20)
    entry_titulo.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(ventana, text="Cantidad:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_cantidad = tk.Entry(ventana, width=15)
    entry_cantidad.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(ventana, text="Precio manual:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
    entry_precio_manual = tk.Entry(ventana, width=15)
    entry_precio_manual.grid(row=1, column=3, padx=5, pady=5)

    tk.Label(ventana, text="Tipo:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    tipo_activo_var = tk.StringVar()
    tipo_activo_combobox = tk.OptionMenu(ventana, tipo_activo_var, 'ACC', 'ETF', 'PP', 'FON')
    tipo_activo_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    var_dividendos = tk.BooleanVar()
    tk.Checkbutton(ventana, text="Dividendos", variable=var_dividendos).grid(row=2, column=2, padx=5, pady=5)

    tk.Label(ventana, text="Broker:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
    broker_var = tk.StringVar()
    broker_combobox = tk.OptionMenu(ventana, broker_var, 'ocean', 'degiro', 'cxbank', 'bbva', 'sant')
    broker_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="w")

    tk.Label(ventana, text="Comisión:").grid(row=3, column=2, padx=5, pady=5, sticky="e")
    entry_comision = tk.Entry(ventana, width=15)
    entry_comision.insert(0, "0.0")
    entry_comision.grid(row=3, column=3, padx=5, pady=5)

    tk.Label(ventana, text="Precio final:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
    var_precio_final = tk.StringVar(value="0.00")
    entry_precio_final = tk.Entry(ventana, textvariable=var_precio_final, width=15, state="readonly")
    entry_precio_final.grid(row=4, column=1, padx=5, pady=5)

    def actualizar_precio_final(*args):
        try:
            cant = float(entry_cantidad.get() or 0)
            prec = float(entry_precio_manual.get() or 0)
            comis = float(entry_comision.get() or 0)
            pf = (cant * prec) + comis
            var_precio_final.set(f"{pf:.2f}")
        except ValueError:
            pass

    entry_cantidad.bind('<KeyRelease>', actualizar_precio_final)
    entry_precio_manual.bind('<KeyRelease>', actualizar_precio_final)
    entry_comision.bind('<KeyRelease>', actualizar_precio_final)

    def agregar_elemento():
        simbolo = entry_simbolo.get().strip()
        titulo = entry_titulo.get().strip()
        cantidad = entry_cantidad.get().strip()
        precio_manual = entry_precio_manual.get().strip()

        if not simbolo or not titulo or not cantidad.isdigit():
            messagebox.showerror("Error", "Campos obligatorios incompletos o inválidos.")
            return

        cantidad = int(cantidad)

        try:
            comision = float(entry_comision.get() or 0.0)
        except ValueError:
            messagebox.showerror("Error", "La comisión debe ser un número válido.")
            return

        precios_actuales = obtener_precios_actuales([simbolo])
        precio_actual = precios_actuales.get(simbolo, 0.0)

        if precio_actual == 0.0:
            if not precio_manual:
                messagebox.showerror("Error", "El precio no se encontró y no se ingresó manualmente.")
                return
            try:
                precio_actual = float(precio_manual)
            except ValueError:
                messagebox.showerror("Error", "El precio ingresado manualmente no es válido.")
                return

        precio_final = (cantidad * precio_actual) + comision
        var_precio_final.set(f"{precio_final:.2f}")

        asset = Asset(
            simbolo,
            titulo,
            cantidad,
            precio_actual,
            precio_final,
            'Sí' if var_dividendos.get() else 'No',
            tipo_activo_var.get(),
            broker_var.get()
        )
        portfolio.add_asset(asset)
        messagebox.showinfo("Éxito", "Elemento añadido a la cartera.")
        entry_simbolo.delete(0, tk.END)
        entry_titulo.delete(0, tk.END)
        entry_cantidad.delete(0, tk.END)
        entry_precio_manual.delete(0, tk.END)
        entry_comision.delete(0, tk.END)
        entry_comision.insert(0, "0.0")
        var_precio_final.set("0.00")
        var_dividendos.set(False)
        tipo_activo_var.set('')
        broker_var.set('')

    boton_agregar = tk.Button(ventana, text="AGREGAR ACTIVO", command=agregar_elemento,
                             bg="green", fg="black", font=("Arial", 10, "bold"))
    boton_agregar.grid(row=5, column=1, columnspan=2, padx=10, pady=20, sticky="ew")

def ventana_ver_cartera():
    ventana = tk.Toplevel()
    ventana.title("Ver Cartera")
    ventana.geometry("1400x800")

    cartera = portfolio.get_all_assets()

    if not cartera:
        tk.Label(ventana, text="No hay elementos en la cartera.", font=("Arial", 14)).pack(pady=50)
        return

    cartera_list_of_dicts = [asset.to_dict() for asset in cartera]
    total_general = sum(item['importe_total'] for item in cartera_list_of_dicts)
    totales_tipo = {tipo: sum(item['importe_total'] for item in cartera_list_of_dicts if item.get('tipo_activo') == tipo) for tipo in ['ACC', 'ETF', 'PP', 'FON']}
    totales_broker = {broker: sum(item['importe_total'] for item in cartera_list_of_dicts if item.get('broker') == broker) for broker in ['sant', 'cxbank', 'bbva', 'degiro', 'ocean']}
    total_acciones = sum(item['cantidad'] for item in cartera_list_of_dicts)
    totales_tipo_cant = {tipo: sum(item['cantidad'] for item in cartera_list_of_dicts if item.get('tipo_activo') == tipo) for tipo in ['ACC', 'ETF', 'PP', 'FON']}
    totales_broker_cant = {broker: sum(item['cantidad'] for item in cartera_list_of_dicts if item.get('broker') == broker) for broker in ['sant', 'cxbank', 'bbva', 'degiro', 'ocean']}

    columnas = [
        'símbolo',
        'título',
        'cantidad',
        'precio_actual',
        'importe_total',
        '% Activo',
        'tipo_activo',
        'broker'
    ]
    anchuras = {
        'símbolo': 12,
        'título': 40,
        'cantidad': 10,
        'precio_actual': 12,
        'importe_total': 15,
        '% Activo': 8,
        'tipo_activo': 12,
        'broker': 12
    }

    cartera_df = pd.DataFrame(cartera_list_of_dicts)
    orden_tipos = {'ACC': 0, 'ETF': 1, 'PP': 2, 'FON': 3}
    cartera_df['orden_tipo'] = cartera_df['tipo_activo'].map(orden_tipos)
    cartera_df = cartera_df.sort_values(['orden_tipo', 'símbolo']).drop('orden_tipo', axis=1)
    total_general_calculado = cartera_df['importe_total'].sum()

    columnas_map = {
        'símbolo': 'SIMBOLO',
        'título': 'TITULO',
        'cantidad': 'CANTIDAD',
        'precio_actual': 'PRECIO',
        'importe_total': 'IMPORTE',
        '% Activo': '%',
        'tipo_activo': 'TIPO',
        'broker': 'BROKER'
    }

    frame_principal = tk.Frame(ventana)
    frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    frame_cabecera_contenedor = tk.Frame(frame_principal)
    frame_cabecera_contenedor.pack(side=tk.TOP, fill=tk.X)
    
    frame_cabecera = tk.Frame(frame_cabecera_contenedor)
    frame_cabecera.pack(side=tk.LEFT)

    frame_scroll = tk.Frame(frame_principal)
    frame_scroll.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(frame_scroll)
    scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
    frame_tabla = tk.Frame(canvas)

    canvas.create_window((0, 0), window=frame_tabla, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for i, columna in enumerate(columnas):
        anchor = "w" if columna == "título" else "center"
        tk.Label(frame_cabecera, text=columnas_map[columna], borderwidth=1, relief="solid", width=anchuras.get(columna, 12),
                bg="yellow", fg="blue", font=("Arial", 11, "bold"), anchor=anchor).grid(row=0, column=i, sticky="ew")

    tk.Label(frame_cabecera, text="MODIFICAR", borderwidth=1, relief="solid", width=18,
            bg="yellow", fg="blue", font=("Arial", 11, "bold")).grid(row=0, column=len(columnas), columnspan=2, sticky="ew")

    def editar_elemento(simbolo):
        elemento = portfolio.get_asset_by_symbol(simbolo)
        if not elemento:
            messagebox.showerror("Error", "No se encontró el elemento a editar.")
            return

        ventana_edicion = tk.Toplevel(ventana)
        ventana_edicion.title("Editar elemento")

        tk.Label(ventana_edicion, text="Cantidad:").grid(row=0, column=0, padx=10, pady=5)
        entry_cantidad = tk.Entry(ventana_edicion)
        entry_cantidad.insert(0, elemento.cantidad)
        entry_cantidad.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(ventana_edicion, text="Precio actual:").grid(row=1, column=0, padx=10, pady=5)
        entry_precio = tk.Entry(ventana_edicion)
        entry_precio.insert(0, elemento.precio_actual)
        entry_precio.grid(row=1, column=1, padx=10, pady=5)

        var_dividendos = tk.BooleanVar(value=elemento.dividendos == 'Sí')
        tk.Checkbutton(ventana_edicion, text="Tiene dividendos", variable=var_dividendos).grid(row=2, columnspan=2, pady=5)

        tk.Label(ventana_edicion, text="Tipo de activo:").grid(row=3, column=0, padx=10, pady=5)
        tipo_var = tk.StringVar(value=elemento.tipo_activo)
        tk.OptionMenu(ventana_edicion, tipo_var, 'ACC', 'ETF', 'PP', 'FON').grid(row=3, column=1, padx=10, pady=5)

        tk.Label(ventana_edicion, text="Broker:").grid(row=4, column=0, padx=10, pady=5)
        broker_var = tk.StringVar(value=elemento.broker)
        tk.OptionMenu(ventana_edicion, broker_var, 'ocean', 'degiro', 'cxbank', 'bbva', 'sant').grid(row=4, column=1, padx=10, pady=5)

        def guardar_edicion():
            if not entry_cantidad.get().isdigit():
                messagebox.showerror("Error", "La cantidad debe ser un número entero válido.")
                return
            try:
                nuevo_precio = float(entry_precio.get())
            except ValueError:
                messagebox.showerror("Error", "El precio debe ser un número válido.")
                return

            elemento.cantidad = int(entry_cantidad.get())
            elemento.precio_actual = nuevo_precio
            elemento.dividendos = 'Sí' if var_dividendos.get() else 'No'
            elemento.tipo_activo = tipo_var.get()
            elemento.broker = broker_var.get()
            elemento.importe_total = elemento.cantidad * elemento.precio_actual

            portfolio.update_asset(simbolo, elemento)
            messagebox.showinfo("Éxito", "Elemento editado correctamente.")
            ventana_edicion.destroy()
            ventana.destroy()
            ventana_ver_cartera()

        tk.Button(ventana_edicion, text="Guardar", command=guardar_edicion).grid(row=5, columnspan=2, pady=10)

    def eliminar_elemento(simbolo):
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este elemento?"):
            portfolio.delete_asset(simbolo)
            messagebox.showinfo("Éxito", "Elemento eliminado.")
            ventana.destroy()
            ventana_ver_cartera()

    for row_num, (index, row) in enumerate(cartera_df.iterrows()):
        tipo_activo = row.get('tipo_activo', '')
        bg_color = {"PP": "#ADD8E6", "FON": "#90EE90", "ETF": "#FFFFE0", "ACC": "#FFDAB9"}.get(tipo_activo, "white")

        for i, columna in enumerate(columnas):
            if columna == '% Activo':
                porcentaje = (row['importe_total'] / total_general_calculado * 100) if total_general_calculado > 0 else 0
                valor = f"{porcentaje:.2f}%"
            else:
                valor = f"{row.get(columna, ''):.2f}" if columna == 'importe_total' else str(row.get(columna, ''))
            anchor = "w" if columna == "título" else "center"
            tk.Label(frame_tabla, text=valor, borderwidth=1, relief="solid", width=anchuras.get(columna, 12),
                    anchor=anchor, bg=bg_color, font=("Arial", 11)).grid(row=row_num, column=i, sticky="ew")

        simbolo = row.get('símbolo', '')
        tk.Button(frame_tabla, text="Editar", width=8, command=lambda s=simbolo: editar_elemento(s)).grid(row=row_num, column=len(columnas), sticky="ew")
        tk.Button(frame_tabla, text="Eliminar", width=8, command=lambda s=simbolo: eliminar_elemento(s)).grid(row=row_num, column=len(columnas) + 1, sticky="ew")

    frame_tabla.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # --- Frame inferior para gráficos y resúmenes ---
    frame_inferior = tk.Frame(ventana)
    frame_inferior.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

    # --- Gráficos (lado izquierdo) ---
    frame_graficos = tk.Frame(frame_inferior)
    frame_graficos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tipos_graf = ['ACC', 'ETF', 'PP', 'FON']
    totales_tipo_graf = [totales_tipo.get(tipo, 0) for tipo in tipos_graf]
    colores = ['#FFDAB9', '#FFFFE0', '#ADD8E6', '#90EE90']

    # Gráfico de barras
    fig_bar, ax_bar = plt.subplots(figsize=(4, 3))
    bars = ax_bar.bar(tipos_graf, totales_tipo_graf, color=colores)
    ax_bar.set_ylabel('Importe (€)')
    ax_bar.set_title('Importe por Tipo de Activo', fontsize=10)
    ax_bar.bar_label(bars, fmt='%.0f€', fontsize=8)
    fig_bar.tight_layout()

    canvas_bar = FigureCanvasTkAgg(fig_bar, master=frame_graficos)
    canvas_bar.draw()
    canvas_bar.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    # Gráfico circular (Pie)
    labels_graf = [tipo for tipo, total in totales_tipo.items() if total > 0]
    valores_graf = [total for total in totales_tipo.values() if total > 0]

    if valores_graf:
        fig_pie, ax_pie = plt.subplots(figsize=(4, 3))
        ax_pie.pie(valores_graf, labels=labels_graf, autopct='%1.1f%%', startangle=140, colors=colores, textprops={'fontsize': 8})
        ax_pie.axis('equal')
        ax_pie.set_title('Distribución por Tipo de Activo', fontsize=10, fontweight='bold')
        fig_pie.tight_layout()

        canvas_pie = FigureCanvasTkAgg(fig_pie, master=frame_graficos)
        canvas_pie.draw()
        canvas_pie.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    # --- Resúmenes (lado derecho) ---
    frame_resumenes = tk.Frame(frame_inferior)
    frame_resumenes.pack(side=tk.RIGHT, fill=tk.Y, padx=20)

    frame_sumario_importe = tk.Frame(frame_resumenes)
    frame_sumario_importe.pack(fill=tk.X, pady=5)
    tk.Label(frame_sumario_importe, text=f"IMPORTE TOTAL: {total_general:.2f}€", font=("Arial", 16, "bold"), fg="red").pack()
    frame_columnas = tk.Frame(frame_sumario_importe)
    frame_columnas.pack()
    frame_tipos = tk.LabelFrame(frame_columnas, text="Totales por Tipo", font=("Arial", 10, "bold"))
    frame_tipos.pack(side=tk.LEFT, padx=5, pady=2, anchor="n")
    for tipo, total in totales_tipo.items():
        if total > 0:
            tk.Label(frame_tipos, text=f"{tipo}: {total:.2f}€", font=("Arial", 10)).pack(anchor="w", padx=10, pady=1)
    frame_brokers = tk.LabelFrame(frame_columnas, text="Totales por Broker", font=("Arial", 10, "bold"))
    frame_brokers.pack(side=tk.LEFT, padx=5, pady=2, anchor="n")
    for broker, total in totales_broker.items():
        if total > 0:
            tk.Label(frame_brokers, text=f"{broker}: {total:.2f}€", font=("Arial", 10)).pack(anchor="w", padx=10, pady=1)

    frame_sumario_cantidad = tk.Frame(frame_resumenes)
    frame_sumario_cantidad.pack(fill=tk.X, pady=5)
    tk.Label(frame_sumario_cantidad, text=f"TOTAL ACCIONES: {total_acciones}", font=("Arial", 16, "bold"), fg="blue").pack()
    frame_columnas_cant = tk.Frame(frame_sumario_cantidad)
    frame_columnas_cant.pack()
    frame_tipos_cant = tk.LabelFrame(frame_columnas_cant, text="Acciones por Tipo", font=("Arial", 10, "bold"))
    frame_tipos_cant.pack(side=tk.LEFT, padx=5, pady=2, anchor="n")
    for tipo, total in totales_tipo_cant.items():
        if total > 0:
            tk.Label(frame_tipos_cant, text=f"{tipo}: {total}", font=("Arial", 10)).pack(anchor="w", padx=10, pady=1)
    frame_brokers_cant = tk.LabelFrame(frame_columnas_cant, text="Acciones por Broker", font=("Arial", 10, "bold"))
    frame_brokers_cant.pack(side=tk.LEFT, padx=5, pady=2, anchor="n")
    for broker, total in totales_broker_cant.items():
        if total > 0:
            tk.Label(frame_brokers_cant, text=f"{broker}: {total}", font=("Arial", 10)).pack(anchor="w", padx=10, pady=1)

ANOS_DIVIDENDOS = [2022, 2023, 2024, 2025, 2026]

def cargar_dividendos():
    try:
        with open(DIVIDENDOS_ARCHIVO, "r") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return {}

def guardar_dividendos(dividendos):
    with open(DIVIDENDOS_ARCHIVO, "w") as archivo:
        json.dump(dividendos, archivo, indent=4)

def ventana_dividendos():
    ventana = tk.Toplevel()
    ventana.title("Dividendos")
    ventana.geometry("900x900")

    cartera = portfolio.get_all_assets()
    activos_con_dividendos = [asset for asset in cartera if asset.dividendos == 'Sí']

    if not activos_con_dividendos:
        tk.Label(ventana, text="No hay activos con dividendos.", font=("Arial", 14)).pack(pady=50)
        return

    dividendos_data = cargar_dividendos()

    notebook = ttk.Notebook(ventana)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def on_tab_change(event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        if tab_text == "Resumen":
            ventana.geometry("900x900")
        else:
            ventana.geometry("1400x900")

    notebook.bind("<<NotebookTabChanged>>", on_tab_change)

    frame_resumen_tab = ttk.Frame(notebook)
    notebook.add(frame_resumen_tab, text="Resumen")

    frame_resumen = tk.LabelFrame(frame_resumen_tab, text="Resumen de Dividendos Totales", font=("Arial", 14, "bold"), padx=10, pady=10)
    frame_resumen.pack(fill=tk.X, padx=10, pady=10, anchor="n")
    anos = ANOS_DIVIDENDOS

    totales_por_activo_ano = {activo.simbolo: {ano: 0 for ano in anos} for activo in activos_con_dividendos}
    totales_por_ano = {ano: 0 for ano in anos}

    for ano_str, data_ano in dividendos_data.items():
        try:
            ano = int(ano_str)
            if ano in anos:
                for simbolo, valores in data_ano.items():
                    if simbolo in totales_por_activo_ano:
                        total_activo_ano = sum(float(v or 0) for v in valores)
                        totales_por_activo_ano[simbolo][ano] = total_activo_ano
                        totales_por_ano[ano] += total_activo_ano
        except (ValueError, TypeError):
            continue

    totales_por_activo = {simbolo: sum(totales_anuales.values()) for simbolo, totales_anuales in totales_por_activo_ano.items()}
    gran_total = sum(totales_por_ano.values())

    headers = ["Activo"] + [str(ano) for ano in anos] + ["Total Activo", "% Total"]
    header_font = ("Arial", 11, "bold")
    for i, header in enumerate(headers):
        tk.Label(frame_resumen, text=header, font=header_font, bg="lightblue", relief="solid", borderwidth=1, padx=5, pady=2).grid(row=0, column=i, sticky="ew")

    row_idx = 1
    for activo in sorted(activos_con_dividendos, key=lambda x: x.simbolo):
        simbolo = activo.simbolo
        tk.Label(frame_resumen, text=simbolo, anchor="w", relief="solid", borderwidth=1, padx=5).grid(row=row_idx, column=0, sticky="ew")

        for i, ano in enumerate(anos):
            valor = totales_por_activo_ano.get(simbolo, {}).get(ano, 0)
            tk.Label(frame_resumen, text=f"{valor:.2f}€", anchor="e", relief="solid", borderwidth=1, padx=5).grid(row=row_idx, column=i+1, sticky="ew")

        total_activo = totales_por_activo.get(simbolo, 0)
        tk.Label(frame_resumen, text=f"{total_activo:.2f}€", anchor="e", relief="solid", borderwidth=1, bg="lightgray", font=("Arial", 10, "bold"), padx=5).grid(row=row_idx, column=len(anos)+1, sticky="ew")

        porcentaje = (total_activo / gran_total * 100) if gran_total > 0 else 0
        tk.Label(frame_resumen, text=f"{porcentaje:.2f}%", anchor="e", relief="solid", borderwidth=1, bg="lightgray", font=("Arial", 10, "bold"), padx=5).grid(row=row_idx, column=len(anos)+2, sticky="ew")

        row_idx += 1

    tk.Label(frame_resumen, text="TOTAL AÑO", font=header_font, bg="orange", relief="solid", borderwidth=1, padx=5).grid(row=row_idx, column=0, sticky="ew")
    for i, ano in enumerate(anos):
        tk.Label(frame_resumen, text=f"{totales_por_ano[ano]:.2f}€", font=header_font, anchor="e", bg="orange", relief="solid", borderwidth=1, padx=5).grid(row=row_idx, column=i+1, sticky="ew")

    tk.Label(frame_resumen, text=f"{gran_total:.2f}€", font=header_font, anchor="e", bg="red", fg="white", relief="solid", borderwidth=1, padx=5).grid(row=row_idx, column=len(anos)+1, sticky="ew")
    tk.Label(frame_resumen, text="100.00%", font=header_font, anchor="e", bg="red", fg="white", relief="solid", borderwidth=1, padx=5).grid(row=row_idx, column=len(anos)+2, sticky="ew")

    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

    def crear_tabla_ano(ano):
        frame_ano = tk.Frame(notebook)
        notebook.add(frame_ano, text=str(ano))

        canvas = tk.Canvas(frame_ano)
        scrollbar = tk.Scrollbar(frame_ano, orient="vertical", command=canvas.yview)
        frame_tabla = tk.Frame(canvas)

        canvas.create_window((0, 0), window=frame_tabla, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(frame_tabla, text="Activo", borderwidth=1, relief="solid", width=15,
                bg="yellow", fg="blue", font=("Arial", 12, "bold")).grid(row=0, column=0)

        for i, mes in enumerate(meses):
            tk.Label(frame_tabla, text=mes, borderwidth=1, relief="solid", width=8,
                    bg="yellow", fg="blue", font=("Arial", 12, "bold")).grid(row=0, column=i+1)

        tk.Label(frame_tabla, text="Total", borderwidth=1, relief="solid", width=10,
                bg="orange", fg="blue", font=("Arial", 12, "bold")).grid(row=0, column=13)

        entries = {}
        totales_fila = {}
        totales_mes = [tk.StringVar() for _ in range(12)]
        total_general = tk.StringVar()

        def actualizar_totales():
            total_gral = 0
            for activo in activos_con_dividendos:
                simbolo = activo.simbolo
                total_fila = 0
                for mes_idx in range(12):
                    try:
                        valor = float(entries[simbolo][mes_idx].get() or 0)
                        total_fila += valor
                    except ValueError:
                        pass
                totales_fila[simbolo].set(f"{total_fila:.2f}")
                total_gral += total_fila

            for mes_idx in range(12):
                total_mes = 0
                for activo in activos_con_dividendos:
                    simbolo = activo.simbolo
                    entry = entries[simbolo][mes_idx]
                    try:
                        valor = float(entry.get() or 0)
                        total_mes += valor
                        if valor > 0:
                            entry.config(bg="#90EE90")
                        else:
                            entry.config(bg="white")
                    except ValueError:
                        entry.config(bg="white")
                totales_mes[mes_idx].set(f"{total_mes:.2f}")

            total_general.set(f"{total_gral:.2f}")

            if str(ano) not in dividendos_data:
                dividendos_data[str(ano)] = {}
            for activo in activos_con_dividendos:
                simbolo = activo.simbolo
                dividendos_data[str(ano)][simbolo] = [entry.get() for entry in entries[simbolo]]

        for index, activo in enumerate(activos_con_dividendos):
            simbolo = activo.simbolo
            tk.Label(frame_tabla, text=simbolo, borderwidth=1, relief="solid", width=15,
                    anchor="w").grid(row=index+1, column=0)

            entries[simbolo] = []
            totales_fila[simbolo] = tk.StringVar()

            for mes_idx in range(12):
                valor_inicial = ""
                if str(ano) in dividendos_data and simbolo in dividendos_data[str(ano)]:
                    if mes_idx < len(dividendos_data[str(ano)][simbolo]):
                        valor_inicial = dividendos_data[str(ano)][simbolo][mes_idx]

                entry = tk.Entry(frame_tabla, width=8, justify="center")
                entry.insert(0, valor_inicial)
                entry.bind('<KeyRelease>', lambda e: actualizar_totales())
                entry.grid(row=index+1, column=mes_idx+1, padx=1, pady=1)
                entries[simbolo].append(entry)

            tk.Label(frame_tabla, textvariable=totales_fila[simbolo], borderwidth=1, relief="solid",
                    width=10, anchor="center", bg="lightgray").grid(row=index+1, column=13)

        tk.Label(frame_tabla, text="TOTAL", borderwidth=1, relief="solid", width=15,
                bg="orange", fg="blue", font=("Arial", 12, "bold")).grid(row=len(activos_con_dividendos)+1, column=0)

        for mes_idx in range(12):
            tk.Label(frame_tabla, textvariable=totales_mes[mes_idx], borderwidth=1, relief="solid",
                    width=8, anchor="center", bg="lightgray", font=("Arial", 12, "bold")).grid(row=len(activos_con_dividendos)+1, column=mes_idx+1)

        tk.Label(frame_tabla, textvariable=total_general, borderwidth=1, relief="solid",
                width=10, anchor="center", bg="orange", font=("Arial", 12, "bold")).grid(row=len(activos_con_dividendos)+1, column=13)

        actualizar_totales()
        frame_tabla.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    for ano in ANOS_DIVIDENDOS:
        crear_tabla_ano(ano)

    frame_guardar = tk.Frame(ventana)
    frame_guardar.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
    
    def guardar_cambios_dividendos():
        guardar_dividendos(dividendos_data)
        messagebox.showinfo("Guardado", "Todos los dividendos han sido guardados en disco correctamente.")
        
    tk.Button(frame_guardar, text="Guardar Todos los Dividendos", command=guardar_cambios_dividendos, bg="green", fg="black", font=("Arial", 12, "bold"), height=2).pack(side=tk.RIGHT)

def ventana_agregar_saldo_mensual():
    ventana = tk.Toplevel()
    ventana.title("Añadir Nuevo Saldo Mensual")
    ventana.geometry("400x350")

    def format_float_to_euro_str(value):
        is_negative = value < 0
        abs_value = abs(value)
        s = f"{abs_value:.2f}"
        s = s.replace('.', ',')
        parts = s.split(',')
        integer_part = parts[0]
        decimal_part = parts[1] if len(parts) > 1 else '00'

        formatted_integer_part = []
        for i, digit in enumerate(reversed(integer_part)):
            if i > 0 and i % 3 == 0:
                formatted_integer_part.append('.')
            formatted_integer_part.append(digit)
        formatted_integer_part = "".join(reversed(formatted_integer_part))

        sign = "-" if is_negative else ""
        return f"{sign}{formatted_integer_part},{decimal_part} €"

    tk.Label(ventana, text="Año (YYYY):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_ano = tk.Entry(ventana, width=10)
    entry_ano.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(ventana, text="Mes:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    mes_var = tk.StringVar(ventana)
    mes_var.set(meses[0]) 
    option_mes = tk.OptionMenu(ventana, mes_var, *meses)
    option_mes.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(ventana, text="Ingresos (€):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    entry_ingresos = tk.Entry(ventana, width=15)
    entry_ingresos.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(ventana, text="Gastos (€):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
    entry_gastos = tk.Entry(ventana, width=15)
    entry_gastos.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(ventana, text="Saldo (€):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
    saldo_var = tk.StringVar(value="0,00 €")
    entry_saldo = tk.Entry(ventana, textvariable=saldo_var, state="readonly", width=15)
    entry_saldo.grid(row=4, column=1, padx=5, pady=5)

    def actualizar_saldo(*args):
        try:
            ingresos = float(entry_ingresos.get().replace('.', '').replace(',', '.') or 0.0)
            gastos = float(entry_gastos.get().replace('.', '').replace(',', '.') or 0.0)
            saldo = ingresos - gastos
            saldo_var.set(format_float_to_euro_str(saldo))
        except ValueError:
            saldo_var.set("Error")

    entry_ingresos.bind('<KeyRelease>', actualizar_saldo)
    entry_gastos.bind('<KeyRelease>', actualizar_saldo)

    def guardar_saldo_mensual():
        ano_str = entry_ano.get().strip()
        mes = mes_var.get()
        
        if not ano_str.isdigit() or len(ano_str) != 4:
            messagebox.showerror("Error", "El año debe ser un número de 4 dígitos.")
            return
        
        try:
            ingresos = float(entry_ingresos.get().replace('.', '').replace(',', '.') or 0.0)
            gastos = float(entry_gastos.get().replace('.', '').replace(',', '.') or 0.0)
        except ValueError:
            messagebox.showerror("Error", "Ingresos y Gastos deben ser números válidos.")
            return

        saldo = ingresos - gastos

        ingresos_csv = format_float_to_euro_str(ingresos)
        gastos_csv = format_float_to_euro_str(gastos)
        saldo_csv = format_float_to_euro_str(saldo)

        linea_nueva = f"{ano_str}\t{mes}\t{ingresos_csv}\t{gastos_csv}\t{saldo_csv}\n"
        
        ruta_csv = os.path.join(os.path.dirname(__file__), "..", "BalancesMensuales.csv")
        try:
            if not os.path.exists(ruta_csv) or os.path.getsize(ruta_csv) == 0:
                with open(ruta_csv, "w", encoding="utf-8") as f:
                    f.write("AÑO\tMES\tINGRESOS\tGASTOS\tSALDO\n")

            with open(ruta_csv, "a", encoding="utf-8") as f:
                f.write(linea_nueva)
            messagebox.showinfo("Éxito", "Saldo mensual añadido correctamente.")
            ventana.destroy()
            
            global ventana_saldos_ref
            if ventana_saldos_ref is not None and ventana_saldos_ref.winfo_exists():
                ventana_saldos_mensuales()
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el saldo: {e}")

    tk.Button(ventana, text="Guardar Saldo", command=guardar_saldo_mensual, bg="green", fg="black", font=("Arial", 10, "bold")).grid(row=5, column=0, columnspan=2, padx=10, pady=20)

def ventana_saldos_mensuales():
    global ventana_saldos_ref
    if ventana_saldos_ref is not None and ventana_saldos_ref.winfo_exists():
        ventana_saldos_ref.destroy()

    ventana = tk.Toplevel()
    ventana_saldos_ref = ventana
    ventana.title("Saldos Mensuales")
    ventana.geometry("800x1000")

    # Obtener ruta al archivo CSV
    ruta_csv = os.path.join(os.path.dirname(__file__), "..", "BalancesMensuales.csv")
    ruta_csv = os.path.abspath(ruta_csv)

    # Función para convertir valores de euros a float
    def convertir_euro_a_float(valor_str):
        if not valor_str or valor_str.strip() == '':
            return 0.0
        valor_str = valor_str.strip()
        valor_str = valor_str.replace('€', '').strip()
        valor_str = valor_str.replace('.', '')  # Eliminar separadores de miles
        valor_str = valor_str.replace(',', '.')  # Cambiar coma decimal a punto
        try:
            return float(valor_str)
        except ValueError:
            return 0.0

    # Parsear el archivo CSV
    datos_por_ano = {}
    ano_actual = None

    try:
        with open(ruta_csv, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            
        for linea in lineas[1:]:  # Omitir encabezado
            # Solo remover saltos de línea, no espacios al inicio
            linea = linea.rstrip('\n\r')
            if not linea or linea.strip() == '':
                continue
            
            partes = linea.split('\t')
            
            # Si la línea comienza con un año
            if partes[0] and partes[0][0].isdigit() and len(partes[0]) == 4:
                ano_actual = int(partes[0])
                if ano_actual not in datos_por_ano:
                    datos_por_ano[ano_actual] = []
                mes = partes[1].strip() if len(partes) > 1 else ''
                ingresos = convertir_euro_a_float(partes[2] if len(partes) > 2 else '0')
                gastos = convertir_euro_a_float(partes[3] if len(partes) > 3 else '0')
                saldo = convertir_euro_a_float(partes[4] if len(partes) > 4 else '0')
                datos_por_ano[ano_actual].append({
                    'mes': mes,
                    'ingresos': ingresos,
                    'gastos': gastos,
                    'saldo': saldo
                })
            # Si no comienza con año, es un mes del año anterior
            elif ano_actual is not None and partes[0].strip() == '':
                mes = partes[1].strip() if len(partes) > 1 else ''
                ingresos = convertir_euro_a_float(partes[2] if len(partes) > 2 else '0')
                gastos = convertir_euro_a_float(partes[3] if len(partes) > 3 else '0')
                saldo = convertir_euro_a_float(partes[4] if len(partes) > 4 else '0')
                datos_por_ano[ano_actual].append({
                    'mes': mes,
                    'ingresos': ingresos,
                    'gastos': gastos,
                    'saldo': saldo
                })
    except FileNotFoundError:
        tk.Label(ventana, text="No se encontró el archivo BalancesMensuales.csv", font=("Arial", 14)).pack(pady=50)
        return

    if datos_por_ano:
        anos_ordenados = sorted(datos_por_ano.keys())
        ventana.title(f"Balances anuales del {anos_ordenados[0]} al {anos_ordenados[-1]}")

    # --- Tabla Resumen General ---
    resumen_anual = {}
    gran_total_ingresos = 0
    gran_total_gastos = 0
    gran_total_saldo = 0

    for ano, meses_data in sorted(datos_por_ano.items()):
        total_ingresos_ano = sum(d['ingresos'] for d in meses_data)
        total_gastos_ano = sum(d['gastos'] for d in meses_data)
        total_saldo_ano = sum(d['saldo'] for d in meses_data)
        
        resumen_anual[ano] = {
            'ingresos': total_ingresos_ano,
            'gastos': total_gastos_ano,
            'saldo': total_saldo_ano
        }
        
        gran_total_ingresos += total_ingresos_ano
        gran_total_gastos += total_gastos_ano
        gran_total_saldo += total_saldo_ano

    frame_resumen_general = tk.LabelFrame(ventana, text="Resumen Anual General", font=("Arial", 12, "bold"), padx=10, pady=10)
    frame_resumen_general.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    headers = ["AÑO", "TOTAL INGRESOS", "TOTAL GASTOS", "TOTAL SALDO"]
    for i, header in enumerate(headers):
        tk.Label(frame_resumen_general, text=header, font=("Arial", 10, "bold"), bg="lightblue", relief="solid", borderwidth=1).grid(row=0, column=i, sticky="ew", padx=2, pady=2)

    row_idx = 1
    for ano, totales in sorted(resumen_anual.items()):
        tk.Label(frame_resumen_general, text=str(ano), font=("Arial", 9), anchor="w", relief="solid", borderwidth=1).grid(row=row_idx, column=0, sticky="ew", padx=2, pady=2)
        tk.Label(frame_resumen_general, text=f"{totales['ingresos']:.2f}€", font=("Arial", 9), anchor="e", relief="solid", borderwidth=1).grid(row=row_idx, column=1, sticky="ew", padx=2, pady=2)
        tk.Label(frame_resumen_general, text=f"{totales['gastos']:.2f}€", font=("Arial", 9), anchor="e", relief="solid", borderwidth=1).grid(row=row_idx, column=2, sticky="ew", padx=2, pady=2)
        tk.Label(frame_resumen_general, text=f"{totales['saldo']:.2f}€", font=("Arial", 9), anchor="e", relief="solid", borderwidth=1).grid(row=row_idx, column=3, sticky="ew", padx=2, pady=2)
        row_idx += 1

    tk.Label(frame_resumen_general, text="TOTAL", font=("Arial", 12, "bold"), bg="orange", relief="solid", borderwidth=2, anchor="w").grid(row=row_idx, column=0, sticky="ew", padx=2, pady=5)
    tk.Label(frame_resumen_general, text=f"{gran_total_ingresos:.2f}€", font=("Arial", 12, "bold"), bg="orange", relief="solid", borderwidth=2, anchor="e").grid(row=row_idx, column=1, sticky="ew", padx=2, pady=5)
    tk.Label(frame_resumen_general, text=f"{gran_total_gastos:.2f}€", font=("Arial", 12, "bold"), bg="orange", relief="solid", borderwidth=2, anchor="e").grid(row=row_idx, column=2, sticky="ew", padx=2, pady=5)
    tk.Label(frame_resumen_general, text=f"{gran_total_saldo:.2f}€", font=("Arial", 12, "bold"), bg="orange", relief="solid", borderwidth=2, anchor="e").grid(row=row_idx, column=3, sticky="ew", padx=2, pady=5)

    for i in range(4):
        frame_resumen_general.grid_columnconfigure(i, weight=1)

    # Frame para el índice superior
    frame_indice = tk.Frame(ventana)
    frame_indice.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
    tk.Label(frame_indice, text="Ir al año:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5, anchor="n", pady=4)
    frame_botones_indice = tk.Frame(frame_indice)
    frame_botones_indice.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Frame con scroll
    frame_scroll = tk.Frame(ventana)
    frame_scroll.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

    canvas = tk.Canvas(frame_scroll)
    scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
    frame_contenido = tk.Frame(canvas)

    canvas.create_window((0, 0), window=frame_contenido, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    frames_por_ano = {}

    # Mostrar datos
    for ano in sorted(datos_por_ano.keys()):
        # Frame para el año
        frame_ano = tk.LabelFrame(frame_contenido, text=f"AÑO {ano}", font=("Arial", 12, "bold"), padx=10, pady=10)
        frame_ano.pack(fill=tk.X, padx=5, pady=10)
        frames_por_ano[ano] = frame_ano

        # Encabezados
        tk.Label(frame_ano, text="MES", font=("Arial", 10, "bold"), bg="lightblue", relief="solid", borderwidth=1, width=15, anchor="w").grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        tk.Label(frame_ano, text="INGRESOS", font=("Arial", 10, "bold"), bg="lightblue", relief="solid", borderwidth=1, width=15, anchor="e").grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        tk.Label(frame_ano, text="GASTOS", font=("Arial", 10, "bold"), bg="lightblue", relief="solid", borderwidth=1, width=15, anchor="e").grid(row=0, column=2, sticky="ew", padx=2, pady=2)
        tk.Label(frame_ano, text="SALDO", font=("Arial", 10, "bold"), bg="lightblue", relief="solid", borderwidth=1, width=15, anchor="e").grid(row=0, column=3, sticky="ew", padx=2, pady=2)

        # Datos mensuales
        meses = datos_por_ano[ano]
        total_ingresos = 0
        total_gastos = 0
        total_saldo = 0

        for i, mes_data in enumerate(meses, start=1):
            total_ingresos += mes_data['ingresos']
            total_gastos += mes_data['gastos']
            total_saldo += mes_data['saldo']

            tk.Label(frame_ano, text=mes_data['mes'], font=("Arial", 9), anchor="w", relief="solid", borderwidth=1).grid(row=i, column=0, sticky="ew", padx=2, pady=2)
            tk.Label(frame_ano, text=f"{mes_data['ingresos']:.2f}€", font=("Arial", 9), anchor="e", relief="solid", borderwidth=1).grid(row=i, column=1, sticky="ew", padx=2, pady=2)
            tk.Label(frame_ano, text=f"{mes_data['gastos']:.2f}€", font=("Arial", 9), anchor="e", relief="solid", borderwidth=1).grid(row=i, column=2, sticky="ew", padx=2, pady=2)
            tk.Label(frame_ano, text=f"{mes_data['saldo']:.2f}€", font=("Arial", 9), anchor="e", relief="solid", borderwidth=1).grid(row=i, column=3, sticky="ew", padx=2, pady=2)

        # Fila de totales
        row_total = len(meses) + 1
        tk.Label(frame_ano, text="TOTAL AÑO", font=("Arial", 12, "bold"), bg="orange", relief="solid", borderwidth=2, anchor="w").grid(row=row_total, column=0, sticky="ew", padx=2, pady=5)
        tk.Label(frame_ano, text=f"{total_ingresos:.2f}€", font=("Arial", 12, "bold"), bg="orange", relief="solid", borderwidth=2, anchor="e").grid(row=row_total, column=1, sticky="ew", padx=2, pady=5)
        tk.Label(frame_ano, text=f"{total_gastos:.2f}€", font=("Arial", 12, "bold"), bg="orange", relief="solid", borderwidth=2, anchor="e").grid(row=row_total, column=2, sticky="ew", padx=2, pady=5)
        tk.Label(frame_ano, text=f"{total_saldo:.2f}€", font=("Arial", 12, "bold"), bg="orange", relief="solid", borderwidth=2, anchor="e").grid(row=row_total, column=3, sticky="ew", padx=2, pady=5)

        frame_ano.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Función y botones para el índice
    def ir_a_ano(ano_seleccionado):
        frame_contenido.update_idletasks()
        y_pos = frames_por_ano[ano_seleccionado].winfo_y()
        total_height = frame_contenido.winfo_height()
        if total_height > 0:
            canvas.yview_moveto(y_pos / total_height)

    for i, ano in enumerate(sorted(datos_por_ano.keys())):
        fila = i // 10
        columna = i % 10
        tk.Button(frame_botones_indice, text=str(ano), command=lambda a=ano: ir_a_ano(a)).grid(row=fila, column=columna, padx=2, pady=2)

    canvas.bind('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    canvas.bind('<Button-4>', lambda e: canvas.yview_scroll(5, "units"))
    canvas.bind('<Button-5>', lambda e: canvas.yview_scroll(-5, "units"))


def cargar_patrimonio():
    """Carga los datos de patrimonio del archivo JSON"""
    try:
        with open(PATRIMONIO_ARCHIVO, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return {}


def guardar_patrimonio(patrimonio_data):
    """Guarda los datos de patrimonio en archivo JSON"""
    os.makedirs(os.path.dirname(PATRIMONIO_ARCHIVO), exist_ok=True)
    with open(PATRIMONIO_ARCHIVO, "w", encoding="utf-8") as archivo:
        json.dump(patrimonio_data, archivo, indent=4, ensure_ascii=False)


def ventana_patrimonio():
    """Ventana para gestionar el patrimonio mensual"""
    ventana = tk.Toplevel()
    ventana.title("Patrimonio")
    ventana.geometry("1200x800")

    # Meses y columnas a mostrar
    meses = ["Enero", "Marzo", "Mayo", "Julio", "Octubre", "Diciembre"]
    anos = [2020, 2021, 2022, 2023, 2024, 2025, 2026]
    
    patrimonio_data = cargar_patrimonio()
    
    # --- LEYENDA ---
    frame_leyenda = tk.LabelFrame(ventana, text="Leyenda", font=("Arial", 10, "bold"), 
                                   bg="lightyellow", padx=10, pady=8)
    frame_leyenda.pack(fill=tk.X, padx=10, pady=8)
    
    frame_leyenda_contenido = tk.Frame(frame_leyenda, bg="lightyellow")
    frame_leyenda_contenido.pack(fill=tk.X)
    
    tk.Label(frame_leyenda_contenido, text="Cuentas Corrientes (CC):", 
             font=("Arial", 9, "bold"), bg="lightblue", relief="solid", 
             borderwidth=1, width=20, anchor="w").pack(side=tk.LEFT, padx=3, pady=3)
    tk.Label(frame_leyenda_contenido, text="CaixaBank, BBVA", 
             font=("Arial", 9), bg="lightyellow").pack(side=tk.LEFT, padx=3, pady=3)
    
    tk.Label(frame_leyenda_contenido, text="Planes de Pensiones (PP):", 
             font=("Arial", 9, "bold"), bg="lightgreen", relief="solid", 
             borderwidth=1, width=20, anchor="w").pack(side=tk.LEFT, padx=10, pady=3)
    tk.Label(frame_leyenda_contenido, text="CaixaBank, Santander", 
             font=("Arial", 9), bg="lightyellow").pack(side=tk.LEFT, padx=3, pady=3)
    
    tk.Label(frame_leyenda_contenido, text="Inversiones (INV):", 
             font=("Arial", 9, "bold"), bg="lightyellow", relief="solid", 
             borderwidth=1, width=20, anchor="w").pack(side=tk.LEFT, padx=10, pady=3)
    tk.Label(frame_leyenda_contenido, text="Degiro, Fondo BBVA, Ocean Broker", 
             font=("Arial", 9), bg="lightyellow").pack(side=tk.LEFT, padx=3, pady=3)
    
    # --- FRAME PRINCIPAL CON SCROLL VERTICAL ---
    frame_principal_scroll = tk.Frame(ventana)
    frame_principal_scroll.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
    
    # Canvas con scrollbar vertical
    canvas_principal = tk.Canvas(frame_principal_scroll, bg="white", highlightthickness=0)
    scrollbar_vertical = tk.Scrollbar(frame_principal_scroll, orient="vertical", command=canvas_principal.yview)
    frame_tablas = tk.Frame(canvas_principal, bg="white")
    
    canvas_principal.create_window((0, 0), window=frame_tablas, anchor="nw")
    canvas_principal.configure(yscrollcommand=scrollbar_vertical.set)
    
    canvas_principal.pack(side="left", fill=tk.BOTH, expand=True)
    scrollbar_vertical.pack(side="right", fill="y")
    
    # Bind mouse wheel para scroll vertical
    def _on_mousewheel(event):
        canvas_principal.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas_principal.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Diccionario para almacenar las entradas
    entries = {}
    
    def crear_tabla(parent_frame, tipo_cuenta, columnas, color_header, color_subheader):
        """Crea una tabla para un tipo de cuenta"""
        frame_tabla_grupo = tk.LabelFrame(parent_frame, text=tipo_cuenta, 
                                           font=("Arial", 11, "bold"), 
                                           bg=color_header, padx=8, pady=8)
        frame_tabla_grupo.pack(fill=tk.X, padx=5, pady=5)
        
        # Frame para la tabla sin scroll horizontal
        frame_tabla = tk.Frame(frame_tabla_grupo)
        frame_tabla.pack(fill=tk.X)
        
        # Encabezado con años
        tk.Label(frame_tabla, text="Mes", font=("Arial", 9, "bold"), 
                 bg="lightgray", relief="solid", borderwidth=1, width=10).grid(row=0, column=0, sticky="ew", padx=1, pady=1)
        
        for col_idx, columna in enumerate(columnas, start=1):
            tk.Label(frame_tabla, text=columna, font=("Arial", 8, "bold"), 
                     bg=color_subheader, relief="solid", borderwidth=1, width=8).grid(row=0, column=col_idx, sticky="ew", padx=1, pady=1)
        
        # Filas para cada mes
        for row_idx, mes in enumerate(meses, start=1):
            tk.Label(frame_tabla, text=mes, font=("Arial", 9, "bold"), 
                     bg="lightgray", relief="solid", borderwidth=1, width=10).grid(row=row_idx, column=0, sticky="ew", padx=1, pady=1)
            
            entries[mes] = entries.get(mes, {})
            
            # Campos para esta tabla
            for col_idx, columna in enumerate(columnas, start=1):
                valor = patrimonio_data.get(mes, {}).get(columna, "")
                entry = tk.Entry(frame_tabla, width=8, justify="center", font=("Arial", 8))
                entry.insert(0, str(valor))
                entry.grid(row=row_idx, column=col_idx, sticky="ew", padx=1, pady=1)
                entries[mes][columna] = entry
    
    # Layout en dos columnas principales para evitar separación vertical indeseada
    frame_columna_izq = tk.Frame(frame_tablas, bg="white")
    frame_columna_izq.pack(side=tk.LEFT, fill=tk.Y, anchor="nw", padx=5)
    
    frame_columna_der = tk.Frame(frame_tablas, bg="white")
    frame_columna_der.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, anchor="nw", padx=5)
    
    # Contenedores de la columna izquierda (Tablas apiladas verticalmente)
    frame_cc_container = tk.Frame(frame_columna_izq, bg="white")
    frame_cc_container.pack(fill=tk.X, anchor="nw")
    
    frame_pp_container = tk.Frame(frame_columna_izq, bg="white")
    frame_pp_container.pack(fill=tk.X, anchor="nw")
    
    frame_inv_container = tk.Frame(frame_columna_izq, bg="white")
    frame_inv_container.pack(fill=tk.X, anchor="nw")
    
    # Contenedores de la columna derecha (Gráfico y Totales apilados verticalmente)
    frame_chart_container = tk.Frame(frame_columna_der, bg="white")
    frame_chart_container.pack(fill=tk.X, anchor="nw")
    
    frame_totales_container = tk.Frame(frame_columna_der, bg="white")
    frame_totales_container.pack(fill=tk.X, anchor="nw")
    
    fig_patrimonio, ax_patrimonio = plt.subplots(figsize=(4, 3))
    canvas_patrimonio = FigureCanvasTkAgg(fig_patrimonio, master=frame_chart_container)
    canvas_patrimonio.get_tk_widget().pack(anchor="nw")

    # Etiqueta destacada para el Total del último mes de 2026
    lbl_total_destacado = tk.Label(frame_chart_container, text="Total 2026: 0,00 €", font=("Arial", 16, "bold"), fg="blue", bg="white")
    lbl_total_destacado.pack(pady=10, anchor="nw")

    ano_grafico = 2025

    # Crear las tres tablas
    cc_columnas = [f"cc{ano}" for ano in anos]
    crear_tabla(frame_cc_container, "CUENTAS CORRIENTES", cc_columnas, "lightblue", "lightskyblue")
    
    pp_columnas = [f"PP{ano}" for ano in anos]
    crear_tabla(frame_pp_container, "PLANES DE PENSIONES", pp_columnas, "lightgreen", "palegreen")
    
    inv_columnas = [f"INV{ano}" for ano in anos]
    crear_tabla(frame_inv_container, "INVERSIONES", inv_columnas, "lightyellow", "khaki")
    
    # --- TABLA DE TOTALES POR AÑO ---
    frame_totales_grupo = tk.LabelFrame(frame_totales_container, text="TOTALES POR AÑO", 
                                         font=("Arial", 11, "bold"), 
                                         bg="lightyellow", padx=8, pady=8)
    frame_totales_grupo.pack(fill=tk.X, padx=5, pady=5, anchor="nw")
    
    frame_totales = tk.Frame(frame_totales_grupo)
    frame_totales.pack(fill=tk.X)
    
    # Encabezado con años
    tk.Label(frame_totales, text="Año", font=("Arial", 9, "bold"), 
             bg="lightgray", relief="solid", borderwidth=1, width=15).grid(row=0, column=0, sticky="ew", padx=1, pady=1)
    
    for col_idx, ano in enumerate(anos, start=1):
        tk.Label(frame_totales, text=str(ano), font=("Arial", 8, "bold"), 
                 bg="orange", relief="solid", borderwidth=1, width=8).grid(row=0, column=col_idx, sticky="ew", padx=1, pady=1)
    
    # Fila de totales Enero
    tk.Label(frame_totales, text="Total Enero", font=("Arial", 9, "bold"), 
             bg="orange", relief="solid", borderwidth=1, width=15).grid(row=1, column=0, sticky="ew", padx=1, pady=1)
    
    totales_enero_labels = {}
    for col_idx, ano in enumerate(anos, start=1):
        total_label = tk.Label(frame_totales, text="0.00", font=("Arial", 8, "bold"), 
                               bg="lightyellow", relief="solid", borderwidth=1, width=8)
        total_label.grid(row=1, column=col_idx, sticky="ew", padx=1, pady=1)
        totales_enero_labels[ano] = total_label
        
    # Fila de totales Diciembre
    tk.Label(frame_totales, text="Total Diciembre", font=("Arial", 9, "bold"), 
             bg="orange", relief="solid", borderwidth=1, width=15).grid(row=2, column=0, sticky="ew", padx=1, pady=1)
    
    totales_diciembre_labels = {}
    for col_idx, ano in enumerate(anos, start=1):
        total_label = tk.Label(frame_totales, text="0.00", font=("Arial", 8, "bold"), 
                               bg="lightyellow", relief="solid", borderwidth=1, width=8)
        total_label.grid(row=2, column=col_idx, sticky="ew", padx=1, pady=1)
        totales_diciembre_labels[ano] = total_label
    
    # Diccionarios para guardar los labels de porcentajes
    porcentajes_labels = {
        "% cc Enero": {},
        "Cant. cc Enero": {},
        "% cc Diciembre": {},
        "Cant. cc Diciembre": {},
        "% PP Enero": {},
        "Cant. PP Enero": {},
        "% PP Diciembre": {},
        "Cant. PP Diciembre": {},
        "% INV Enero": {},
        "Cant. INV Enero": {},
        "% INV Diciembre": {},
        "Cant. INV Diciembre": {}
    }
    
    # Crear filas para los porcentajes
    row_idx = 3
    for metrica in porcentajes_labels.keys():
        font_metrica = ("Arial", 8) if "Cant." in metrica else ("Arial", 9, "bold")
        bg_metrica = "white" if "Cant." in metrica else "lightyellow"
        
        tk.Label(frame_totales, text=metrica, font=font_metrica, 
                 bg=bg_metrica, relief="solid", borderwidth=1, width=15).grid(row=row_idx, column=0, sticky="ew", padx=1, pady=1)
        
        for col_idx, ano in enumerate(anos, start=1):
            pct_label = tk.Label(frame_totales, text="0.00" if "Cant." in metrica else "0.00%", font=("Arial", 8), 
                                bg="white", relief="solid", borderwidth=1, width=8)
            pct_label.grid(row=row_idx, column=col_idx, sticky="ew", padx=1, pady=1)
            porcentajes_labels[metrica][ano] = pct_label
        
        row_idx += 1
    
    def actualizar_totales_anuales():
        """Actualiza los totales anuales y porcentajes basados en los valores de las tablas"""
        valores_grafico_2025 = [0, 0, 0]
        ultimo_mes_2026 = "Enero"
        total_ultimo_mes_2026 = 0.0
        
        for ano in anos:
            # Sumar CC + PP + INV para este año
            cc_col = f"cc{ano}"
            pp_col = f"PP{ano}"
            inv_col = f"INV{ano}"
            
            valores_meses = {}
            for mes in meses:
                valores_meses[mes] = {"cc": 0.0, "pp": 0.0, "inv": 0.0}
                
                if mes in entries:
                    try:
                        if cc_col in entries[mes]:
                            valor_cc = float(entries[mes][cc_col].get() or 0)
                            valores_meses[mes]["cc"] = valor_cc
                    except ValueError:
                        pass
                    try:
                        if pp_col in entries[mes]:
                            valor_pp = float(entries[mes][pp_col].get() or 0)
                            valores_meses[mes]["pp"] = valor_pp
                    except ValueError:
                        pass
                    try:
                        if inv_col in entries[mes]:
                            valor_inv = float(entries[mes][inv_col].get() or 0)
                            valores_meses[mes]["inv"] = valor_inv
                    except ValueError:
                        pass
            
            total_enero = valores_meses["Enero"]["cc"] + valores_meses["Enero"]["pp"] + valores_meses["Enero"]["inv"]
            total_diciembre = valores_meses["Diciembre"]["cc"] + valores_meses["Diciembre"]["pp"] + valores_meses["Diciembre"]["inv"]
            
            if ano == ano_grafico:
                valores_grafico_2025 = [
                    valores_meses["Diciembre"]["cc"],
                    valores_meses["Diciembre"]["pp"],
                    valores_meses["Diciembre"]["inv"]
                ]
            
            if ano == 2026:
                for mes_iter in meses:
                    total_mes_iter = valores_meses[mes_iter]["cc"] + valores_meses[mes_iter]["pp"] + valores_meses[mes_iter]["inv"]
                    if total_mes_iter > 0:
                        ultimo_mes_2026 = mes_iter
                        total_ultimo_mes_2026 = total_mes_iter

            # Actualizar totales
            totales_enero_labels[ano].config(text=f"{total_enero:.2f}")
            totales_diciembre_labels[ano].config(text=f"{total_diciembre:.2f}")
            
            # Calcular y actualizar porcentajes Enero
            if total_enero > 0:
                pct_cc_ene = (valores_meses["Enero"]["cc"] / total_enero) * 100
                porcentajes_labels["% cc Enero"][ano].config(text=f"{pct_cc_ene:.2f}%")
                porcentajes_labels["Cant. cc Enero"][ano].config(text=f"{valores_meses['Enero']['cc']:.2f}")
                
                pct_pp_ene = (valores_meses["Enero"]["pp"] / total_enero) * 100
                porcentajes_labels["% PP Enero"][ano].config(text=f"{pct_pp_ene:.2f}%")
                porcentajes_labels["Cant. PP Enero"][ano].config(text=f"{valores_meses['Enero']['pp']:.2f}")
                
                pct_inv_ene = (valores_meses["Enero"]["inv"] / total_enero) * 100
                porcentajes_labels["% INV Enero"][ano].config(text=f"{pct_inv_ene:.2f}%")
                porcentajes_labels["Cant. INV Enero"][ano].config(text=f"{valores_meses['Enero']['inv']:.2f}")
            else:
                porcentajes_labels["% cc Enero"][ano].config(text="0.00%")
                porcentajes_labels["Cant. cc Enero"][ano].config(text="0.00")
                porcentajes_labels["% PP Enero"][ano].config(text="0.00%")
                porcentajes_labels["Cant. PP Enero"][ano].config(text="0.00")
                porcentajes_labels["% INV Enero"][ano].config(text="0.00%")
                porcentajes_labels["Cant. INV Enero"][ano].config(text="0.00")
                
            # Calcular y actualizar porcentajes Diciembre
            if total_diciembre > 0:
                pct_cc_dic = (valores_meses["Diciembre"]["cc"] / total_diciembre) * 100
                porcentajes_labels["% cc Diciembre"][ano].config(text=f"{pct_cc_dic:.2f}%")
                porcentajes_labels["Cant. cc Diciembre"][ano].config(text=f"{valores_meses['Diciembre']['cc']:.2f}")
                
                pct_pp_dic = (valores_meses["Diciembre"]["pp"] / total_diciembre) * 100
                porcentajes_labels["% PP Diciembre"][ano].config(text=f"{pct_pp_dic:.2f}%")
                porcentajes_labels["Cant. PP Diciembre"][ano].config(text=f"{valores_meses['Diciembre']['pp']:.2f}")
                
                pct_inv_dic = (valores_meses["Diciembre"]["inv"] / total_diciembre) * 100
                porcentajes_labels["% INV Diciembre"][ano].config(text=f"{pct_inv_dic:.2f}%")
                porcentajes_labels["Cant. INV Diciembre"][ano].config(text=f"{valores_meses['Diciembre']['inv']:.2f}")
            else:
                porcentajes_labels["% cc Diciembre"][ano].config(text="0.00%")
                porcentajes_labels["Cant. cc Diciembre"][ano].config(text="0.00")
                porcentajes_labels["% PP Diciembre"][ano].config(text="0.00%")
                porcentajes_labels["Cant. PP Diciembre"][ano].config(text="0.00")
                porcentajes_labels["% INV Diciembre"][ano].config(text="0.00%")
                porcentajes_labels["Cant. INV Diciembre"][ano].config(text="0.00")
                
        # Actualizar gráfico de sectores
        ax_patrimonio.clear()
        labels = ['CC', 'PP', 'INV']
        colores = ['lightblue', 'lightgreen', 'lightyellow']
        if sum(valores_grafico_2025) > 0:
            def formato_autopct(pct):
                total = sum(valores_grafico_2025)
                val = (pct * total) / 100.0
                val_str = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                return f"{pct:.1f}%\n{val_str} €"
            ax_patrimonio.pie(valores_grafico_2025, labels=labels, autopct=formato_autopct, startangle=140, colors=colores, textprops={'fontsize': 9})
        ax_patrimonio.set_title(f'Distribución Diciembre {ano_grafico}', fontsize=10, fontweight='bold')
        fig_patrimonio.tight_layout()
        canvas_patrimonio.draw()
        
        # Actualizar etiqueta de Total con el último mes de 2026 con formato de millares
        lbl_total_destacado.config(text=f"Total {ultimo_mes_2026} 2026: {total_ultimo_mes_2026:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
    
    # Vincular actualización de totales a cambios en las entradas
    def crear_actualizador_totales(inputs):
        """Crea una función para actualizar los totales cuando cambian los campos"""
        def actualizar(*args):
            actualizar_totales_anuales()
        return actualizar
    
    for mes in entries:
        for columna in entries[mes]:
            entries[mes][columna].bind('<KeyRelease>', crear_actualizador_totales(entries))
    
    # Actualizar totales inicialmente
    actualizar_totales_anuales()
    
    # Actualizar scrollregion del canvas principal
    frame_tablas.bind("<Configure>", lambda e: canvas_principal.configure(scrollregion=canvas_principal.bbox("all")))
    
    # Frame de botones
    frame_botones = tk.Frame(ventana)
    frame_botones.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
    
    def guardar_patrimonio_datos():
        """Guarda los datos del patrimonio"""
        datos_nuevos = {}
        todas_columnas = cc_columnas + pp_columnas + inv_columnas
        
        for mes in meses:
            datos_nuevos[mes] = {}
            for columna in todas_columnas:
                if mes in entries and columna in entries[mes]:
                    valor_texto = entries[mes][columna].get().strip()
                    if valor_texto:
                        try:
                            datos_nuevos[mes][columna] = float(valor_texto)
                        except ValueError:
                            entries[mes][columna].config(bg="red")
                            messagebox.showerror("Error", f"El valor en {mes} - {columna} no es un número válido.")
                            return
                        entries[mes][columna].config(bg="white")
                    else:
                        datos_nuevos[mes][columna] = ""
        
        guardar_patrimonio(datos_nuevos)
        messagebox.showinfo("Éxito", "Datos de patrimonio guardados correctamente.")
    
    tk.Button(frame_botones, text="Guardar Patrimonio", command=guardar_patrimonio_datos,
             bg="green", fg="black", font=("Arial", 11, "bold"), height=2, width=30).pack(side=tk.RIGHT, padx=5)



def iniciar_gui():
    root = tk.Tk()
    root.title("Gestor de Cartera AAF")
    root.geometry("600x400")

    # Forzar la ventana principal a estar en primer plano al iniciar
    root.attributes('-topmost', True)
    root.update()
    root.attributes('-topmost', False)

    tk.Label(root, text="Gestor de Cartera AAF", font=("Arial", 18, "bold")).pack(pady=30)

    frame_anadir = tk.Frame(root)
    frame_anadir.pack(pady=10)

    tk.Button(frame_anadir, text="Añadir Nuevos Activos", command=ventana_agregar_activos,
             width=25, height=2, font=("Arial", 12), bg="lightblue").pack(side=tk.LEFT, padx=10)
             
    tk.Button(frame_anadir, text="Añadir Nuevo Saldo Mensual", command=ventana_agregar_saldo_mensual,
             width=25, height=2, font=("Arial", 12), bg="lightskyblue").pack(side=tk.LEFT, padx=10)

    tk.Button(root, text="Ver Cartera", command=ventana_ver_cartera,
             width=25, height=2, font=("Arial", 12), bg="lightgreen").pack(pady=10)

    tk.Button(root, text="Ver Dividendos", command=ventana_dividendos,
             width=25, height=2, font=("Arial", 12), bg="lightyellow").pack(pady=10)

    tk.Button(root, text="Saldos Mensuales", command=ventana_saldos_mensuales,
             width=25, height=2, font=("Arial", 12), bg="lightcoral").pack(pady=10)

    tk.Button(root, text="Patrimonio", command=ventana_patrimonio,
             width=25, height=2, font=("Arial", 12), bg="lightsteelblue").pack(pady=10)

    root.mainloop()
