import yfinance as yf

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
