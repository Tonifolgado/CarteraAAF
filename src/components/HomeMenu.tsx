import React from 'react';
import { ActiveView, Asset, SaldosPorAno } from '../types';

interface HomeMenuProps {
  onSelectView: (view: ActiveView) => void;
  assets: Asset[];
  saldosPorAno: SaldosPorAno;
}

export const HomeMenu: React.FC<HomeMenuProps> = ({
  onSelectView,
  assets,
  saldosPorAno
}) => {
  const totalCartera = assets.reduce((s, a) => s + a.importe_total, 0);
  const numActivosDividendos = assets.filter((a) => a.dividendos === 'Sí').length;
  const anosList = Object.keys(saldosPorAno)
    .map(Number)
    .filter((n) => !Number.isNaN(n))
    .sort((a, b) => a - b);
  const totalAnosSaldos = anosList.length;
  const rangoAnos =
    anosList.length > 0 ? ` (${anosList[0]}–${anosList[anosList.length - 1]})` : '';

  return (
    <div className="home-menu-card">
      <h1 className="home-title">Gestor de Cartera AAF</h1>

      {/* Fila superior de botones de adición directamente bajo el título como en iniciar_gui() */}
      <div className="home-row-two">
        <button
          type="button"
          className="tk-main-btn"
          style={{ backgroundColor: '#ADD8E6' }}
          onClick={() => onSelectView('agregar_activos')}
        >
          Añadir Nuevos Activos
        </button>

        <button
          type="button"
          className="tk-main-btn"
          style={{ backgroundColor: '#87CEFA' }}
          onClick={() => onSelectView('agregar_saldo')}
        >
          Añadir Nuevo Saldo Mensual
        </button>
      </div>

      {/* Columna central de vistas principales como en iniciar_gui() */}
      <div className="home-col-stack">
        <button
          type="button"
          className="tk-main-btn"
          style={{ backgroundColor: '#90EE90' }}
          onClick={() => onSelectView('ver_cartera')}
        >
          Ver Cartera
        </button>

        <button
          type="button"
          className="tk-main-btn"
          style={{ backgroundColor: '#FFFFE0' }}
          onClick={() => onSelectView('dividendos')}
        >
          Ver Dividendos
        </button>

        <button
          type="button"
          className="tk-main-btn"
          style={{ backgroundColor: '#F08080' }}
          onClick={() => onSelectView('saldos_mensuales')}
        >
          Saldos Mensuales
        </button>

        <button
          type="button"
          className="tk-main-btn"
          style={{ backgroundColor: '#B0C4DE' }}
          onClick={() => onSelectView('patrimonio')}
        >
          Patrimonio
        </button>
      </div>

      <div className="home-kpis mt-6">
        <div className="home-kpi-pill">
          <span className="kpi-label">Activos en Cartera:</span>
          <span className="kpi-val">{assets.length}</span>
        </div>
        <div className="home-kpi-pill">
          <span className="kpi-label">Importe Total Cartera:</span>
          <span className="kpi-val text-red-700">{totalCartera.toFixed(2)} €</span>
        </div>
        <div className="home-kpi-pill">
          <span className="kpi-label">Activos con Dividendos:</span>
          <span className="kpi-val">{numActivosDividendos}</span>
        </div>
        <div className="home-kpi-pill">
          <span className="kpi-label">Años de Balances:</span>
          <span className="kpi-val">
            {totalAnosSaldos}
            {rangoAnos}
          </span>
        </div>
      </div>
    </div>
  );
};

