import React, { useMemo, useRef, useState } from 'react';
import { ArrowUp, ChevronDown, ChevronRight, ChevronsDownUp, ChevronsUpDown } from 'lucide-react';
import { SaldosPorAno } from '../types';

interface SaldosMensualesViewProps {
  datosPorAno: SaldosPorAno;
  onNavigateAddSaldo: () => void;
}

export const SaldosMensualesView: React.FC<SaldosMensualesViewProps> = ({
  datosPorAno,
  onNavigateAddSaldo
}) => {
  const scrollContainerRef = useRef<HTMLDivElement | null>(null);
  const yearRefs = useRef<Record<number, HTMLFieldSetElement | null>>({});
  const [anosPlegados, setAnosPlegados] = useState<Set<number>>(new Set());

  const togglePlegado = (ano: number) => {
    setAnosPlegados((prev) => {
      const next = new Set(prev);
      if (next.has(ano)) next.delete(ano);
      else next.add(ano);
      return next;
    });
  };

  const anosOrdenados = useMemo(() => {
    return Object.keys(datosPorAno)
      .map(Number)
      .filter((n) => !Number.isNaN(n))
      .sort((a, b) => a - b);
  }, [datosPorAno]);

  const { resumenAnual, granTotalIngresos, granTotalGastos, granTotalSaldo } = useMemo(() => {
    const res: Record<number, { ingresos: number; gastos: number; saldo: number }> = {};
    let gIng = 0;
    let gGas = 0;
    let gSal = 0;

    anosOrdenados.forEach((ano) => {
      const meses = datosPorAno[ano] || [];
      const tIng = meses.reduce((s, d) => s + d.ingresos, 0);
      const tGas = meses.reduce((s, d) => s + d.gastos, 0);
      const tSal = meses.reduce((s, d) => s + d.saldo, 0);
      res[ano] = { ingresos: tIng, gastos: tGas, saldo: tSal };
      gIng += tIng;
      gGas += tGas;
      gSal += tSal;
    });

    return {
      resumenAnual: res,
      granTotalIngresos: gIng,
      granTotalGastos: gGas,
      granTotalSaldo: gSal
    };
  }, [anosOrdenados, datosPorAno]);

  const plegarTodos = () => setAnosPlegados(new Set(anosOrdenados));
  const desplegarTodos = () => setAnosPlegados(new Set());

  const irAResumen = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    document
      .getElementById('resumen-anual-general')
      ?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const irAAno = (ano: number) => {
    const targetEl = yearRefs.current[ano];
    const containerEl = scrollContainerRef.current;
    if (targetEl && containerEl) {
      const topPos = targetEl.offsetTop - containerEl.offsetTop;
      containerEl.scrollTo({ top: topPos, behavior: 'smooth' });
    } else if (targetEl) {
      targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  if (anosOrdenados.length === 0) {
    return (
      <div className="panel-card text-center py-12">
        <h2>Saldos Mensuales</h2>
        <p className="empty-msg">No se encontraron datos en BalancesMensuales.csv</p>
        <button type="button" className="btn-green-action mt-4" onClick={onNavigateAddSaldo}>
          Añadir Nuevo Saldo Mensual
        </button>
      </div>
    );
  }

  return (
    <div className="panel-card saldos-view-wrapper">
      <div className="panel-header">
        <h2>
          Balances anuales del {anosOrdenados[0]} al {anosOrdenados[anosOrdenados.length - 1]}
        </h2>
        <button type="button" className="btn-primary" onClick={onNavigateAddSaldo}>
          Añadir Nuevo Saldo Mensual
        </button>
      </div>

      {/* Tabla Resumen Anual General */}
      <fieldset id="resumen-anual-general" className="tk-labelframe-large mb-4">
        <legend>Resumen Anual General</legend>
        <div className="table-scroll-container resumen-anual-scroll">
          <table className="tk-table">
            <thead>
              <tr className="tk-header-lightblue">
                <th className="text-left">AÑO</th>
                <th className="text-right">TOTAL INGRESOS</th>
                <th className="text-right">TOTAL GASTOS</th>
                <th className="text-right">TOTAL SALDO</th>
              </tr>
            </thead>
            <tbody>
              {anosOrdenados.map((ano) => {
                const tot = resumenAnual[ano];
                return (
                  <tr key={ano}>
                    <td className="text-left font-medium">{ano}</td>
                    <td className="text-right">{tot.ingresos.toFixed(2)}€</td>
                    <td className="text-right">{tot.gastos.toFixed(2)}€</td>
                    <td
                      className={`text-right font-semibold ${
                        tot.saldo < 0 ? 'text-red-700' : ''
                      }`}
                    >
                      {tot.saldo.toFixed(2)}€
                    </td>
                  </tr>
                );
              })}
              <tr>
                <td className="tk-cell-orange font-bold text-left">TOTAL</td>
                <td className="tk-cell-orange font-bold text-right">
                  {granTotalIngresos.toFixed(2)}€
                </td>
                <td className="tk-cell-orange font-bold text-right">
                  {granTotalGastos.toFixed(2)}€
                </td>
                <td className="tk-cell-orange font-bold text-right">
                  {granTotalSaldo.toFixed(2)}€
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </fieldset>

      {/* Índice superior "Ir al año:" */}
      <div className="saldos-indice-bar">
        <span className="saldos-indice-label">Ir al año:</span>
        <div className="saldos-indice-grid">
          {anosOrdenados.map((ano) => (
            <button
              key={ano}
              type="button"
              className="btn-year-jump"
              onClick={() => irAAno(ano)}
            >
              {ano}
            </button>
          ))}
        </div>
      </div>

      {/* Plegar / desplegar todos los años */}
      <div className="saldos-pliegue-toolbar">
        <button
          type="button"
          className="btn-secondary saldos-pliegue-btn"
          onClick={plegarTodos}
          disabled={anosPlegados.size === anosOrdenados.length}
        >
          <ChevronsDownUp size={16} aria-hidden="true" />
          Plegar todos
        </button>
        <button
          type="button"
          className="btn-secondary saldos-pliegue-btn"
          onClick={desplegarTodos}
          disabled={anosPlegados.size === 0}
        >
          <ChevronsUpDown size={16} aria-hidden="true" />
          Desplegar todos
        </button>
      </div>

      {/* Contenedor con scroll de todos los años */}
      <div ref={scrollContainerRef} className="saldos-anos-scroll-container">
        {anosOrdenados.map((ano) => {
          const meses = datosPorAno[ano] || [];
          const tot = resumenAnual[ano];
          const plegado = anosPlegados.has(ano);

          return (
            <fieldset
              key={ano}
              ref={(el) => {
                yearRefs.current[ano] = el;
              }}
              className="tk-labelframe-large mb-4"
            >
              <legend>
                <button
                  type="button"
                  className="saldos-toggle-ano"
                  aria-expanded={!plegado}
                  aria-controls={`saldos-ano-${ano}`}
                  onClick={() => togglePlegado(ano)}
                >
                  {plegado ? (
                    <ChevronRight size={18} aria-hidden="true" />
                  ) : (
                    <ChevronDown size={18} aria-hidden="true" />
                  )}
                  AÑO {ano}
                </button>
              </legend>
              <div className="saldos-ano-links">
                <a href="#resumen-anual-general" className="saldos-link-resumen" onClick={irAResumen}>
                  <ArrowUp size={14} aria-hidden="true" />
                  Ir a Resumen Anual General
                </a>
              </div>
              <table className="tk-table" id={`saldos-ano-${ano}`}>
                <thead>
                  <tr className="tk-header-lightblue">
                    <th className="text-left" style={{ width: '25%' }}>
                      MES
                    </th>
                    <th className="text-right" style={{ width: '25%' }}>
                      INGRESOS
                    </th>
                    <th className="text-right" style={{ width: '25%' }}>
                      GASTOS
                    </th>
                    <th className="text-right" style={{ width: '25%' }}>
                      SALDO
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {!plegado &&
                    meses.map((mesData, idx) => (
                    <tr key={`${ano}-${mesData.mes}-${idx}`}>
                      <td className="text-left">{mesData.mes}</td>
                      <td className="text-right">{mesData.ingresos.toFixed(2)}€</td>
                      <td className="text-right">{mesData.gastos.toFixed(2)}€</td>
                      <td
                        className={`text-right ${mesData.saldo < 0 ? 'text-red-700' : ''}`}
                      >
                        {mesData.saldo.toFixed(2)}€
                      </td>
                    </tr>
                  ))}
                  <tr>
                    <td className="tk-cell-orange font-bold text-left">TOTAL AÑO</td>
                    <td className="tk-cell-orange font-bold text-right">
                      {tot.ingresos.toFixed(2)}€
                    </td>
                    <td className="tk-cell-orange font-bold text-right">
                      {tot.gastos.toFixed(2)}€
                    </td>
                    <td className="tk-cell-orange font-bold text-right">
                      {tot.saldo.toFixed(2)}€
                    </td>
                  </tr>
                </tbody>
              </table>
            </fieldset>
          );
        })}
      </div>
    </div>
  );
};

