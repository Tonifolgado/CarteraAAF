import React, { useMemo, useState } from 'react';
import {
  ANOS_PATRIMONIO,
  MESES_PATRIMONIO,
  PatrimonioData
} from '../types';
import { AssetPieChart } from './Charts';

interface PatrimonioViewProps {
  patrimonioData: PatrimonioData;
  onSavePatrimonio: (updated: PatrimonioData) => Promise<void>;
}

const METRICAS_ROWS = [
  '% cc Enero',
  'Cant. cc Enero',
  '% cc Diciembre',
  'Cant. cc Diciembre',
  '% PP Enero',
  'Cant. PP Enero',
  '% PP Diciembre',
  'Cant. PP Diciembre',
  '% INV Enero',
  'Cant. INV Enero',
  '% INV Diciembre',
  'Cant. INV Diciembre'
] as const;

function formatSpanishMiles(val: number): string {
  return val
    .toFixed(2)
    .replace('.', ',')
    .replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

export const PatrimonioView: React.FC<PatrimonioViewProps> = ({
  patrimonioData,
  onSavePatrimonio
}) => {
  // Store editable strings per [mes][columna]
  const [entries, setEntries] = useState<Record<string, Record<string, string>>>(() => {
    const init: Record<string, Record<string, string>> = {};
    MESES_PATRIMONIO.forEach((mes) => {
      init[mes] = {};
      ANOS_PATRIMONIO.forEach((ano) => {
        ['cc', 'PP', 'INV'].forEach((prefix) => {
          const col = `${prefix}${ano}`;
          const raw = patrimonioData?.[mes]?.[col];
          init[mes][col] = raw !== undefined && raw !== null && raw !== '' ? String(raw) : '';
        });
      });
    });
    return init;
  });

  const [invalidCell, setInvalidCell] = useState<{ mes: string; col: string } | null>(null);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; msg: string } | null>(
    null
  );
  const [saving, setSaving] = useState(false);

  React.useEffect(() => {
    const next: Record<string, Record<string, string>> = {};
    MESES_PATRIMONIO.forEach((mes) => {
      next[mes] = {};
      ANOS_PATRIMONIO.forEach((ano) => {
        ['cc', 'PP', 'INV'].forEach((prefix) => {
          const col = `${prefix}${ano}`;
          const raw = patrimonioData?.[mes]?.[col];
          next[mes][col] = raw !== undefined && raw !== null && raw !== '' ? String(raw) : '';
        });
      });
    });
    setEntries(next);
  }, [patrimonioData]);

  const handleEntryChange = (mes: string, col: string, value: string) => {
    if (invalidCell && invalidCell.mes === mes && invalidCell.col === col) {
      setInvalidCell(null);
    }
    setEntries((prev) => ({
      ...prev,
      [mes]: {
        ...(prev[mes] || {}),
        [col]: value
      }
    }));
  };

  const parseVal = (s: string | undefined): number => {
    if (!s || s.trim() === '') return 0.0;
    const n = parseFloat(s.trim().replace(',', '.'));
    return Number.isFinite(n) ? n : 0.0;
  };

  const anoGrafico = 2025;

  const calculos = useMemo(() => {
    const totalesEnero: Record<number, number> = {};
    const totalesDiciembre: Record<number, number> = {};
    const metricasPorAno: Record<string, Record<number, string>> = {};
    METRICAS_ROWS.forEach((m) => {
      metricasPorAno[m] = {};
    });

    let valoresGrafico2025: [number, number, number] = [0, 0, 0];
    let ultimoMes2026 = 'Enero';
    let totalUltimoMes2026 = 0.0;

    ANOS_PATRIMONIO.forEach((ano) => {
      const ccCol = `cc${ano}`;
      const ppCol = `PP${ano}`;
      const invCol = `INV${ano}`;

      const valoresMeses: Record<string, { cc: number; pp: number; inv: number }> = {};
      MESES_PATRIMONIO.forEach((mes) => {
        valoresMeses[mes] = {
          cc: parseVal(entries[mes]?.[ccCol]),
          pp: parseVal(entries[mes]?.[ppCol]),
          inv: parseVal(entries[mes]?.[invCol])
        };
      });

      const totalEne =
        valoresMeses['Enero'].cc + valoresMeses['Enero'].pp + valoresMeses['Enero'].inv;
      const totalDic =
        valoresMeses['Diciembre'].cc +
        valoresMeses['Diciembre'].pp +
        valoresMeses['Diciembre'].inv;

      totalesEnero[ano] = totalEne;
      totalesDiciembre[ano] = totalDic;

      if (ano === 2025) {
        valoresGrafico2025 = [
          valoresMeses['Diciembre'].cc,
          valoresMeses['Diciembre'].pp,
          valoresMeses['Diciembre'].inv
        ];
      }

      if (ano === 2026) {
        MESES_PATRIMONIO.forEach((mesIter) => {
          const totalMesIter =
            valoresMeses[mesIter].cc + valoresMeses[mesIter].pp + valoresMeses[mesIter].inv;
          if (totalMesIter > 0) {
            ultimoMes2026 = mesIter;
            totalUltimoMes2026 = totalMesIter;
          }
        });
      }

      // Enero %
      if (totalEne > 0) {
        const pctCcEne = (valoresMeses['Enero'].cc / totalEne) * 100;
        const pctPpEne = (valoresMeses['Enero'].pp / totalEne) * 100;
        const pctInvEne = (valoresMeses['Enero'].inv / totalEne) * 100;

        metricasPorAno['% cc Enero'][ano] = `${pctCcEne.toFixed(2)}%`;
        metricasPorAno['Cant. cc Enero'][ano] = valoresMeses['Enero'].cc.toFixed(2);
        metricasPorAno['% PP Enero'][ano] = `${pctPpEne.toFixed(2)}%`;
        metricasPorAno['Cant. PP Enero'][ano] = valoresMeses['Enero'].pp.toFixed(2);
        metricasPorAno['% INV Enero'][ano] = `${pctInvEne.toFixed(2)}%`;
        metricasPorAno['Cant. INV Enero'][ano] = valoresMeses['Enero'].inv.toFixed(2);
      } else {
        metricasPorAno['% cc Enero'][ano] = '0.00%';
        metricasPorAno['Cant. cc Enero'][ano] = '0.00';
        metricasPorAno['% PP Enero'][ano] = '0.00%';
        metricasPorAno['Cant. PP Enero'][ano] = '0.00';
        metricasPorAno['% INV Enero'][ano] = '0.00%';
        metricasPorAno['Cant. INV Enero'][ano] = '0.00';
      }

      // Diciembre %
      if (totalDic > 0) {
        const pctCcDic = (valoresMeses['Diciembre'].cc / totalDic) * 100;
        const pctPpDic = (valoresMeses['Diciembre'].pp / totalDic) * 100;
        const pctInvDic = (valoresMeses['Diciembre'].inv / totalDic) * 100;

        metricasPorAno['% cc Diciembre'][ano] = `${pctCcDic.toFixed(2)}%`;
        metricasPorAno['Cant. cc Diciembre'][ano] = valoresMeses['Diciembre'].cc.toFixed(2);
        metricasPorAno['% PP Diciembre'][ano] = `${pctPpDic.toFixed(2)}%`;
        metricasPorAno['Cant. PP Diciembre'][ano] = valoresMeses['Diciembre'].pp.toFixed(2);
        metricasPorAno['% INV Diciembre'][ano] = `${pctInvDic.toFixed(2)}%`;
        metricasPorAno['Cant. INV Diciembre'][ano] = valoresMeses['Diciembre'].inv.toFixed(2);
      } else {
        metricasPorAno['% cc Diciembre'][ano] = '0.00%';
        metricasPorAno['Cant. cc Diciembre'][ano] = '0.00';
        metricasPorAno['% PP Diciembre'][ano] = '0.00%';
        metricasPorAno['Cant. PP Diciembre'][ano] = '0.00';
        metricasPorAno['% INV Diciembre'][ano] = '0.00%';
        metricasPorAno['Cant. INV Diciembre'][ano] = '0.00';
      }
    });

    return {
      totalesEnero,
      totalesDiciembre,
      metricasPorAno,
      valoresGrafico2025,
      ultimoMes2026,
      totalUltimoMes2026
    };
  }, [entries]);

  const handleGuardarPatrimonio = async () => {
    setFeedback(null);
    setInvalidCell(null);

    const ccCols = ANOS_PATRIMONIO.map((a) => `cc${a}`);
    const ppCols = ANOS_PATRIMONIO.map((a) => `PP${a}`);
    const invCols = ANOS_PATRIMONIO.map((a) => `INV${a}`);
    const todasColumnas = [...ccCols, ...ppCols, ...invCols];

    const datosNuevos: PatrimonioData = {};

    for (const mes of MESES_PATRIMONIO) {
      datosNuevos[mes] = {};
      for (const col of todasColumnas) {
        const valorTexto = (entries[mes]?.[col] ?? '').trim();
        if (valorTexto) {
          const parsed = Number(valorTexto.replace(',', '.'));
          if (Number.isNaN(parsed)) {
            setInvalidCell({ mes, col });
            setFeedback({
              type: 'error',
              msg: `El valor en ${mes} - ${col} no es un número válido.`
            });
            return;
          }
          datosNuevos[mes][col] = parsed;
        } else {
          datosNuevos[mes][col] = '';
        }
      }
    }

    setSaving(true);
    try {
      await onSavePatrimonio(datosNuevos);
      setFeedback({ type: 'success', msg: 'Datos de patrimonio guardados correctamente.' });
      setTimeout(() => setFeedback(null), 4000);
    } finally {
      setSaving(false);
    }
  };

  const renderAccountTable = (
    tituloGrupo: string,
    prefix: 'cc' | 'PP' | 'INV',
    bgHeader: string,
    bgSubheader: string,
    explicacion: string
  ) => {
    const columnas = ANOS_PATRIMONIO.map((a) => `${prefix}${a}`);

    return (
      <fieldset
        className="tk-labelframe-patrimonio"
        style={{ backgroundColor: bgHeader }}
      >
        <legend>{tituloGrupo}</legend>
        <div className="table-scroll-container">
          <table className="tk-table patrimonio-input-table">
            <thead>
              <tr>
                <th className="tk-cell-lightgray text-center">Mes</th>
                {columnas.map((col) => (
                  <th
                    key={col}
                    className="text-center font-bold"
                    style={{ backgroundColor: bgSubheader }}
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {MESES_PATRIMONIO.map((mes) => (
                <tr key={mes}>
                  <td className="tk-cell-lightgray font-bold text-center">{mes}</td>
                  {columnas.map((col) => {
                    const isErr =
                      invalidCell?.mes === mes && invalidCell?.col === col;
                    return (
                      <td key={col} className="p-05">
                        <input
                          type="text"
                          inputMode="decimal"
                          value={entries[mes]?.[col] ?? ''}
                          onChange={(e) => handleEntryChange(mes, col, e.target.value)}
                          className="patrimonio-cell-input"
                          style={{
                            backgroundColor: isErr ? '#fca5a5' : '#ffffff'
                          }}
                        />
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="patrimonio-table-caption">{explicacion}</div>
      </fieldset>
    );
  };

  const pieSlices2025 = [
    { label: 'CC', value: calculos.valoresGrafico2025[0], color: '#ADD8E6' },
    { label: 'PP', value: calculos.valoresGrafico2025[1], color: '#90EE90' },
    { label: 'INV', value: calculos.valoresGrafico2025[2], color: '#FFFFE0' }
  ];

  return (
    <div className="panel-card">
      <div className="panel-header">
        <h2>Patrimonio</h2>
        <button
          type="button"
          className="btn-green-action"
          onClick={handleGuardarPatrimonio}
          disabled={saving}
        >
          {saving ? 'Guardando...' : 'Guardar Patrimonio'}
        </button>
      </div>

      {feedback && (
        <div
          className={`alert-banner ${
            feedback.type === 'error' ? 'alert-error' : 'alert-success'
          }`}
        >
          {feedback.msg}
        </div>
      )}

      {/* LEYENDA */}
      <fieldset className="patrimonio-leyenda">
        <legend>Leyenda</legend>
        <div className="leyenda-items">
          <div className="leyenda-item">
            <span className="leyenda-badge" style={{ backgroundColor: '#ADD8E6' }}>
              Cuentas Corrientes (CC):
            </span>
            <span>CaixaBank, BBVA</span>
          </div>
          <div className="leyenda-item">
            <span className="leyenda-badge" style={{ backgroundColor: '#90EE90' }}>
              Planes de Pensiones (PP):
            </span>
            <span>CaixaBank, Santander</span>
          </div>
          <div className="leyenda-item">
            <span className="leyenda-badge" style={{ backgroundColor: '#FFFFE0' }}>
              Inversiones (INV):
            </span>
            <span>Degiro, Fondo BBVA, Ocean Broker</span>
          </div>
        </div>
      </fieldset>

      {/* Layout en dos columnas principales como en Tkinter */}
      <div className="patrimonio-two-col">
        {/* Columna izquierda: 3 tablas apiladas */}
        <div className="patrimonio-col-left">
          {renderAccountTable(
            'CUENTAS CORRIENTES',
            'cc',
            '#ADD8E6',
            '#87CEFA',
            'CaixaBank + BBVA'
          )}
          {renderAccountTable(
            'PLANES DE PENSIONES',
            'PP',
            '#90EE90',
            '#98FB98',
            'CaixaBank Tendencias PP + Santander PPE'
          )}
          {renderAccountTable(
            'INVERSIONES',
            'INV',
            '#FFFFE0',
            '#F0E68C',
            'Degiro + Ocean'
          )}
        </div>

        {/* Columna derecha: Gráfico, Etiqueta destacada 2026 y Tabla TOTALES POR AÑO */}
        <div className="patrimonio-col-right">
          <div className="patrimonio-chart-header-area">
            <AssetPieChart
              title="Distribución Diciembre 2025"
              items={pieSlices2025}
              showCurrencyInSlice={true}
              startAngleDeg={140}
              size="large"
            />
            <div className="patrimonio-total-destacado">
              Total {calculos.ultimoMes2026} 2026:{' '}
              {formatSpanishMiles(calculos.totalUltimoMes2026)} €
            </div>
          </div>

          <fieldset
            className="tk-labelframe-patrimonio"
            style={{ backgroundColor: '#FFFFE0' }}
          >
            <legend>TOTALES POR AÑO</legend>
            <div className="table-scroll-container">
              <table className="tk-table patrimonio-totales-table">
                <thead>
                  <tr>
                    <th className="tk-cell-lightgray text-center">Año</th>
                    {ANOS_PATRIMONIO.map((ano) => (
                      <th key={ano} className="tk-cell-orange text-center font-bold">
                        {ano}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {/* Fila Total Enero */}
                  <tr>
                    <td className="tk-cell-orange font-bold text-left">Total Enero</td>
                    {ANOS_PATRIMONIO.map((ano) => (
                      <td
                        key={ano}
                        className="text-center font-bold"
                        style={{ backgroundColor: '#FFFFE0' }}
                      >
                        {(calculos.totalesEnero[ano] || 0).toFixed(2)}
                      </td>
                    ))}
                  </tr>

                  {/* Fila Total Diciembre */}
                  <tr>
                    <td className="tk-cell-orange font-bold text-left">Total Diciembre</td>
                    {ANOS_PATRIMONIO.map((ano) => (
                      <td
                        key={ano}
                        className="text-center font-bold"
                        style={{ backgroundColor: '#FFFFE0' }}
                      >
                        {(calculos.totalesDiciembre[ano] || 0).toFixed(2)}
                      </td>
                    ))}
                  </tr>

                  {/* Filas de Porcentajes y Cantidades */}
                  {METRICAS_ROWS.map((metrica) => {
                    const isCant = metrica.includes('Cant.');
                    return (
                      <tr key={metrica}>
                        <td
                          className={`text-left ${isCant ? '' : 'font-bold'}`}
                          style={{
                            backgroundColor: isCant ? '#ffffff' : '#FFFFE0'
                          }}
                        >
                          {metrica}
                        </td>
                        {ANOS_PATRIMONIO.map((ano) => (
                          <td
                            key={ano}
                            className="text-center"
                            style={{ backgroundColor: '#ffffff' }}
                          >
                            {calculos.metricasPorAno[metrica]?.[ano] ??
                              (isCant ? '0.00' : '0.00%')}
                          </td>
                        ))}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </fieldset>
        </div>
      </div>

      <div className="panel-footer-right mt-4">
        <button
          type="button"
          className="btn-green-action"
          onClick={handleGuardarPatrimonio}
          disabled={saving}
        >
          {saving ? 'Guardando...' : 'Guardar Patrimonio'}
        </button>
      </div>
    </div>
  );
};
