# Gestor de Cartera AAF (Aplicación Web en TypeScript)

**Gestor de Cartera AAF** ha sido convertido en una aplicación web moderna en **TypeScript + React + Vite**, manteniendo el 100% de las funcionalidades, cálculos, tablas, colores, gráficos y persistencia de datos (`data/cartera.json`, `data/dividendos.json`, `data/patrimonio.json` y `BalancesMensuales.csv`) de la aplicación original en Python.

## Cómo Ejecutar la Aplicación Web (TypeScript)

### 1. Iniciar el servidor de desarrollo
Desde la raíz del proyecto ejecuta:
```bash
npm run dev
```
La aplicación estará disponible en `http://localhost:3000`.

### 2. Compilar para producción
```bash
npm run build
npm run preview
```

## Estructura del Proyecto Web (TypeScript)

* **`vite.config.ts`**: Configuración de Vite junto con el plugin de API backend (`/api/cartera`, `/api/dividendos`, `/api/patrimonio`, `/api/saldos`, `/api/market-prices`) que lee y guarda directamente en los ficheros locales de `data/` y `BalancesMensuales.csv`, además de consultar cotizaciones en tiempo real desde Yahoo Finance.
* **`src/types.ts`**: Modelos e interfaces en TypeScript (`Asset`, `DividendosData`, `PatrimonioData`, `SaldosPorAno`, etc.).
* **`src/services/api.ts`**: Servicio de comunicación con los endpoints de persistencia en disco (con respaldo automático en `localStorage`) y consulta de precios de mercado.
* **`src/utils/formatters.ts`**: Utilidades de formateo en euros (`1.234,56 €`), recorte de títulos (`tituloCorto`) y parseo numérico.
* **`src/components/`**:
  * `HomeMenu.tsx`: Menú principal con KPIs y acceso directo a los 6 módulos.
  * `AgregarActivoView.tsx`: Formulario para añadir nuevos activos con consulta automática/manual a Yahoo Finance y cálculo en vivo del precio final con comisión.
  * `VerCarteraView.tsx`: Tabla completa ordenada por tipo de activo y símbolo, colores por categoría (`ACC`, `ETF`, `PP`, `FON`), edición y eliminación modal, resúmenes por Tipo y Broker (Importe y Acciones) y gráficos de barras y circular.
  * `DividendosView.tsx`: Pestaña de `Resumen` (con tabla consolidada 2022–2026 y gráfico de evolución anual) y pestañas editables por año (`2022`–`2026`) con resaltado en verde para cobros registrados y guardado en `data/dividendos.json`.
  * `AgregarSaldoView.tsx`: Registro de nuevos balances mensuales con cálculo en tiempo real del saldo en formato euro español y escritura en `BalancesMensuales.csv`.
  * `SaldosMensualesView.tsx`: Resumen Anual General (2000–2026), índice rápido `"Ir al año:"` con desplazamiento suave y tablas detalladas por cada año.
  * `PatrimonioView.tsx`: Gestión de Cuentas Corrientes (`CC`), Planes de Pensiones (`PP`) e Inversiones (`INV`) entre 2020 y 2026, gráfico circular de distribución Diciembre 2025 con importes y porcentajes, total destacado de 2026 y tabla reactiva de `TOTALES POR AÑO`.
  * `Charts.tsx`: Componentes de gráficos interactivos en SVG (`AssetBarChart` y `AssetPieChart`).
