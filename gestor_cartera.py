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
        columnas = ['símbolo', 'título', 'cantidad', 'precio_actual', 'importe_total', 'dividendos', 'tipo_activo']
        tipos_disponibles = ['ACC', 'ETF', 'PP', 'FON']

        # Crear encabezados de la tabla
        encabezados = tk.Frame(frame_tabla)
        encabezados.grid(row=0, column=0, columnspan=len(columnas), sticky="nsew")
        anchuras = {
            "cantidad": 5,
            "precio_actual": 10,
            "importe_total": 12,
            "dividendos": 4,
            "tipo_activo": 5
        }
        for i, columna in enumerate(columnas):
            anchor = "w" if columna == "título" else "center"  # Alinear título a la izquierda
            width = anchuras.get(columna, 15)  # Usar anchura especificada o valor por defecto
            tk.Label(encabezados, text=columna, borderwidth=1, relief="solid", width=width, bg="yellow", fg="blue", font=("Arial", 12, "bold"), anchor=anchor).grid(row=0, column=i, sticky="nsew")

        # Crear filas de la tabla
        for index, row in cartera_df.iterrows():
            fila = tk.Frame(frame_tabla)
            fila.grid(row=index + 1, column=0, columnspan=len(columnas), sticky="nsew")

            # Determinar el color de fondo según el tipo de activo
            tipo_activo = row.get('tipo_activo', '')
            if tipo_activo == 'PP':
                bg_color = "#ADD8E6"  # Azul pálido
            elif tipo_activo == 'FON':
                bg_color = "#90EE90"  # Verde pálido
            elif tipo_activo == 'ETF':
                bg_color = "#FFFFE0"  # Amarillo
            elif tipo_activo == 'ACC':
                bg_color = "#FFDAB9"  # Naranja pálido
            else:
                bg_color = "white"  # Color por defecto

            for i, columna in enumerate(columnas):
                valor = row.get(columna, '')
                if columna == 'importe_total':
                    valor = f"{valor:.2f}"  # Formatear importe total con dos decimales
                anchor = "w" if columna == "título" else "center"  # Alinear título a la izquierda
                width = anchuras.get(columna, 15)  # Usar anchura especificada o valor por defecto
                tk.Label(fila, text=str(valor), borderwidth=1, relief="solid", width=width, anchor=anchor, bg=bg_color).grid(row=0, column=i, sticky="nsew")

            # Eliminar edición directa de tipo_activo
            tipo_activo_var = tk.StringVar(value=row.get('tipo_activo', ''))
            tk.Label(fila, text=tipo_activo_var.get(), borderwidth=1, relief="solid", width=15, anchor="center", bg=bg_color).grid(row=0, column=6, sticky="nsew")

            tk.Button(fila, text="Editar", command=lambda idx=index: editar_elemento(idx)).grid(row=0, column=7, sticky="nsew")

            # Botón para eliminar el elemento
            def eliminar_elemento(idx):
                del cartera[idx]
                guardar_cartera(cartera)
                actualizar_tabla()

            tk.Button(fila, text="Eliminar", command=lambda idx=index: eliminar_elemento(idx)).grid(row=0, column=8, sticky="nsew")

        # Ajustar el ancho de las columnas al contenido
        for i, columna in enumerate(columnas):
            max_width = max(len(str(row.get(columna, ''))) for row in cartera)
            frame_tabla.grid_columnconfigure(i, minsize=max_width * 10)  # Multiplicar por un factor para ajustar el ancho visual

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
    root.geometry("1024x768")  # Establecer un tamaño inicial más amplio para mostrar más contenido
    root.update_idletasks()  # Actualizar la ventana para ajustar el contenido

    def ajustar_tamano_ventana(event):
        canvas_principal.configure(scrollregion=canvas_principal.bbox("all"))

    root.bind("<Configure>", ajustar_tamano_ventana)

    # Configurar el canvas principal para que se expanda con la ventana
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Crear un canvas con barra de desplazamiento para la ventana principal
    canvas_principal = tk.Canvas(root)
    canvas_principal.grid(row=0, column=0, columnspan=3, sticky="nsew")

    scrollbar_principal = tk.Scrollbar(root, orient="vertical", command=canvas_principal.yview)
    scrollbar_principal.grid(row=0, column=3, sticky="ns")

    canvas_principal.configure(yscrollcommand=scrollbar_principal.set)

    frame_principal = tk.Frame(canvas_principal)
    canvas_principal.create_window((0, 0), window=frame_principal, anchor="nw")

    def ajustar_scroll_principal(event):
        canvas_principal.configure(scrollregion=canvas_principal.bbox("all"))

    frame_principal.bind("<Configure>", ajustar_scroll_principal)

    # Mover los widgets al frame principal
    tk.Label(frame_principal, text="Símbolo:").grid(row=0, column=0, padx=10, pady=5)
    entry_simbolo = tk.Entry(frame_principal)
    entry_simbolo.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(frame_principal, text="Título:").grid(row=1, column=0, padx=10, pady=5)
    entry_titulo = tk.Entry(frame_principal)
    entry_titulo.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(frame_principal, text="Cantidad:").grid(row=2, column=0, padx=10, pady=5)
    entry_cantidad = tk.Entry(frame_principal)
    entry_cantidad.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(frame_principal, text="Precio manual (opcional):").grid(row=3, column=0, padx=10, pady=5)
    entry_precio_manual = tk.Entry(frame_principal)
    entry_precio_manual.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(frame_principal, text="Tipo de activo:").grid(row=4, column=0, padx=10, pady=5)
    tipo_activo_var = tk.StringVar()
    tipo_activo_combobox = tk.OptionMenu(frame_principal, tipo_activo_var, 'ACC', 'ETF', 'PP', 'FON')
    tipo_activo_combobox.grid(row=4, column=1, padx=10, pady=5)

    var_dividendos = tk.BooleanVar()
    tk.Checkbutton(frame_principal, text="Tiene dividendos", variable=var_dividendos).grid(row=5, columnspan=2, pady=5)

    tk.Button(frame_principal, text="Agregar elemento", command=lambda: agregar_elemento(tipo_activo_var.get())).grid(row=6, column=0, padx=10, pady=10)

    canvas_tabla = tk.Canvas(frame_principal)
    canvas_tabla.grid(row=7, column=0, columnspan=2, sticky="nsew")

    scrollbar_tabla = tk.Scrollbar(frame_principal, orient="vertical", command=canvas_tabla.yview)
    scrollbar_tabla.grid(row=7, column=2, sticky="ns")

    canvas_tabla.configure(yscrollcommand=scrollbar_tabla.set)

    frame_tabla = tk.Frame(canvas_tabla)
    canvas_tabla.create_window((0, 0), window=frame_tabla, anchor="nw")

    # Crear barra de desplazamiento horizontal para la tabla
    scrollbar_horizontal_tabla = tk.Scrollbar(frame_principal, orient="horizontal", command=canvas_tabla.xview)
    scrollbar_horizontal_tabla.grid(row=8, column=0, columnspan=2, sticky="ew")

    canvas_tabla.configure(xscrollcommand=scrollbar_horizontal_tabla.set)

    def ajustar_scroll_tabla(event):
        canvas_tabla.configure(scrollregion=canvas_tabla.bbox("all"))

    frame_tabla.bind("<Configure>", ajustar_scroll_tabla)

    totales_frame = tk.Frame(frame_principal)
    totales_frame.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

    actualizar_tabla()

    # Ajustar el tamaño inicial del canvas para que todas las filas sean visibles
    def ajustar_tamano_inicial():
        canvas_tabla.update_idletasks()
        ancho_total = sum(widget.winfo_width() for widget in frame_tabla.winfo_children())
        alto_total = frame_tabla.winfo_height()
        canvas_tabla.configure(width=ancho_total, height=alto_total)

    ajustar_tamano_inicial()

    # Asegurar que los valores totales sean visibles
    totales_frame.grid(row=10, column=0, columnspan=2, padx=10, pady=10)

    # Asegurar que los campos de entrada sean visibles
    frame_principal.grid_rowconfigure(0, weight=0)
    frame_principal.grid_rowconfigure(1, weight=0)
    frame_principal.grid_rowconfigure(2, weight=0)
    frame_principal.grid_rowconfigure(3, weight=0)
    frame_principal.grid_rowconfigure(4, weight=0)
    frame_principal.grid_rowconfigure(5, weight=0)

    # Asegurar que el resumen sea visible
    totales_frame.grid(row=11, column=0, columnspan=2, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    iniciar_gui()