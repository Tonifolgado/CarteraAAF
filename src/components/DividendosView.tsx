import React, { useMemo, useState } from 'react';
import {
  ANOS_DIVIDENDOS,
  Asset,
  DividendosData,
  MESES_CORTOS
} from '../types';
import { tituloCorto } from '../utils/formatters';
import { AssetBarChart } from './Charts';

interface DividendosViewProps {
  assets: Asset[];
  dividendosData: DividendosData;
  onSaveDividendos: (updated: DividendosData) => Promise<void>;
}

export const DividendosView: React.FC<DividendosViewProps> = ({
  assets,
  dividendosData,
  onSaveDividendos
}) => {
  const [activeTab, setActiveTab] = useState<'Resumen' | number>('Resumen');
  const [localData, setLocalData] = useState<DividendosData>(() =>
    JSON.parse(JSON.stringify(dividendosData))
  );
  const [saving, setSaving] = useState(false);
  const [savedBanner, setSavedBanner] = useState<string | null>(null);

  // Sync if prop updates externally
  React.useEffect(() => {
    setLocalData(JSON.parse(JSON.stringify(dividendosData)));
  }, [dividendosData]);

  const activosConDividendos = useMemo(() => {
    return assets
      .filter((a) => a.dividendos === 'Sí')
      .sort((a, b) => {
        const keyA = (a.titulo || a.simbolo).toLocaleLowerCase();
        const keyB = (b.titulo || b.simbolo).toLocaleLowerCase();
        return keyA.localeCompare(keyB);
      });
  }, [assets]);

  const parseCellVal = (raw: string | undefined): number => {
    if (!raw || raw.trim() === '') return 0;
    const n = parseFloat(raw.replace(',', '.'));
    return Number.isFinite(n) ? n : 0;
  };

  // Totales para la pestaña Resumen
  const resumenCalculado = useMemo(() => {
    const totalesPorActivoAno: Record<string, Record<number, number>> = {};
    const totalesPorAno: Record<number, number> = {};

    ANOS_DIVIDENDOS.forEach((ano) => {
      totalesPorAno[ano] = 0;
    });

    activosConDividendos.forEach((activo) => {
      totalesPorActivoAno[activo.simbolo] = {};
      ANOS_DIVIDENDOS.forEach((ano) => {
        const arr = localData[String(ano)]?.[activo.simbolo] || [];
        const sumAno = arr.reduce((acc, v) => acc + parseCellVal(v), 0);
        totalesPorActivoAno[activo.simbolo][ano] = sumAno;
        totalesPorAno[ano] += sumAno;
      });
    });

    const totalesPorActivo: Record<string, number> = {};
    activosConDividendos.forEach((activo) => {
      totalesPorActivo[activo.simbolo] = ANOS_DIVIDENDOS.reduce(
        (acc, ano) => acc + (totalesPorActivoAno[activo.simbolo]?.[ano] || 0),
        0
      );
    });

    const granTotal = ANOS_DIVIDENDOS.reduce((acc, ano) => acc + totalesPorAno[ano], 0);

    const maxPorAno: Record<number, number> = {};
    ANOS_DIVIDENDOS.forEach((ano) => {
      maxPorAno[ano] = Math.max(
        0,
        ...activosConDividendos.map((a) => totalesPorActivoAno[a.simbolo]?.[ano] || 0)
      );
    });

    const maxTotalActivo = Math.max(
      0,
      ...activosConDividendos.map((a) => totalesPorActivo[a.simbolo] || 0)
    );

    return {
      totalesPorActivoAno,
      totalesPorAno,
      totalesPorActivo,
      granTotal,
      maxPorAno,
      maxTotalActivo
    };
  }, [activosConDividendos, localData]);

  const handleCellChange = (ano: number, simbolo: string, mesIdx: number, val: string) => {
    setLocalData((prev) => {
      const anoKey = String(ano);
      const prevAno = prev[anoKey] ? { ...prev[anoKey] } : {};
      const prevMeses = prevAno[simbolo]
        ? [...prevAno[simbolo]]
        : Array.from({ length: 12 }, () => '');
      while (prevMeses.length < 12) {
        prevMeses.push('');
      }
      prevMeses[mesIdx] = val;
      prevAno[simbolo] = prevMeses;
      return {
        ...prev,
        [anoKey]: prevAno
      };
    });
  };

  const handleGuardarCambios = async () => {
    setSaving(true);
    setSavedBanner(null);
    try {
      // Asegurar que todos los años y activos tengan su array de 12 meses como en Python
      const normalized: DividendosData = { ...localData };
      ANOS_DIVIDENDOS.forEach((ano) => {
        const anoStr = String(ano);
        if (!normalized[anoStr]) normalized[anoStr] = {};
        activosConDividendos.forEach((act) => {
          const currentArr = normalized[anoStr][act.simbolo] || [];
          normalized[anoStr][act.simbolo] = Array.from(
            { length: 12 },
            (_, idx) => currentArr[idx] ?? ''
          );
        });
      });

      await onSaveDividendos(normalized);
      setSavedBanner('Todos los dividendos han sido guardados en disco correctamente.');
      setTimeout(() => setSavedBanner(null), 4000);
    } finally {
      setSaving(false);
    }
  };

  if (activosConDividendos.length === 0) {
    return (
      <div className="panel-card text-center py-12">
        <h2>Dividendos</h2>
        <p className="empty-msg">No hay activos con dividendos.</p>
      </div>
    );
  }

  const renderTabAno = (ano: number) => {
    const anoStr = String(ano);
    const dataAno = localData[anoStr] || {};

    const totalesMes = Array.from({ length: 12 }, (_, mesIdx) => {
      return activosConDividendos.reduce((acc, act) => {
        const valStr = dataAno[act.simbolo]?.[mesIdx] ?? '';
        return acc + parseCellVal(valStr);
      }, 0);
    });

    const maxPorMes = Array.from({ length: 12 }, (_, mesIdx) => {
      return Math.max(
        0,
        ...activosConDividendos.map((act) =>
          parseCellVal(dataAno[act.simbolo]?.[mesIdx])
        )
      );
    });

    const totalesFilaMap: Record<string, number> = {};
    activosConDividendos.forEach((act) => {
      const valoresMes = dataAno[act.simbolo] || [];
      totalesFilaMap[act.simbolo] = Array.from({ length: 12 }, (_, idx) =>
        parseCellVal(valoresMes[idx])
      ).reduce((a, b) => a + b, 0);
    });

    const maxTotalFila = Math.max(0, ...Object.values(totalesFilaMap));
    const maxTotalMes = Math.max(0, ...totalesMes);

    const totalGeneralAno = totalesMes.reduce((a, b) => a + b, 0);

    return (
      <div className="table-scroll-container">
        <table className="tk-table dividendos-ano-table">
          <thead>
            <tr className="tk-header-darkblue">
              <th className="text-left">Activo</th>
              {MESES_CORTOS.map((mes) => (
                <th key={mes} className="text-center">
                  {mes}
                </th>
              ))}
              <th className="text-center">Total</th>
            </tr>
          </thead>
          <tbody>
            {activosConDividendos.map((activo) => {
              const simbolo = activo.simbolo;
              const valoresMes = dataAno[simbolo] || [];
              const totalFila = totalesFilaMap[simbolo] || 0;
              const isMaxTotalFila = maxTotalFila > 0 && totalFila === maxTotalFila;

              return (
                <tr key={simbolo}>
                  <td
                    className="text-left font-medium whitespace-nowrap"
                    title={`${activo.titulo} (${activo.simbolo})`}
                  >
                    {tituloCorto(activo)}
                  </td>
                  {Array.from({ length: 12 }, (_, mesIdx) => {
                    const rawVal = valoresMes[mesIdx] ?? '';
                    const numVal = parseCellVal(rawVal);
                    const isPositive = numVal > 0;
                    const isMaxMes =
                      maxPorMes[mesIdx] > 0 && numVal === maxPorMes[mesIdx];
                    return (
                      <td key={mesIdx} className="p-1 text-center">
                        <input
                          type="text"
                          inputMode="decimal"
                          value={rawVal}
                          onChange={(e) =>
                            handleCellChange(ano, simbolo, mesIdx, e.target.value)
                          }
                          className="dividendo-cell-input"
                          style={{
                            backgroundColor: isPositive ? '#90EE90' : '#ffffff',
                            color: isMaxMes ? '#dc2626' : '#0f172a',
                            fontWeight: isMaxMes ? 800 : 600
                          }}
                        />
                      </td>
                    );
                  })}
                  <td
                    className="tk-cell-lightgray text-center font-bold"
                    style={isMaxTotalFila ? { color: '#dc2626' } : undefined}
                  >
                    {totalFila.toFixed(2)}
                  </td>
                </tr>
              );
            })}
            {/* Fila TOTAL */}
            <tr>
              <td className="tk-cell-orange-blue font-bold text-left">TOTAL</td>
              {totalesMes.map((tm, idx) => {
                const isMaxMesTotal = maxTotalMes > 0 && tm === maxTotalMes;
                return (
                  <td
                    key={idx}
                    className="tk-cell-lightgray font-bold text-center"
                    style={isMaxMesTotal ? { color: '#dc2626' } : undefined}
                  >
                    {tm.toFixed(2)}
                  </td>
                );
              })}
              <td className="tk-cell-orange font-bold text-center">
                {totalGeneralAno.toFixed(2)}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    );
  };

  const annualBarItems = ANOS_DIVIDENDOS.map((ano) => ({
    label: String(ano),
    value: resumenCalculado.totalesPorAno[ano] || 0,
    color: '#90EE90'
  }));

  return (
    <div className="panel-card">
      <div className="panel-header">
        <h2>Dividendos</h2>
        <button
          type="button"
          className="btn-green-action"
          onClick={handleGuardarCambios}
          disabled={saving}
        >
          {saving ? 'Guardando...' : 'Guardar Todos los Dividendos'}
        </button>
      </div>

      {savedBanner && <div className="alert-banner alert-success">{savedBanner}</div>}

      {/* Notebook Tabs */}
      <div className="notebook-tabs">
        <button
          type="button"
          className={`notebook-tab ${activeTab === 'Resumen' ? 'active' : ''}`}
          onClick={() => setActiveTab('Resumen')}
        >
          Resumen
        </button>
        {ANOS_DIVIDENDOS.map((ano) => (
          <button
            key={ano}
            type="button"
            className={`notebook-tab ${activeTab === ano ? 'active' : ''}`}
            onClick={() => setActiveTab(ano)}
          >
            {ano}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="notebook-body">
        {activeTab === 'Resumen' ? (
          <div className="resumen-dividendos-layout">
            <fieldset className="tk-labelframe-large">
              <legend>Resumen de Dividendos Totales</legend>
              <div className="table-scroll-container">
                <table className="tk-table">
                  <thead>
                    <tr className="tk-header-darkblue">
                      <th className="text-left">Activo</th>
                      {ANOS_DIVIDENDOS.map((ano) => (
                        <th key={ano} className="text-right">
                          {ano}
                        </th>
                      ))}
                      <th className="text-right">Total Activo</th>
                      <th className="text-right">% Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activosConDividendos.map((activo) => {
                      const simbolo = activo.simbolo;
                      const totalActivo = resumenCalculado.totalesPorActivo[simbolo] || 0;
                      const pct =
                        resumenCalculado.granTotal > 0
                          ? (totalActivo / resumenCalculado.granTotal) * 100
                          : 0;
                      const isMaxTotalActivo =
                        resumenCalculado.maxTotalActivo > 0 &&
                        totalActivo === resumenCalculado.maxTotalActivo;

                      return (
                        <tr key={simbolo}>
                          <td
                            className="text-left font-medium"
                            title={`${activo.titulo} (${activo.simbolo})`}
                          >
                            {tituloCorto(activo)}
                          </td>
                          {ANOS_DIVIDENDOS.map((ano) => {
                            const val =
                              resumenCalculado.totalesPorActivoAno[simbolo]?.[ano] || 0;
                            const isMaxAno =
                              resumenCalculado.maxPorAno[ano] > 0 &&
                              val === resumenCalculado.maxPorAno[ano];
                            return (
                              <td
                                key={ano}
                                className={`text-right ${isMaxAno ? 'font-bold' : ''}`}
                                style={
                                  isMaxAno
                                    ? { color: '#dc2626', fontWeight: 700 }
                                    : undefined
                                }
                              >
                                {val.toFixed(2)}€
                              </td>
                            );
                          })}
                          <td
                            className="tk-cell-lightgray text-right font-bold"
                            style={
                              isMaxTotalActivo
                                ? { backgroundColor: '#90EE90', color: '#dc2626' }
                                : { backgroundColor: '#d3d3d3' }
                            }
                          >
                            {totalActivo.toFixed(2)}€
                          </td>
                          <td
                            className="tk-cell-lightgray text-right font-bold"
                            style={
                              isMaxTotalActivo
                                ? { backgroundColor: '#1e3a8a', color: '#ffff00' }
                                : { backgroundColor: '#d3d3d3' }
                            }
                          >
                            {pct.toFixed(2)}%
                          </td>
                        </tr>
                      );
                    })}
                    {/* TOTAL AÑO */}
                    <tr>
                      <td className="tk-cell-orange font-bold text-left">TOTAL AÑO</td>
                      {ANOS_DIVIDENDOS.map((ano) => (
                        <td key={ano} className="tk-cell-orange font-bold text-right">
                          {(resumenCalculado.totalesPorAno[ano] || 0).toFixed(2)}€
                        </td>
                      ))}
                      <td className="tk-cell-red-white font-bold text-right">
                        {resumenCalculado.granTotal.toFixed(2)}€
                      </td>
                      <td className="tk-cell-red-white font-bold text-right">100.00%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </fieldset>

            <div className="mt-6 flex justify-center">
              <AssetBarChart
                title="Evolución Anual de Dividendos Cobrados"
                yAxisLabel="Dividendos (€)"
                items={annualBarItems}
                formatValueLabel={(val) => `${val.toFixed(2)}€`}
                size="large"
              />
            </div>
          </div>
        ) : (
          renderTabAno(activeTab)
        )}
      </div>

      <div className="panel-footer-right">
        <button
          type="button"
          className="btn-green-action"
          onClick={handleGuardarCambios}
          disabled={saving}
        >
          {saving ? 'Guardando...' : 'Guardar Todos los Dividendos'}
        </button>
      </div>
    </div>
  );
};

