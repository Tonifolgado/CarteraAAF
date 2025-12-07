# Gestor de Cartera AAF

**Gestor de Cartera AAF** is a desktop application developed in Python that allows for the management and tracking of a personal investment portfolio. It provides a graphical user interface (GUI) to easily add, view, and manage financial assets, as well as track dividend income.

## Features

*   **Add New Assets**: A dedicated window to add new assets to the portfolio, specifying details like ticker symbol, quantity, asset type, and broker.
*   **View Portfolio**: A comprehensive dashboard that displays all assets in a detailed table. It includes:
    *   Real-time price updates fetched from Yahoo Finance.
    *   Calculation of total value per asset and for the entire portfolio.
    *   Summaries of total investment amounts grouped by asset type and broker.
    *   A pie chart showing the portfolio's distribution by asset type.
*   **Edit and Delete Assets**: Functionality to modify the quantity, price, or other attributes of an asset, or to remove it completely from the portfolio.
*   **Dividend Tracking**: A sophisticated multi-tab interface to record and review dividend income. It includes:
    *   Separate, editable tables for each year (2022-2025) to log monthly dividends per asset.
    *   An auto-calculated summary tab that shows total dividends per asset and per year.
*   **Data Persistence**: The portfolio and dividend data are saved locally in `cartera.json` and `dividendos.json` files, ensuring the information is retained between sessions.

## Technologies Used

*   **Python 3**: The core programming language.
*   **Tkinter**: Used for building the graphical user interface.
*   **Pandas**: For data manipulation and structuring, especially in the portfolio view.
*   **yfinance**: To fetch real-time stock market data.
*   **Matplotlib**: For generating the portfolio distribution pie chart.

## File Structure

```
├── gestor_cartera.py   # Main application script containing all the logic and UI.
├── cartera.json        # Database file storing the list of portfolio assets.
└── dividendos.json     # Database file storing dividend income data by year.
```

## Setup and Installation

1.  **Prerequisites**: Make sure you have Python 3 installed on your system.

2.  **Clone the Repository (Optional)**: If the project is in a Git repository, you can clone it:
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

3.  **Install Dependencies**: Open a terminal or command prompt and install the required Python libraries using pip.
    ```bash
    pip install pandas yfinance matplotlib
    ```

## How to Run the Application

To start the application, navigate to the directory containing the `gestor_cartera.py` file and run the following command in your terminal:

```bash
python gestor_cartera.py
```

This will launch the main window of the application.

## Application Modules Explained

The application is contained within a single script, `gestor_cartera.py`, which includes several key functions:

### Main GUI Functions

*   `iniciar_gui()`: This is the entry point of the application. It creates the main window with buttons to access the different functionalities ("Añadir Nuevos Activos", "Ver Cartera", "Ver Dividendos").

*   `ventana_agregar_activos()`: Opens a new window with a form to add a new asset. It captures the symbol, title, quantity, type, broker, and whether it pays dividends. It uses `yfinance` to fetch the current price automatically but also allows for manual price entry if the fetch fails.

*   `ventana_ver_cartera()`: This is the core view of the application. It displays:
    *   A detailed table of all assets, sorted by type. Each row shows the symbol, title, quantity, current price, total value, and its percentage of the total portfolio.
    *   Buttons to **Edit** or **Delete** each asset. Editing allows you to update quantity, price, and other attributes.
    *   Summary panels that show the total portfolio value, as well as subtotals by asset type and broker.
    *   A Matplotlib pie chart visualizing the distribution of assets by type.

*   `ventana_dividendos()`: Opens a window dedicated to dividend management.
    *   It uses a `ttk.Notebook` to create tabs.
    *   **Yearly Tabs (2022-2025)**: Each tab contains an editable grid where you can input the dividend amount received for each asset for each month of that year. Totals are updated in real-time as you type.
    *   **Summary Tab**: A read-only tab that provides a consolidated view of all dividend income. It shows the total dividends received per asset for each year, the total for each asset across all years, and a grand total.

### Data Handling Functions

*   `cargar_cartera()` / `guardar_cartera(cartera)`: These functions handle reading from and writing to the `cartera.json` file. They are responsible for loading the portfolio when the app starts and saving any changes (additions, edits, deletions).

*   `cargar_dividendos()` / `guardar_dividendos(dividendos)`: Similar to the portfolio functions, these manage the reading and writing of dividend data to the `dividendos.json` file. Data is saved automatically as you edit the dividend tables.

*   `obtener_precios_actuales(simbolos)`: Takes a list of stock symbols and uses the `yfinance` library to fetch their current market prices. It includes error handling for symbols that are not found.

## Data Files

The application relies on two JSON files to store its data:

### `cartera.json`

This file stores an array of asset objects. Each object represents an asset in the portfolio and has the following structure:

```json
{
    "símbolo": "IWRD.AS",
    "título": "iShs MSCI World ETF USD D (XAMS:IWRD)",
    "cantidad": 25,
    "precio_actual": 74.015,
    "importe_total": 1850.375,
    "dividendos": "Sí",
    "tipo_activo": "ETF",
    "broker": "degiro"
}
```

### `dividendos.json`

This file stores a dictionary where keys are years (as strings). Each year-key holds another dictionary where keys are asset symbols. The value for each symbol is an array of 12 strings, representing the dividend income for each month from January to December.

```json
{
    "2024": {
        "HDLV.DE": [
            "",
            "",
            "7.71",
            "",
            "",
            "9.12",
            "",
            "",
            "8.66",
            "",
            "",
            "10.07"
        ]
    }
}
```