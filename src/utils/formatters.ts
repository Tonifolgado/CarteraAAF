import { Asset } from '../types';

export const ANCHO_TITULO_DIVIDENDOS = 20;

export function tituloCorto(activo: Asset, ancho: number = ANCHO_TITULO_DIVIDENDOS): string {
  const titulo = activo.titulo || activo.simbolo;
  return titulo.length <= ancho ? titulo : titulo.slice(0, ancho - 1).trimEnd() + '…';
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

export function parseEuroInput(raw: string): number {
  const trimmed = raw.trim().replace(/€/g, '').trim();
  if (!trimmed) return 0.0;
  // Si contiene coma decimal (formato español: 1.234,56)
  if (trimmed.includes(',')) {
    const normalized = trimmed.replace(/\./g, '').replace(',', '.');
    return Number(normalized);
  }
  // Si tiene punto con exactamente 3 decimales tipo "1.500", tratar como separador de miles como en Python
  if (/^[+-]?\d{1,3}(\.\d{3})+$/.test(trimmed)) {
    return Number(trimmed.replace(/\./g, ''));
  }
  return Number(trimmed);
}

