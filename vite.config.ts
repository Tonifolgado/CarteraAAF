import { defineConfig, Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs';
import path from 'path';
import type { IncomingMessage, ServerResponse } from 'http';

const ROOT_DIR = path.resolve(__dirname);
const CARTERA_FILE = path.join(ROOT_DIR, 'data', 'cartera.json');
const DIVIDENDOS_FILE = path.join(ROOT_DIR, 'data', 'dividendos.json');
const PATRIMONIO_FILE = path.join(ROOT_DIR, 'data', 'patrimonio.json');
const BALANCES_CSV_FILE = path.join(ROOT_DIR, 'BalancesMensuales.csv');

function readBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', (chunk) => {
      body += chunk.toString();
    });
    req.on('end', () => resolve(body));
    req.on('error', reject);
  });
}

function sendJson(res: ServerResponse, status: number, data: unknown) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.end(JSON.stringify(data));
}

function normalizeFullWidthDigits(str: string): string {
  return str.replace(/[\uFF10-\uFF19]/g, (ch) =>
    String.fromCharCode(ch.charCodeAt(0) - 0xfee0)
  );
}

export function convertirEuroAFloat(valorStr: string | undefined): number {
  if (!valorStr || valorStr.trim() === '') return 0.0;
  let s = normalizeFullWidthDigits(valorStr.trim());
  s = s.replace(/€/g, '').trim();
  s = s.replace(/\./g, ''); // Eliminar separadores de miles
  s = s.replace(/,/g, '.'); // Cambiar coma decimal a punto
  if (!/^[+-]?\d+(\.\d+)?$/.test(s)) {
    return 0.0;
  }
  const num = Number(s);
  return Number.isFinite(num) ? num : 0.0;
}

export function formatFloatToEuroStr(value: number): string {
  const isNegative = value < 0;
  const absValue = Math.abs(value);
  const s = absValue.toFixed(2).replace('.', ',');
  const parts = s.split(',');
  const integerPart = parts[0];
  const decimalPart = parts[1] ?? '00';

  const reversedDigits = integerPart.split('').reverse();
  const formattedReversed: string[] = [];
  reversedDigits.forEach((digit, i) => {
    if (i > 0 && i % 3 === 0) {
      formattedReversed.push('.');
    }
    formattedReversed.push(digit);
  });
  const formattedIntegerPart = formattedReversed.reverse().join('');
  const sign = isNegative ? '-' : '';
  return `${sign}${formattedIntegerPart},${decimalPart} €`;
}

function parseBalancesCsv(csvPath: string) {
  const datosPorAno: Record<
    number,
    Array<{ mes: string; ingresos: number; gastos: number; saldo: number }>
  > = {};

  if (!fs.existsSync(csvPath)) {
    return datosPorAno;
  }

  const content = fs.readFileSync(csvPath, 'utf-8');
  const lineas = content.split(/\r?\n/);
  let anoActual: number | null = null;

  for (let i = 1; i < lineas.length; i++) {
    const linea = lineas[i].replace(/[\r\n]+$/, '');
    if (!linea || linea.trim() === '') continue;

    const partes = linea.split('\t');
    const col0 = partes[0] ?? '';

    if (col0.length === 4 && /^\d{4}$/.test(col0)) {
      anoActual = parseInt(col0, 10);
      if (!datosPorAno[anoActual]) {
        datosPorAno[anoActual] = [];
      }
      const mes = (partes[1] ?? '').trim();
      const ingresos = convertirEuroAFloat(partes[2]);
      const gastos = convertirEuroAFloat(partes[3]);
      const saldo = convertirEuroAFloat(partes[4]);
      datosPorAno[anoActual].push({ mes, ingresos, gastos, saldo });
    } else if (anoActual !== null && col0.trim() === '') {
      const mes = (partes[1] ?? '').trim();
      const ingresos = convertirEuroAFloat(partes[2]);
      const gastos = convertirEuroAFloat(partes[3]);
      const saldo = convertirEuroAFloat(partes[4]);
      datosPorAno[anoActual].push({ mes, ingresos, gastos, saldo });
    }
  }

  return datosPorAno;
}

async function fetchYahooPrice(symbol: string): Promise<number> {
  try {
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(
      symbol
    )}?interval=1d&range=1d`;
    const response = await fetch(url, {
      headers: {
        'User-Agent':
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
      }
    });
    if (!response.ok) return 0.0;
    const data = (await response.json()) as any;
    const meta = data?.chart?.result?.[0]?.meta;
    const price = meta?.regularMarketPrice ?? meta?.previousClose ?? 0.0;
    return typeof price === 'number' && Number.isFinite(price) ? price : 0.0;
  } catch {
    return 0.0;
  }
}

function carteraApiPlugin(): Plugin {
  const setupMiddleware = (middlewares: any) => {
    middlewares.use(async (req: IncomingMessage, res: ServerResponse, next: () => void) => {
      const url = req.url?.split('?')[0];
      if (!url || !url.startsWith('/api/')) {
        return next();
      }

      try {
        // 1. CARTERA
        if (url === '/api/cartera' && req.method === 'GET') {
          if (!fs.existsSync(CARTERA_FILE)) {
            return sendJson(res, 200, []);
          }
          const raw = fs.readFileSync(CARTERA_FILE, 'utf-8');
          return sendJson(res, 200, JSON.parse(raw));
        }

        if (url === '/api/cartera' && req.method === 'POST') {
          const body = await readBody(req);
          const data = JSON.parse(body);
          fs.mkdirSync(path.dirname(CARTERA_FILE), { recursive: true });
          fs.writeFileSync(CARTERA_FILE, JSON.stringify(data, null, 4), 'utf-8');
          return sendJson(res, 200, { ok: true });
        }

        // 2. DIVIDENDOS
        if (url === '/api/dividendos' && req.method === 'GET') {
          if (!fs.existsSync(DIVIDENDOS_FILE)) {
            return sendJson(res, 200, {});
          }
          const raw = fs.readFileSync(DIVIDENDOS_FILE, 'utf-8');
          return sendJson(res, 200, JSON.parse(raw));
        }

        if (url === '/api/dividendos' && req.method === 'POST') {
          const body = await readBody(req);
          const data = JSON.parse(body);
          fs.mkdirSync(path.dirname(DIVIDENDOS_FILE), { recursive: true });
          fs.writeFileSync(DIVIDENDOS_FILE, JSON.stringify(data, null, 4), 'utf-8');
          return sendJson(res, 200, { ok: true });
        }

        // 3. PATRIMONIO
        if (url === '/api/patrimonio' && req.method === 'GET') {
          if (!fs.existsSync(PATRIMONIO_FILE)) {
            return sendJson(res, 200, {});
          }
          const raw = fs.readFileSync(PATRIMONIO_FILE, 'utf-8');
          return sendJson(res, 200, JSON.parse(raw));
        }

        if (url === '/api/patrimonio' && req.method === 'POST') {
          const body = await readBody(req);
          const data = JSON.parse(body);
          fs.mkdirSync(path.dirname(PATRIMONIO_FILE), { recursive: true });
          fs.writeFileSync(PATRIMONIO_FILE, JSON.stringify(data, null, 4), 'utf-8');
          return sendJson(res, 200, { ok: true });
        }

        // 4. SALDOS MENSUALES (CSV)
        if (url === '/api/saldos' && req.method === 'GET') {
          const datosPorAno = parseBalancesCsv(BALANCES_CSV_FILE);
          return sendJson(res, 200, datosPorAno);
        }

        if (url === '/api/saldos' && req.method === 'POST') {
          const body = await readBody(req);
          const { ano, mes, ingresos, gastos } = JSON.parse(body) as {
            ano: string;
            mes: string;
            ingresos: number;
            gastos: number;
          };
          const saldo = ingresos - gastos;
          const ingresosCsv = formatFloatToEuroStr(ingresos);
          const gastosCsv = formatFloatToEuroStr(gastos);
          const saldoCsv = formatFloatToEuroStr(saldo);
          const lineaNueva = `${ano}\t${mes}\t${ingresosCsv}\t${gastosCsv}\t${saldoCsv}\n`;

          if (!fs.existsSync(BALANCES_CSV_FILE) || fs.statSync(BALANCES_CSV_FILE).size === 0) {
            fs.writeFileSync(BALANCES_CSV_FILE, 'AÑO\tMES\tINGRESOS\tGASTOS\tSALDO\n', 'utf-8');
          }
          fs.appendFileSync(BALANCES_CSV_FILE, lineaNueva, 'utf-8');
          const datosPorAno = parseBalancesCsv(BALANCES_CSV_FILE);
          return sendJson(res, 200, { ok: true, datosPorAno });
        }

        // 5. MARKET PRICES (Yahoo Finance)
        if (url === '/api/market-prices' && req.method === 'POST') {
          const body = await readBody(req);
          const { symbols } = JSON.parse(body) as { symbols: string[] };
          const precios: Record<string, number> = {};
          await Promise.all(
            (symbols || []).map(async (sym) => {
              precios[sym] = await fetchYahooPrice(sym);
            })
          );
          return sendJson(res, 200, precios);
        }

        return sendJson(res, 404, { error: 'Not found' });
      } catch (err: any) {
        return sendJson(res, 500, { error: err?.message || 'Internal Server Error' });
      }
    });
  };

  return {
    name: 'cartera-aaf-api',
    configureServer(server) {
      setupMiddleware(server.middlewares);
    },
    configurePreviewServer(server) {
      setupMiddleware(server.middlewares);
    }
  };
}

export default defineConfig({
  plugins: [react(), carteraApiPlugin()],
  server: {
    port: 3000,
    host: '0.0.0.0'
  }
});

