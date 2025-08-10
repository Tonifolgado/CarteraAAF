import pandas as pd
import yfinance as yf
from tabulate import tabulate
import tkinter as tk
from tkinter import messagebox
import json

# Ruta del archivo para persistir los datos
CARPETA_ARCHIVO = "cartera.json"

def obtener_precios_actuales(simbolos):
    """
    Obtiene los precios actuales para una lista de símbolos (tickers).
    Args:simbolos: Una lista de strings con los símbolos de los activos.
    Returns:Un diccionario mapeando cada símbolo a su precio actual (float).
    """
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
def mostrar_cartera(df):
    """
    Muestra la cartera en un formato de tabla.

    Args:
        df: El DataFrame que contiene los datos a mostrar.
    """
    if df.empty:
        print("\n--- Cartera ---")
        print("No hay activos en la cartera.")
        return

    df_display = df.copy()
    df_display['precio_actual'] = df_display['precio_actual'].map('€{:.2f}'.format)
    df_display['importe_total'] = df_display['importe_total'].map('€{:.2f}'.format)

    print("\n--- Cartera ---")
    print(tabulate(df_display, headers='keys', tablefmt='psql', showindex=False))

def cargar_cartera():
    """Carga la cartera desde un archivo JSON."""
    try:
        with open(CARPETA_ARCHIVO, "r") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def guardar_cartera(cartera):
    """Guarda la cartera en un archivo JSON."""
    with open(CARPETA_ARCHIVO, "w") as archivo:
        json.dump(cartera, archivo, indent=4)

def iniciar_gui():
    """Inicia la interfaz gráfica de usuario."""
    cartera = cargar_cartera()

    def actualizar_tabla():
        for widget in frame_tabla.winfo_children():
            widget.destroy()

        if not cartera:
            tk.Label(frame_tabla, text="No hay elementos en la cartera.").pack()
            return

        cartera_df = pd.DataFrame(cartera)
        # Ordenar por tipo de activo y luego por símbolo
        orden_tipos = {'ACC': 0, 'ETF': 1, 'PP': 2, 'FON': 3}
        cartera_df['orden_tipo'] = cartera_df['tipo_activo'].map(orden_tipos)
        cartera_df = cartera_df.sort_values(['orden_tipo', 'símbolo']).drop('orden_tipo', axis=1)
        columnas = ['símbolo', 'título', 'cantidad', 'precio_actual', 'importe_total', 'dividendos', 'tipo_activo']

        # Crear encabezados de la tabla
        anchuras = {
            "símbolo": 10,
            "título": 25,
            "cantidad": 8,
            "precio_actual": 12,
            "importe_total": 12,
            "dividendos": 10,
            "tipo_activo": 8
        }
        
        for i, columna in enumerate(columnas):
            anchor = "w" if columna == "título" else "center"
            width = anchuras.get(columna, 15)
            tk.Label(frame_tabla, text=columna, borderwidth=1, relief="solid", width=width, 
                    bg="yellow", fg="blue", font=("Arial", 12, "bold"), anchor=anchor).grid(row=0, column=i, sticky="ew")

        # Crear filas de la tabla
        for index, row in cartera_df.iterrows():
            # Determinar el color de fondo según el tipo de activo
            tipo_activo = row.get('tipo_activo', '')
            if tipo_activo == 'PP':
                bg_color = "#ADD8E6"
            elif tipo_activo == 'FON':
                bg_color = "#90EE90"
            elif tipo_activo == 'ETF':
                bg_color = "#FFFFE0"
            elif tipo_activo == 'ACC':
                bg_color = "#FFDAB9"
            else:
                bg_color = "white"

            for i, columna in enumerate(columnas):
                valor = row.get(columna, '')
                if columna == 'importe_total':
                    valor = f"{valor:.2f}"
                anchor = "w" if columna == "título" else "center"
                width = anchuras.get(columna, 15)
                tk.Label(frame_tabla, text=str(valor), borderwidth=1, relief="solid", width=width, 
                        anchor=anchor, bg=bg_color).grid(row=index + 1, column=i, sticky="ew")

            # Botones de acción
            tk.Button(frame_tabla, text="Editar", command=lambda idx=index: editar_elemento(idx)).grid(row=index + 1, column=len(columnas), sticky="ew")
            
            def eliminar_elemento(idx):
                del cartera[idx]
                guardar_cartera(cartera)
                actualizar_tabla()

            tk.Button(frame_tabla, text="Eliminar", command=lambda idx=index: eliminar_elemento(idx)).grid(row=index + 1, column=len(columnas) + 1, sticky="ew")

        # Configurar el ancho de las columnas
        for i, columna in enumerate(columnas):
            frame_tabla.grid_columnconfigure(i, weight=0, minsize=anchuras.get(columna, 15) * 8)

        # Calcular totales
        total_cantidad_acc = sum(item['cantidad'] for item in cartera if item.get('tipo_activo') == 'ACC')
        total_cantidad_etf = sum(item['cantidad'] for item in cartera if item.get('tipo_activo') == 'ETF')
        total_cantidad_pp = sum(item['cantidad'] for item in cartera if item.get('tipo_activo') == 'PP')
        total_cantidad_fon = sum(item['cantidad'] for item in cartera if item.get('tipo_activo') == 'FON')
        total_importe_etf = sum(item['importe_total'] for item in cartera if item.get('tipo_activo') == 'ETF')
        total_importe_pp = sum(item['importe_total'] for item in cartera if item.get('tipo_activo') == 'PP')
        total_importe_acc = sum(item['importe_total'] for item in cartera if item.get('tipo_activo') == 'ACC')
        total_importe_fon = sum(item['importe_total'] for item in cartera if item.get('tipo_activo') == 'FON')
        total_importe_todos = sum(item['importe_total'] for item in cartera)

        # Mostrar totales debajo de la tabla
        for widget in totales_frame.winfo_children():
            widget.destroy()

        # Crear marco para las dos columnas
        columnas_totales = tk.Frame(totales_frame)
        columnas_totales.pack(anchor="w", pady=10)

        # Columna de cantidades
        columna_cantidades = tk.Frame(columnas_totales)
        columna_cantidades.grid(row=0, column=0, padx=10)
        tk.Label(columna_cantidades, text="Cantidades", font=("Arial", 12, "bold")).pack(anchor="w")
        tk.Label(columna_cantidades, text=f"ACC: {total_cantidad_acc}").pack(anchor="w")
        tk.Label(columna_cantidades, text=f"ETF: {total_cantidad_etf}").pack(anchor="w")
        tk.Label(columna_cantidades, text=f"PP: {total_cantidad_pp}").pack(anchor="w")
        tk.Label(columna_cantidades, text=f"FON: {total_cantidad_fon}").pack(anchor="w")

        # Columna de importes
        columna_importes = tk.Frame(columnas_totales)
        columna_importes.grid(row=0, column=1, padx=10)
        tk.Label(columna_importes, text="Importes", font=("Arial", 12, "bold")).pack(anchor="w")
        tk.Label(columna_importes, text=f"ACC: {total_importe_acc:.2f}€").pack(anchor="w")
        tk.Label(columna_importes, text=f"ETF: {total_importe_etf:.2f}€").pack(anchor="w")
        tk.Label(columna_importes, text=f"PP: {total_importe_pp:.2f}€").pack(anchor="w")
        tk.Label(columna_importes, text=f"FON: {total_importe_fon:.2f}€").pack(anchor="w")

        # Mostrar cantidad total de activos e importe total
        tk.Label(totales_frame, text=f"Cantidad total de activos: {total_cantidad_acc + total_cantidad_etf + total_cantidad_pp + total_cantidad_fon}", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        tk.Label(totales_frame, text=f"Importe total de todos los activos: {total_importe_todos:.2f}€", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)

    def editar_elemento(idx):
        elemento = cartera[idx]

        # Crear ventana de edición
        ventana_edicion = tk.Toplevel(root)
        ventana_edicion.title("Editar elemento")

        tk.Label(ventana_edicion, text="Cantidad:").grid(row=0, column=0, padx=10, pady=5)
        entry_cantidad_edicion = tk.Entry(ventana_edicion)
        entry_cantidad_edicion.insert(0, elemento['cantidad'])
        entry_cantidad_edicion.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(ventana_edicion, text="Precio actual:").grid(row=1, column=0, padx=10, pady=5)
        entry_precio_actual_edicion = tk.Entry(ventana_edicion)
        entry_precio_actual_edicion.insert(0, elemento['precio_actual'])
        entry_precio_actual_edicion.grid(row=1, column=1, padx=10, pady=5)

        var_dividendos_edicion = tk.BooleanVar(value=elemento['dividendos'] == 'Sí')
        tk.Checkbutton(ventana_edicion, text="Tiene dividendos", variable=var_dividendos_edicion).grid(row=2, columnspan=2, pady=5)

        tk.Label(ventana_edicion, text="Tipo de activo:").grid(row=3, column=0, padx=10, pady=5)
        tipo_activo_var_edicion = tk.StringVar(value=elemento.get('tipo_activo', ''))
        tipo_activo_combobox_edicion = tk.OptionMenu(ventana_edicion, tipo_activo_var_edicion, 'ACC', 'ETF', 'PP', 'FON')
        tipo_activo_combobox_edicion.grid(row=3, column=1, padx=10, pady=5)

        def guardar_edicion():
            nueva_cantidad = entry_cantidad_edicion.get().strip()
            nuevo_precio_actual = entry_precio_actual_edicion.get().strip()

            if not nueva_cantidad.isdigit():
                messagebox.showerror("Error", "La cantidad debe ser un número entero válido.")
                return

            try:
                nuevo_precio_actual = float(nuevo_precio_actual)
            except ValueError:
                messagebox.showerror("Error", "El precio actual debe ser un número válido.")
                return

            elemento['cantidad'] = int(nueva_cantidad)
            elemento['precio_actual'] = nuevo_precio_actual
            elemento['dividendos'] = 'Sí' if var_dividendos_edicion.get() else 'No'
            elemento['tipo_activo'] = tipo_activo_var_edicion.get()
            elemento['importe_total'] = elemento['cantidad'] * elemento['precio_actual']

            guardar_cartera(cartera)
            messagebox.showinfo("Éxito", "Elemento editado correctamente.")
            ventana_edicion.destroy()
            actualizar_tabla()

        tk.Button(ventana_edicion, text="Guardar", command=guardar_edicion).grid(row=4, columnspan=2, pady=10)

    def agregar_elemento(tipo_activo):
        simbolo = entry_simbolo.get().strip()
        titulo = entry_titulo.get().strip()
        cantidad = entry_cantidad.get().strip()
        tiene_dividendos = var_dividendos.get()
        precio_manual = entry_precio_manual.get().strip()

        # Validar que los campos obligatorios no estén vacíos
        if not simbolo:
            messagebox.showerror("Error", "El campo 'Símbolo' no puede estar vacío.")
            return

        if not titulo:
            messagebox.showerror("Error", "El campo 'Título' no puede estar vacío.")
            return

        if not cantidad.isdigit():
            messagebox.showerror("Error", "El campo 'Cantidad' debe ser un número entero válido.")
            return

        cantidad = int(cantidad)
        precios_actuales = obtener_precios_actuales([simbolo])
        precio_actual = precios_actuales.get(simbolo, 0.0)

        # Validar el precio manual si el precio automático no se encuentra
        if precio_actual == 0.0:
            if not precio_manual:
                messagebox.showerror("Error", "El precio no se encontró y no se ingresó manualmente.")
                return
            try:
                precio_actual = float(precio_manual)
            except ValueError:
                messagebox.showerror("Error", "El precio ingresado manualmente no es válido.")
                return

        importe_total = cantidad * precio_actual

        cartera.append({
            'símbolo': simbolo,
            'título': titulo,
            'cantidad': cantidad,
            'precio_actual': precio_actual,
            'importe_total': importe_total,
            'dividendos': 'Sí' if tiene_dividendos else 'No',
            'tipo_activo': tipo_activo
        })

        guardar_cartera(cartera)
        messagebox.showinfo("Éxito", "Elemento añadido a la cartera.")
        entry_simbolo.delete(0, tk.END)
        entry_titulo.delete(0, tk.END)
        entry_cantidad.delete(0, tk.END)
        entry_precio_manual.delete(0, tk.END)
        var_dividendos.set(False)
        tipo_activo_var.set('')
        actualizar_tabla()

    root = tk.Tk()
    root.title("Gestor de Cartera")
    root.geometry("1200x800")
    
    # Frame principal con scroll
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Frame para los campos de entrada (siempre visible)
    entrada_frame = tk.LabelFrame(main_frame, text="Agregar Nuevo Activo", font=("Arial", 12, "bold"))
    entrada_frame.pack(fill=tk.X, pady=(0, 10))
    
    # Campos de entrada en una cuadrícula más compacta
    tk.Label(entrada_frame, text="Símbolo:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_simbolo = tk.Entry(entrada_frame, width=15)
    entry_simbolo.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(entrada_frame, text="Título:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
    entry_titulo = tk.Entry(entrada_frame, width=20)
    entry_titulo.grid(row=0, column=3, padx=5, pady=5)
    
    tk.Label(entrada_frame, text="Cantidad:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_cantidad = tk.Entry(entrada_frame, width=15)
    entry_cantidad.grid(row=1, column=1, padx=5, pady=5)
    
    tk.Label(entrada_frame, text="Precio manual:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
    entry_precio_manual = tk.Entry(entrada_frame, width=15)
    entry_precio_manual.grid(row=1, column=3, padx=5, pady=5)
    
    tk.Label(entrada_frame, text="Tipo:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    tipo_activo_var = tk.StringVar()
    tipo_activo_combobox = tk.OptionMenu(entrada_frame, tipo_activo_var, 'ACC', 'ETF', 'PP', 'FON')
    tipo_activo_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    
    var_dividendos = tk.BooleanVar()
    tk.Checkbutton(entrada_frame, text="Dividendos", variable=var_dividendos).grid(row=2, column=2, padx=5, pady=5)
    
    tk.Button(entrada_frame, text="Agregar", command=lambda: agregar_elemento(tipo_activo_var.get()), 
              bg="green", fg="white", font=("Arial", 10, "bold")).grid(row=2, column=3, padx=5, pady=5)
    
    # Frame para la tabla con scroll
    tabla_frame = tk.LabelFrame(main_frame, text="Cartera de Inversiones", font=("Arial", 12, "bold"))
    tabla_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    # Canvas y scrollbar para la tabla
    canvas_tabla = tk.Canvas(tabla_frame)
    scrollbar_v = tk.Scrollbar(tabla_frame, orient="vertical", command=canvas_tabla.yview)
    scrollbar_h = tk.Scrollbar(tabla_frame, orient="horizontal", command=canvas_tabla.xview)
    
    frame_tabla = tk.Frame(canvas_tabla)
    
    canvas_tabla.create_window((0, 0), window=frame_tabla, anchor="nw")
    canvas_tabla.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
    
    canvas_tabla.pack(side="left", fill="both", expand=True)
    scrollbar_v.pack(side="right", fill="y")
    scrollbar_h.pack(side="bottom", fill="x")
    
    def configurar_scroll(event):
        canvas_tabla.configure(scrollregion=canvas_tabla.bbox("all"))
    
    frame_tabla.bind("<Configure>", configurar_scroll)
    
    # Frame para totales (siempre visible)
    totales_frame = tk.LabelFrame(main_frame, text="Resumen", font=("Arial", 12, "bold"))
    totales_frame.pack(fill=tk.X)
    
    actualizar_tabla()
    root.mainloop()

if __name__ == "__main__":
    iniciar_gui()