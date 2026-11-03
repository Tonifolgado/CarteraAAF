import {
  Asset,
  RawAsset,
  rawToAsset,
  assetToRaw,
  DividendosData,
  PatrimonioData,
  SaldosPorAno
} from '../types';

import initialCarteraJson from '../../data/cartera.json';
import initialDividendosJson from '../../data/dividendos.json';
import initialPatrimonioJson from '../../data/patrimonio.json';
import initialBalancesCsvRaw from '../../BalancesMensuales.csv?raw';

const LS_CARTERA = 'cartera_aaf_assets';
const LS_DIVIDENDOS = 'cartera_aaf_dividendos';
const LS_PATRIMONIO = 'cartera_aaf_patrimonio';
const LS_SALDOS = 'cartera_aaf_saldos';

function normalizeFullWidthDigits(str: string): string {
  return str.replace(/[\uFF10-\uFF19]/g, (ch) =>
    String.fromCharCode(ch.charCodeAt(0) - 0xfee0)
  );
}

function convertirEuroAFloatClient(valorStr: string | undefined): number {
  if (!valorStr || valorStr.trim() === '') return 0.0;
  let s = normalizeFullWidthDigits(valorStr.trim());
  s = s.replace(/€/g, '').trim();
  s = s.replace(/\./g, '');
  s = s.replace(/,/g, '.');
  if (!/^[+-]?\d+(\.\d+)?$/.test(s)) {
    return 0.0;
  }
  const num = Number(s);
  return Number.isFinite(num) ? num : 0.0;
}

function parseBalancesCsvString(content: string): SaldosPorAno {
  const datosPorAno: SaldosPorAno = {};
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
      const ingresos = convertirEuroAFloatClient(partes[2]);
      const gastos = convertirEuroAFloatClient(partes[3]);
      const saldo = convertirEuroAFloatClient(partes[4]);
      datosPorAno[anoActual].push({ mes, ingresos, gastos, saldo });
    } else if (anoActual !== null && col0.trim() === '') {
      const mes = (partes[1] ?? '').trim();
      const ingresos = convertirEuroAFloatClient(partes[2]);
      const gastos = convertirEuroAFloatClient(partes[3]);
      const saldo = convertirEuroAFloatClient(partes[4]);
      datosPorAno[anoActual].push({ mes, ingresos, gastos, saldo });
    }
  }

  return datosPorAno;
}

export async function fetchCartera(): Promise<Asset[]> {
  try {
    const res = await fetch('/api/cartera');
    if (res.ok) {
      const data = (await res.json()) as RawAsset[];
      const assets = data.map(rawToAsset);
      localStorage.setItem(LS_CARTERA, JSON.stringify(data));
      return assets;
    }
  } catch {
    // Fallback to localStorage / bundled json
  }
  const cached = localStorage.getItem(LS_CARTERA);
  if (cached) {
    try {
      return (JSON.parse(cached) as RawAsset[]).map(rawToAsset);
    } catch {
      // ignore
    }
  }
  return (initialCarteraJson as RawAsset[]).map(rawToAsset);
}

export async function saveCartera(assets: Asset[]): Promise<void> {
  const rawList: RawAsset[] = assets.map(assetToRaw);
  localStorage.setItem(LS_CARTERA, JSON.stringify(rawList));
  try {
    await fetch('/api/cartera', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(rawList)
    });
  } catch {
    // Saved in localStorage as fallback
  }
}

export async function fetchDividendos(): Promise<DividendosData> {
  try {
    const res = await fetch('/api/dividendos');
    if (res.ok) {
      const data = (await res.json()) as DividendosData;
      localStorage.setItem(LS_DIVIDENDOS, JSON.stringify(data));
      return data;
    }
  } catch {
    // fallback
  }
  const cached = localStorage.getItem(LS_DIVIDENDOS);
  if (cached) {
    try {
      return JSON.parse(cached) as DividendosData;
    } catch {
      // ignore
    }
  }
  return initialDividendosJson as unknown as DividendosData;
}

export async function saveDividendos(dividendos: DividendosData): Promise<void> {
  localStorage.setItem(LS_DIVIDENDOS, JSON.stringify(dividendos));
  try {
    await fetch('/api/dividendos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dividendos)
    });
  } catch {
    // fallback
  }
}

export async function fetchPatrimonio(): Promise<PatrimonioData> {
  try {
    const res = await fetch('/api/patrimonio');
    if (res.ok) {
      const data = (await res.json()) as PatrimonioData;
      localStorage.setItem(LS_PATRIMONIO, JSON.stringify(data));
      return data;
    }
  } catch {
    // fallback
  }
  const cached = localStorage.getItem(LS_PATRIMONIO);
  if (cached) {
    try {
      return JSON.parse(cached) as PatrimonioData;
    } catch {
      // ignore
    }
  }
  return initialPatrimonioJson as unknown as PatrimonioData;
}

export async function savePatrimonio(patrimonio: PatrimonioData): Promise<void> {
  localStorage.setItem(LS_PATRIMONIO, JSON.stringify(patrimonio));
  try {
    await fetch('/api/patrimonio', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patrimonio)
    });
  } catch {
    // fallback
  }
}

export async function fetchSaldosMensuales(): Promise<SaldosPorAno> {
  try {
    const res = await fetch('/api/saldos');
    if (res.ok) {
      const data = (await res.json()) as SaldosPorAno;
      if (data && Object.keys(data).length > 0) {
        localStorage.setItem(LS_SALDOS, JSON.stringify(data));
        return data;
      }
    }
  } catch {
    // fallback
  }
  const cached = localStorage.getItem(LS_SALDOS);
  if (cached) {
    try {
      const parsed = JSON.parse(cached) as SaldosPorAno;
      if (parsed && Object.keys(parsed).length > 0) {
        return parsed;
      }
    } catch {
      // ignore
    }
  }
  const fromCsv = parseBalancesCsvString(initialBalancesCsvRaw);
  localStorage.setItem(LS_SALDOS, JSON.stringify(fromCsv));
  return fromCsv;
}

export async function addSaldoMensual(
  ano: string,
  mes: string,
  ingresos: number,
  gastos: number
): Promise<SaldosPorAno> {
  try {
    const res = await fetch('/api/saldos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ano, mes, ingresos, gastos })
    });
    if (res.ok) {
      const json = (await res.json()) as { ok: boolean; datosPorAno: SaldosPorAno };
      localStorage.setItem(LS_SALDOS, JSON.stringify(json.datosPorAno));
      return json.datosPorAno;
    }
  } catch {
    // fallback
  }

  const current = await fetchSaldosMensuales();
  const anoNum = parseInt(ano, 10);
  if (!current[anoNum]) {
    current[anoNum] = [];
  }
  current[anoNum].push({
    mes,
    ingresos,
    gastos,
    saldo: ingresos - gastos
  });
  localStorage.setItem(LS_SALDOS, JSON.stringify(current));
  return current;
}

export async function obtenerPreciosActuales(
  simbolos: string[]
): Promise<Record<string, number>> {
  try {
    const res = await fetch('/api/market-prices', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbols: simbolos })
    });
    if (res.ok) {
      return (await res.json()) as Record<string, number>;
    }
  } catch {
    // ignore
  }
  const fallback: Record<string, number> = {};
  simbolos.forEach((s) => {
    fallback[s] = 0.0;
  });
  return fallback;
}
