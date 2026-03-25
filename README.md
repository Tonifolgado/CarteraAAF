# Gestor de Cartera AAF

**Gestor de Cartera AAF** es una aplicación de escritorio desarrollada en Python para facilitar la gestión, seguimiento y análisis de tu cartera de inversiones personal y el cobro de dividendos.

## Estructura de Ficheros

El proyecto ha evolucionado a una arquitectura modular, separando la interfaz gráfica, la lógica de negocio, los modelos de datos y los servicios externos:

*   **`data/`**: Carpeta que contiene los datos persistentes de la aplicación.
    *   `cartera.json`: Archivo JSON con la lista y detalles de los activos de la cartera.
    *   `dividendos.json`: Archivo JSON que almacena el historial de dividendos cobrados por año y mes.
*   **`gui/`**: Contiene la lógica de la interfaz visual.
    *   `main_window.py`: Define la interfaz gráfica de usuario (GUI) principal y sus vistas usando `Tkinter`.
*   **`models/`**: Contiene las clases que representan la lógica de negocio.
    *   `asset.py`: Define la clase `Asset` (activo financiero y sus propiedades).
    *   `portfolio.py`: Define la clase `Portfolio`, encargada de interactuar con el archivo JSON y manejar las operaciones de la cartera.
*   **`services/`**: Contiene los servicios de conexión externa.
    *   `market_data.py`: Módulo de conexión con la API de Yahoo Finance (`yfinance`) para obtener precios actuales del mercado en tiempo real.
*   **`gestor_cartera.py`**: Script principal (entry point) que inicializa y arranca la aplicación.

## Lógica del Código

El código está organizado para separar responsabilidades (Separation of Concerns):

1.  **Modelos (`models/`)**: La clase `Asset` se utiliza para representar posiciones financieras en memoria. `Portfolio` agrupa estos activos, proveyendo métodos para añadir, editar, eliminar (CRUD) y guardarlos transparentemente en `cartera.json`.
2.  **Interfaz Gráfica (`gui/main_window.py`)**: Construida de forma nativa con **Tkinter**. Esta capa captura los inputs del usuario y delega el procesamiento de la información a la clase `Portfolio`. Utiliza **Pandas** para convertir los datos de los activos en un DataFrame, ordenarlos y agruparlos antes de renderizarlos en la tabla principal. Asimismo, usa **Matplotlib** para dibujar de manera integrada los gráficos de barras y distribución sectorial (tarta).
3.  **Servicios (`services/market_data.py`)**: Centraliza la obtención de precios del mercado de valores con la librería `yfinance`, previniendo que la interfaz gráfica realice peticiones HTTP directamente y centralizando el manejo de errores.
4.  **Persistencia de Datos**: Se ha optado por utilizar archivos JSON estáticos (`cartera.json` y `dividendos.json`). Los dividendos se actualizan y calculan automáticamente año tras año (2022-2026) a través de los eventos de la interfaz, grabando las entradas a disco bajo demanda.

## Cómo Usar la Aplicación

### 1. Requisitos e Instalación
Necesitas tener Python 3 instalado en tu sistema. Instala las dependencias necesarias mediante pip:
```bash
pip install pandas yfinance matplotlib
```

### 2. Ejecutar la Aplicación
Inicia la aplicación ejecutando el script principal que lanza la interfaz. Asegúrate de ejecutarlo desde el directorio raíz del proyecto para que las rutas relativas (como la lectura de `data/cartera.json`) funcionen correctamente:
```bash
python -c "from gui.main_window import iniciar_gui; iniciar_gui()"
```
*(Si dispones de un script `main.py` en la raíz del proyecto para inicializar la app, también puedes ejecutar directamente `python main.py`)*

### 3. Funcionalidades Principales
*   **Añadir Nuevos Activos**: Al añadir un nuevo activo, rellena el símbolo del ticker (ej. `AAPL` o `IBE.MC`). El sistema contactará automáticamente a Yahoo Finance para recuperar su precio actual.
*   **Ver Cartera**: Abre un dashboard interactivo. Podrás revisar el total invertido, el peso de cada activo (%) y resúmenes financieros apoyados por gráficas dinámicas. Desde la propia tabla puedes "Editar" o "Eliminar" posiciones.
*   **Ver Dividendos**: Utiliza un sistema de pestañas por año (2022-2026). Registra mes a mes los cobros introduciendo el importe en las celdas (que se pintarán de verde). Todo se suma y consolida de forma automática en la pestaña general de "Resumen".
```