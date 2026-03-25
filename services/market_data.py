import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed

def _fetch_price(simbolo):
    """Función auxiliar para obtener el precio de un único símbolo."""
    try:
        ticker = yf.Ticker(simbolo)
        # 'regularMarketPrice' es para datos actuales, 'previousClose' es un respaldo
        precio = ticker.info.get('regularMarketPrice') or ticker.info.get('previousClose')
        if precio:
            return simbolo, precio
        else:
            print(f"  - Advertencia: No se pudo obtener el precio para '{simbolo}'. Se omitirá.")
            return simbolo, 0.0
    except Exception:
        print(f"  - Advertencia: Símbolo '{simbolo}' no encontrado o error al obtener datos.")
        return simbolo, 0.0

def obtener_precios_actuales(simbolos):
    print("Obteniendo precios de mercado actuales...")
    precios = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_symbol = {executor.submit(_fetch_price, s): s for s in simbolos}
        for future in as_completed(future_to_symbol):
            simbolo, precio = future.result()
            precios[simbolo] = precio
    print("Precios obtenidos.")
    return precios
