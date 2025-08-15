import pandas as pd
import yfinance as yf
from tabulate import tabulate
import tkinter as tk
from tkinter import messagebox
import json

CARPETA_ARCHIVO = "cartera.json"

def obtener_precios_actuales(simbolos):
    print("Obteniendo precios de mercado actuales...")
    tickers = yf.Tickers(" ".join(simbolos))
    precios = {}
    for simbolo in simbolos:
        try:
            ticker_info = tickers.tickers[simbolo].info
            precio = ticker_info.get('regularMarketPrice')
            if precio:
                precios[simbolo] = precio
            else:
                print(f"  - Advertencia: No se pudo obtener el precio para '{simbolo}'. Se omitirá.")
                precios[simbolo] = 0.0
        except Exception:
            print(f"  - Advertencia: Símbolo '{simbolo}' no encontrado o error al obtener datos.")
            precios[simbolo] = 0.0
    print("Precios obtenidos.")
    return precios

def cargar_cartera():
    try:
        with open(CARPETA_ARCHIVO, "r") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def guardar_cartera(cartera):
    with open(CARPETA_ARCHIVO, "w") as archivo:
        json.dump(cartera, archivo, indent=4)

def ventana_agregar_activos():
    ventana = tk.Toplevel()
    ventana.title("Agregar Nuevos Activos")
    ventana.geometry("600x400")
    
    cartera = cargar_cartera()
    
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
    
    def agregar_elemento():
        simbolo = entry_simbolo.get().strip()
        titulo = entry_titulo.get().strip()
        cantidad = entry_cantidad.get().strip()
        precio_manual = entry_precio_manual.get().strip()
        
        if not simbolo or not titulo or not cantidad.isdigit():
            messagebox.showerror("Error", "Campos obligatorios incompletos o inválidos.")
            return
        
        cantidad = int(cantidad)
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
        
        cartera.append({
            'símbolo': simbolo,
            'título': titulo,
            'cantidad': cantidad,
            'precio_actual': precio_actual,
            'importe_total': cantidad * precio_actual,
            'dividendos': 'Sí' if var_dividendos.get() else 'No',
            'tipo_activo': tipo_activo_var.get(),
            'broker': broker_var.get()
        })
        
        guardar_cartera(cartera)
        messagebox.showinfo("Éxito", "Elemento añadido a la cartera.")
        entry_simbolo.delete(0, tk.END)
        entry_titulo.delete(0, tk.END)
        entry_cantidad.delete(0, tk.END)
        entry_precio_manual.delete(0, tk.END)
        var_dividendos.set(False)
        tipo_activo_var.set('')
        broker_var.set('')
    
    boton_agregar = tk.Button(ventana, text="AGREGAR ACTIVO", command=agregar_elemento, 
                             bg="green", fg="white", font=("Arial", 10, "bold"))
    boton_agregar.grid(row=4, column=1, columnspan=2, padx=10, pady=20, sticky="ew")

def ventana_ver_cartera():
    ventana = tk.Toplevel()
    ventana.title("Ver Cartera")
    ventana.geometry("1200x800")
    
    cartera = cargar_cartera()
    
    if not cartera:
        tk.Label(ventana, text="No hay elementos en la cartera.", font=("Arial", 14)).pack(pady=50)
        return
    
    # Frame con scroll para la tabla
    frame_scroll = tk.Frame(ventana)
    frame_scroll.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    canvas = tk.Canvas(frame_scroll)
    scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
    frame_tabla = tk.Frame(canvas)
    
    canvas.create_window((0, 0), window=frame_tabla, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Ordenar cartera
    cartera_df = pd.DataFrame(cartera)
    orden_tipos = {'ACC': 0, 'ETF': 1, 'PP': 2, 'FON': 3}
    cartera_df['orden_tipo'] = cartera_df['tipo_activo'].map(orden_tipos)
    cartera_df = cartera_df.sort_values(['orden_tipo', 'símbolo']).drop('orden_tipo', axis=1)
    
    columnas = ['símbolo', 'título', 'cantidad', 'precio_actual', 'importe_total', 'dividendos', 'tipo_activo', 'broker']
    anchuras = {"símbolo": 10, "título": 25, "cantidad": 8, "precio_actual": 12, "importe_total": 12, "dividendos": 10, "tipo_activo": 8, "broker": 10}
    
    # Encabezados
    for i, columna in enumerate(columnas):
        anchor = "w" if columna == "título" else "center"
        tk.Label(frame_tabla, text=columna, borderwidth=1, relief="solid", width=anchuras.get(columna, 15), 
                bg="yellow", fg="blue", font=("Arial", 12, "bold"), anchor=anchor).grid(row=0, column=i, sticky="ew")
    
    tk.Label(frame_tabla, text="Acciones", borderwidth=1, relief="solid", width=15, 
            bg="yellow", fg="blue", font=("Arial", 12, "bold")).grid(row=0, column=len(columnas), columnspan=2, sticky="ew")
    
    def editar_elemento(idx):
        elemento = cartera[idx]
        ventana_edicion = tk.Toplevel(ventana)
        ventana_edicion.title("Editar elemento")
        
        tk.Label(ventana_edicion, text="Cantidad:").grid(row=0, column=0, padx=10, pady=5)
        entry_cantidad = tk.Entry(ventana_edicion)
        entry_cantidad.insert(0, elemento['cantidad'])
        entry_cantidad.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(ventana_edicion, text="Precio actual:").grid(row=1, column=0, padx=10, pady=5)
        entry_precio = tk.Entry(ventana_edicion)
        entry_precio.insert(0, elemento['precio_actual'])
        entry_precio.grid(row=1, column=1, padx=10, pady=5)
        
        var_dividendos = tk.BooleanVar(value=elemento['dividendos'] == 'Sí')
        tk.Checkbutton(ventana_edicion, text="Tiene dividendos", variable=var_dividendos).grid(row=2, columnspan=2, pady=5)
        
        tk.Label(ventana_edicion, text="Tipo de activo:").grid(row=3, column=0, padx=10, pady=5)
        tipo_var = tk.StringVar(value=elemento.get('tipo_activo', ''))
        tk.OptionMenu(ventana_edicion, tipo_var, 'ACC', 'ETF', 'PP', 'FON').grid(row=3, column=1, padx=10, pady=5)
        
        tk.Label(ventana_edicion, text="Broker:").grid(row=4, column=0, padx=10, pady=5)
        broker_var = tk.StringVar(value=elemento.get('broker', ''))
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
            
            elemento['cantidad'] = int(entry_cantidad.get())
            elemento['precio_actual'] = nuevo_precio
            elemento['dividendos'] = 'Sí' if var_dividendos.get() else 'No'
            elemento['tipo_activo'] = tipo_var.get()
            elemento['broker'] = broker_var.get()
            elemento['importe_total'] = elemento['cantidad'] * elemento['precio_actual']
            
            guardar_cartera(cartera)
            messagebox.showinfo("Éxito", "Elemento editado correctamente.")
            ventana_edicion.destroy()
            ventana.destroy()
            ventana_ver_cartera()
        
        tk.Button(ventana_edicion, text="Guardar", command=guardar_edicion).grid(row=5, columnspan=2, pady=10)
    
    def eliminar_elemento(idx):
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este elemento?"):
            del cartera[idx]
            guardar_cartera(cartera)
            messagebox.showinfo("Éxito", "Elemento eliminado.")
            ventana.destroy()
            ventana_ver_cartera()
    
    # Filas de datos
    for index, row in cartera_df.iterrows():
        tipo_activo = row.get('tipo_activo', '')
        bg_color = {"PP": "#ADD8E6", "FON": "#90EE90", "ETF": "#FFFFE0", "ACC": "#FFDAB9"}.get(tipo_activo, "white")
        
        for i, columna in enumerate(columnas):
            valor = f"{row.get(columna, ''):.2f}" if columna == 'importe_total' else str(row.get(columna, ''))
            anchor = "w" if columna == "título" else "center"
            tk.Label(frame_tabla, text=valor, borderwidth=1, relief="solid", width=anchuras.get(columna, 15), 
                    anchor=anchor, bg=bg_color).grid(row=index + 1, column=i, sticky="ew")
        
        # Encontrar índice original en cartera
        simbolo = row.get('símbolo', '')
        idx_original = next(i for i, item in enumerate(cartera) if item['símbolo'] == simbolo)
        
        tk.Button(frame_tabla, text="Editar", command=lambda idx=idx_original: editar_elemento(idx)).grid(row=index + 1, column=len(columnas), sticky="ew")
        tk.Button(frame_tabla, text="Eliminar", command=lambda idx=idx_original: eliminar_elemento(idx)).grid(row=index + 1, column=len(columnas) + 1, sticky="ew")
    
    frame_tabla.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    # Sumario de totales
    frame_sumario = tk.Frame(ventana)
    frame_sumario.pack(fill=tk.X, padx=10, pady=10)
    
    # Calcular totales
    total_general = sum(item['importe_total'] for item in cartera)
    
    # Totales por tipo
    totales_tipo = {}
    for tipo in ['ACC', 'ETF', 'PP', 'FON']:
        totales_tipo[tipo] = sum(item['importe_total'] for item in cartera if item.get('tipo_activo') == tipo)
    
    # Totales por broker
    totales_broker = {}
    for broker in ['sant', 'cxbank', 'bbva', 'degiro', 'ocean']:
        totales_broker[broker] = sum(item['importe_total'] for item in cartera if item.get('broker') == broker)
    
    # Suma de cantidades por tipo
    cantidad_por_tipo = {}
    for tipo in ['ACC', 'ETF', 'PP', 'FON']:
        cantidad_por_tipo[tipo] = sum(item.get('cantidad', 0) for item in cartera if item.get('tipo_activo') == tipo)

    # Suma de cantidades por broker
    cantidad_por_broker = {}
    for broker in ['sant', 'cxbank', 'bbva', 'degiro', 'ocean']:
        cantidad_por_broker[broker] = sum(item.get('cantidad', 0) for item in cartera if item.get('broker') == broker)

    # Importe total general (grande)
    tk.Label(frame_sumario, text=f"IMPORTE TOTAL: {total_general:.2f}€", 
            font=("Arial", 16, "bold"), fg="red").pack(pady=10)
    
    # Frame para las columnas de totales
    frame_columnas = tk.Frame(frame_sumario)
    frame_columnas.pack()
    
    # Columna izquierda - Totales por tipo
    frame_tipos = tk.LabelFrame(frame_columnas, text="Totales por Tipo", font=("Arial", 12, "bold"))
    frame_tipos.grid(row=0, column=0, padx=10, pady=5, sticky="n")
    
    for tipo, total in totales_tipo.items():
        if total > 0:
            tk.Label(frame_tipos, text=f"{tipo}: {total:.2f}€", font=("Arial", 11)).pack(anchor="w", padx=10, pady=2)
    
    # Columna derecha - Totales por broker
    frame_brokers = tk.LabelFrame(frame_columnas, text="Totales por Broker", font=("Arial", 12, "bold"))
    frame_brokers.grid(row=0, column=1, padx=10, pady=5, sticky="n")
    
    for broker, total in totales_broker.items():
        if total > 0:
            tk.Label(frame_brokers, text=f"{broker}: {total:.2f}€", font=("Arial", 11)).pack(anchor="w", padx=10, pady=2)

    # Panel de activos por tipo
    frame_conteo_tipos = tk.LabelFrame(frame_columnas, text="Activos por Tipo", font=("Arial", 12, "bold"))
    frame_conteo_tipos.grid(row=0, column=2, padx=10, pady=5, sticky="n")
    for tipo, cantidad in cantidad_por_tipo.items():
        if cantidad > 0:
            tk.Label(frame_conteo_tipos, text=f"{tipo}: {cantidad}", font=("Arial", 11)).pack(anchor="w", padx=10, pady=2)

    # Panel de activos por broker
    frame_conteo_brokers = tk.LabelFrame(frame_columnas, text="Activos por Broker", font=("Arial", 12, "bold"))
    frame_conteo_brokers.grid(row=0, column=3, padx=10, pady=5, sticky="n")
    for broker, cantidad in cantidad_por_broker.items():
        if cantidad > 0:
            tk.Label(frame_conteo_brokers, text=f"{broker}: {cantidad}", font=("Arial", 11)).pack(anchor="w", padx=10, pady=2)

def cargar_dividendos():
    try:
        with open("dividendos.json", "r") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return {}

def guardar_dividendos(dividendos):
    with open("dividendos.json", "w") as archivo:
        json.dump(dividendos, archivo, indent=4)

def ventana_dividendos():
    ventana = tk.Toplevel()
    ventana.title("Dividendos")
    ventana.geometry("1200x800")
    
    cartera = cargar_cartera()
    activos_con_dividendos = [item for item in cartera if item.get('dividendos') == 'Sí']
    
    if not activos_con_dividendos:
        tk.Label(ventana, text="No hay activos con dividendos.", font=("Arial", 14)).pack(pady=50)
        return
    
    dividendos_data = cargar_dividendos()
    
    # Notebook para las pestañas de años
    from tkinter import ttk
    notebook = ttk.Notebook(ventana)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    def crear_tabla_ano(ano):
        frame_ano = tk.Frame(notebook)
        notebook.add(frame_ano, text=str(ano))
        
        # Frame con scroll
        canvas = tk.Canvas(frame_ano)
        scrollbar = tk.Scrollbar(frame_ano, orient="vertical", command=canvas.yview)
        frame_tabla = tk.Frame(canvas)
        
        canvas.create_window((0, 0), window=frame_tabla, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Encabezados
        tk.Label(frame_tabla, text="Activo", borderwidth=1, relief="solid", width=15, 
                bg="yellow", fg="blue", font=("Arial", 10, "bold")).grid(row=0, column=0)
        
        for i, mes in enumerate(meses):
            tk.Label(frame_tabla, text=mes, borderwidth=1, relief="solid", width=8, 
                    bg="yellow", fg="blue", font=("Arial", 10, "bold")).grid(row=0, column=i+1)
        
        tk.Label(frame_tabla, text="Total", borderwidth=1, relief="solid", width=10, 
                bg="orange", fg="blue", font=("Arial", 10, "bold")).grid(row=0, column=13)
        
        entries = {}
        totales_fila = {}
        totales_mes = [tk.StringVar() for _ in range(12)]
        total_general = tk.StringVar()
        
        def actualizar_totales():
            # Totales por mes
            for mes_idx in range(12):
                total_mes = 0
                for activo in activos_con_dividendos:
                    simbolo = activo['símbolo']
                    try:
                        valor = float(entries[simbolo][mes_idx].get() or 0)
                        total_mes += valor
                    except ValueError:
                        pass
                totales_mes[mes_idx].set(f"{total_mes:.2f}")
            
            # Totales por fila y general
            total_gral = 0
            for activo in activos_con_dividendos:
                simbolo = activo['símbolo']
                total_fila = 0
                for mes_idx in range(12):
                    try:
                        valor = float(entries[simbolo][mes_idx].get() or 0)
                        total_fila += valor
                    except ValueError:
                        pass
                totales_fila[simbolo].set(f"{total_fila:.2f}")
                total_gral += total_fila
            
            total_general.set(f"{total_gral:.2f}")
            
            # Guardar datos
            if str(ano) not in dividendos_data:
                dividendos_data[str(ano)] = {}
            for activo in activos_con_dividendos:
                simbolo = activo['símbolo']
                dividendos_data[str(ano)][simbolo] = [entry.get() for entry in entries[simbolo]]
            guardar_dividendos(dividendos_data)
            actualizar_sumario()
        
        # Filas de activos
        for index, activo in enumerate(activos_con_dividendos):
            simbolo = activo['símbolo']
            tk.Label(frame_tabla, text=simbolo, borderwidth=1, relief="solid", width=15, 
                    anchor="w").grid(row=index+1, column=0)
            
            entries[simbolo] = []
            totales_fila[simbolo] = tk.StringVar()
            
            # Campos editables para cada mes
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
            
            # Total de fila (no editable)
            tk.Label(frame_tabla, textvariable=totales_fila[simbolo], borderwidth=1, relief="solid", 
                    width=10, anchor="center", bg="lightgray").grid(row=index+1, column=13)
        
        # Fila de totales por mes
        tk.Label(frame_tabla, text="TOTAL", borderwidth=1, relief="solid", width=15, 
                bg="orange", fg="blue", font=("Arial", 10, "bold")).grid(row=len(activos_con_dividendos)+1, column=0)
        
        for mes_idx in range(12):
            tk.Label(frame_tabla, textvariable=totales_mes[mes_idx], borderwidth=1, relief="solid", 
                    width=8, anchor="center", bg="lightgray", font=("Arial", 10, "bold")).grid(row=len(activos_con_dividendos)+1, column=mes_idx+1)
        
        tk.Label(frame_tabla, textvariable=total_general, borderwidth=1, relief="solid", 
                width=10, anchor="center", bg="orange", font=("Arial", 10, "bold")).grid(row=len(activos_con_dividendos)+1, column=13)
        
        actualizar_totales()
        frame_tabla.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    # Sumario de totales
    frame_sumario = tk.Frame(ventana)
    frame_sumario.pack(fill=tk.X, padx=10, pady=10)
    
    totales_anos = {}
    total_todos_anos = tk.StringVar()
    
    def actualizar_sumario():
        dividendos_data = cargar_dividendos()
        total_general = 0
        
        for ano in [2022, 2023, 2024, 2025]:
            total_ano = 0
            if str(ano) in dividendos_data:
                for simbolo, valores in dividendos_data[str(ano)].items():
                    for valor in valores:
                        try:
                            total_ano += float(valor or 0)
                        except ValueError:
                            pass
            totales_anos[ano].set(f"{ano}: {total_ano:.2f}€")
            total_general += total_ano
        
        total_todos_anos.set(f"TOTAL TODOS LOS AÑOS: {total_general:.2f}€")
    
    # Labels para totales por año
    for ano in [2022, 2023, 2024, 2025]:
        totales_anos[ano] = tk.StringVar()
        tk.Label(frame_sumario, textvariable=totales_anos[ano], font=("Arial", 14, "bold")).pack(anchor="w")
    
    # Total general
    tk.Label(frame_sumario, textvariable=total_todos_anos, font=("Arial", 16, "bold"), fg="red").pack(pady=10)
    
    # Crear tablas para cada año
    for ano in [2022, 2023, 2024, 2025]:
        crear_tabla_ano(ano)
    
    actualizar_sumario()

def iniciar_gui():
    root = tk.Tk()
    root.title("Gestor de Cartera AAF")
    root.geometry("400x300")
    
    # Título principal
    tk.Label(root, text="Gestor de Cartera AAF", font=("Arial", 18, "bold")).pack(pady=30)
    
    # Botones principales
    tk.Button(root, text="Añadir Nuevos Activos", command=ventana_agregar_activos, 
             width=25, height=2, font=("Arial", 12), bg="lightblue").pack(pady=10)
    
    tk.Button(root, text="Ver Cartera", command=ventana_ver_cartera, 
             width=25, height=2, font=("Arial", 12), bg="lightgreen").pack(pady=10)
    
    tk.Button(root, text="Ver Dividendos", command=ventana_dividendos, 
             width=25, height=2, font=("Arial", 12), bg="lightyellow").pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    iniciar_gui()