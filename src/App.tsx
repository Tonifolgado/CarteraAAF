import React, { useEffect, useState } from 'react';
import {
  ActiveView,
  Asset,
  DividendosData,
  PatrimonioData,
  SaldosPorAno
} from './types';
import {
  addSaldoMensual,
  fetchCartera,
  fetchDividendos,
  fetchPatrimonio,
  fetchSaldosMensuales,
  saveCartera,
  saveDividendos,
  savePatrimonio
} from './services/api';
import { HomeMenu } from './components/HomeMenu';
import { AgregarActivoView } from './components/AgregarActivoView';
import { VerCarteraView } from './components/VerCarteraView';
import { DividendosView } from './components/DividendosView';
import { AgregarSaldoView } from './components/AgregarSaldoView';
import { SaldosMensualesView } from './components/SaldosMensualesView';
import { PatrimonioView } from './components/PatrimonioView';

export const App: React.FC = () => {
  const [activeView, setActiveView] = useState<ActiveView>('menu');
  const [assets, setAssets] = useState<Asset[]>([]);
  const [dividendosData, setDividendosData] = useState<DividendosData>({});
  const [patrimonioData, setPatrimonioData] = useState<PatrimonioData>({});
  const [saldosPorAno, setSaldosPorAno] = useState<SaldosPorAno>({});
  const [loading, setLoading] = useState(true);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [carteraRes, divRes, patRes, saldosRes] = await Promise.all([
        fetchCartera(),
        fetchDividendos(),
        fetchPatrimonio(),
        fetchSaldosMensuales()
      ]);
      setAssets(carteraRes);
      setDividendosData(divRes);
      setPatrimonioData(patRes);
      setSaldosPorAno(saldosRes);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  const handleGoHomeAndRefresh = async () => {
    setActiveView('menu');
    await loadAllData();
  };

  const handleAddAsset = async (newAsset: Asset) => {
    const next = [...assets, newAsset];
    setAssets(next);
    await saveCartera(next);
  };

  const handleUpdateAsset = async (originalSymbol: string, updatedAsset: Asset) => {
    const next = assets.map((a) => (a.simbolo === originalSymbol ? updatedAsset : a));
    setAssets(next);
    await saveCartera(next);
  };

  const handleDeleteAsset = async (symbol: string) => {
    const next = assets.filter((a) => a.simbolo !== symbol);
    setAssets(next);
    await saveCartera(next);
  };

  const handleBulkUpdateAssets = async (updatedList: Asset[]) => {
    setAssets(updatedList);
    await saveCartera(updatedList);
  };

  const handleSaveDividendos = async (updated: DividendosData) => {
    setDividendosData(updated);
    await saveDividendos(updated);
  };

  const handleAddSaldo = async (
    ano: string,
    mes: string,
    ingresos: number,
    gastos: number
  ) => {
    const updatedSaldos = await addSaldoMensual(ano, mes, ingresos, gastos);
    setSaldosPorAno(updatedSaldos);
  };

  const handleSavePatrimonio = async (updated: PatrimonioData) => {
    setPatrimonioData(updated);
    await savePatrimonio(updated);
  };

  const mainNavItems: Array<{ id: ActiveView; label: string; color: string }> = [
    { id: 'menu', label: 'Inicio', color: '#e2e8f0' },
    { id: 'ver_cartera', label: 'Ver Cartera', color: '#90EE90' },
    { id: 'dividendos', label: 'Ver Dividendos', color: '#FFFFE0' },
    { id: 'saldos_mensuales', label: 'Saldos Mensuales', color: '#F08080' },
    { id: 'patrimonio', label: 'Patrimonio', color: '#B0C4DE' }
  ];

  const addNavItems: Array<{ id: ActiveView; label: string; color: string }> = [
    { id: 'agregar_activos', label: 'Añadir Activos', color: '#ADD8E6' },
    { id: 'agregar_saldo', label: 'Añadir Saldo Mensual', color: '#87CEFA' }
  ];

  return (
    <div className="app-shell">
      {/* Barra de navegación superior */}
      <header className="top-navbar">
        <div className="top-navbar-row-main">
          <div
            className="brand-title"
            onClick={handleGoHomeAndRefresh}
            role="button"
            tabIndex={0}
          >
            Gestor de Cartera AAF
          </div>
          <nav className="top-nav-links">
            {mainNavItems.map((item) => {
              const isHome = item.id === 'menu';
              return (
                <button
                  key={item.id}
                  type="button"
                  className={`nav-pill-btn ${isHome ? 'nav-pill-btn-home' : ''} ${
                    activeView === item.id ? 'active' : ''
                  }`}
                  style={{
                    backgroundColor: activeView === item.id ? item.color : undefined,
                    borderBottomColor: item.color
                  }}
                  onClick={() => {
                    if (isHome) {
                      handleGoHomeAndRefresh();
                    } else {
                      setActiveView(item.id);
                    }
                  }}
                >
                  {item.label}
                </button>
              );
            })}
          </nav>
        </div>
        <div className="top-navbar-row-sub">
          {addNavItems.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`nav-pill-btn ${activeView === item.id ? 'active' : ''}`}
              style={{
                backgroundColor: activeView === item.id ? item.color : undefined,
                borderBottomColor: item.color
              }}
              onClick={() => setActiveView(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>
      </header>

      {/* Contenido Principal */}
      <main className="main-content">
        {loading ? (
          <div className="loading-state">Cargando datos de la cartera...</div>
        ) : (
          <>
            {activeView === 'menu' && (
              <HomeMenu
                onSelectView={setActiveView}
                assets={assets}
                saldosPorAno={saldosPorAno}
              />
            )}

            {activeView === 'agregar_activos' && (
              <AgregarActivoView
                onAddAsset={handleAddAsset}
                onNavigateCartera={() => setActiveView('ver_cartera')}
              />
            )}

            {activeView === 'ver_cartera' && (
              <VerCarteraView
                assets={assets}
                onUpdateAsset={handleUpdateAsset}
                onDeleteAsset={handleDeleteAsset}
                onBulkUpdateAssets={handleBulkUpdateAssets}
                onNavigateAdd={() => setActiveView('agregar_activos')}
              />
            )}

            {activeView === 'dividendos' && (
              <DividendosView
                assets={assets}
                dividendosData={dividendosData}
                onSaveDividendos={handleSaveDividendos}
              />
            )}

            {activeView === 'agregar_saldo' && (
              <AgregarSaldoView
                onAddSaldo={handleAddSaldo}
                onNavigateSaldos={() => setActiveView('saldos_mensuales')}
              />
            )}

            {activeView === 'saldos_mensuales' && (
              <SaldosMensualesView
                datosPorAno={saldosPorAno}
                onNavigateAddSaldo={() => setActiveView('agregar_saldo')}
              />
            )}

            {activeView === 'patrimonio' && (
              <PatrimonioView
                patrimonioData={patrimonioData}
                onSavePatrimonio={handleSavePatrimonio}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
};

export default App;

