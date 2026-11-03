export type TipoActivo = 'ACC' | 'ETF' | 'PP' | 'FON';
export type BrokerType = 'ocean' | 'degiro' | 'cxbank' | 'bbva' | 'sant';

export interface RawAsset {
  símbolo: string;
  título: string;
  cantidad: number;
  precio_actual: number;
  importe_total: number;
  dividendos: 'Sí' | 'No' | string;
  tipo_activo: TipoActivo | string;
  broker: BrokerType | string;
}

export interface Asset {
  simbolo: string;
  titulo: string;
  cantidad: number;
  precio_actual: number;
  importe_total: number;
  dividendos: 'Sí' | 'No';
  tipo_activo: TipoActivo | string;
  broker: BrokerType | string;
}

export function rawToAsset(raw: RawAsset): Asset {
  return {
    simbolo: raw['símbolo'],
    titulo: raw['título'],
    cantidad: Number(raw.cantidad),
    precio_actual: Number(raw.precio_actual),
    importe_total: Number(raw.importe_total),
    dividendos: raw.dividendos === 'Sí' ? 'Sí' : 'No',
    tipo_activo: raw.tipo_activo,
    broker: raw.broker
  };
}

export function assetToRaw(asset: Asset): RawAsset {
  return {
    símbolo: asset.simbolo,
    título: asset.titulo,
    cantidad: asset.cantidad,
    precio_actual: asset.precio_actual,
    importe_total: asset.importe_total,
    dividendos: asset.dividendos,
    tipo_activo: asset.tipo_activo,
    broker: asset.broker
  };
}

// { "2022": { "HDLV.DE": ["", "", "1.35", ...] } }
export type DividendosData = Record<string, Record<string, string[]>>;

// { "Enero": { "cc2020": 27000.0, ... } }
export type PatrimonioData = Record<string, Record<string, number | string>>;

export interface SaldoMesEntry {
  mes: string;
  ingresos: number;
  gastos: number;
  saldo: number;
}

export type SaldosPorAno = Record<number, SaldoMesEntry[]>;

export type ActiveView =
  | 'menu'
  | 'agregar_activos'
  | 'ver_cartera'
  | 'dividendos'
  | 'agregar_saldo'
  | 'saldos_mensuales'
  | 'patrimonio';

export const TIPOS_ACTIVO: TipoActivo[] = ['ACC', 'ETF', 'PP', 'FON'];
export const BROKERS: BrokerType[] = ['ocean', 'degiro', 'cxbank', 'bbva', 'sant'];
export const BROKERS_RESUMEN_ORDER: BrokerType[] = ['sant', 'cxbank', 'bbva', 'degiro', 'ocean'];

export const COLORES_TIPO_ACTIVO: Record<string, string> = {
  ACC: '#bbf7d0', // Verde claro para ACC
  ETF: '#FFFFE0', // LightYellow
  PP: '#ADD8E6',  // LightBlue
  FON: '#15803d'  // Verde oscuro para FON
};

export const COLORES_TIPO_ACTIVO_CLARO: Record<string, string> = {
  ACC: '#ecfdf5', // Tono más claro de verde para ACC (columna Importe)
  ETF: '#FFFFF5', // Tono más claro de LightYellow
  PP: '#E6F4F9',  // Tono más claro de LightBlue
  FON: '#86efac'  // Tono más claro que el verde oscuro de FON (columna Importe)
};

export const COLORES_TEXTO_TIPO_ACTIVO: Record<string, string> = {
  ETF: '#dc2626', // Letras rojas para ETF
  ACC: '#15803d'  // Letras verdes para ACC
};

export const COLORES_BROKER: Record<string, { bg: string; fg: string }> = {
  degiro: { bg: '#2563eb', fg: '#ffffff' }, // Fondo azul
  ocean: { bg: '#dc2626', fg: '#ffffff' },  // Fondo rojo
  bbva: { bg: '#16a34a', fg: '#ffffff' }    // Fondo verde
};

export const ANOS_DIVIDENDOS = [2022, 2023, 2024, 2025, 2026];
export const MESES_CORTOS = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
export const MESES_LARGOS = [
  'Enero',
  'Febrero',
  'Marzo',
  'Abril',
  'Mayo',
  'Junio',
  'Julio',
  'Agosto',
  'Septiembre',
  'Octubre',
  'Noviembre',
  'Diciembre'
];

export const MESES_PATRIMONIO = ['Enero', 'Marzo', 'Mayo', 'Julio', 'Octubre', 'Diciembre'];
export const ANOS_PATRIMONIO = [2020, 2021, 2022, 2023, 2024, 2025, 2026];

