import React, { useMemo, useState } from 'react';
import {
  Asset,
  BROKERS,
  BROKERS_RESUMEN_ORDER,
  COLORES_BROKER,
  COLORES_TEXTO_TIPO_ACTIVO,
  COLORES_TIPO_ACTIVO,
  COLORES_TIPO_ACTIVO_CLARO,
  TIPOS_ACTIVO
} from '../types';
import { AssetBarChart, AssetPieChart } from './Charts';
import { obtenerPreciosActuales } from '../services/api';

interface VerCarteraViewProps {
  assets: Asset[];
  onUpdateAsset: (originalSymbol: string, updated: Asset) => Promise<void>;
  onDeleteAsset: (symbol: string) => Promise<void>;
  onBulkUpdateAssets: (updatedList: Asset[]) => Promise<void>;
  onNavigateAdd: () => void;
}

const ORDEN_TIPOS: Record<string, number> = {
  ACC: 0,
  ETF: 1,
  PP: 2,
  FON: 3
};

export const VerCarteraView: React.FC<VerCarteraViewProps> = ({
  assets,
  onUpdateAsset,
  onDeleteAsset,
  onBulkUpdateAssets,
  onNavigateAdd
}) => {
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);
  const [editCantidad, setEditCantidad] = useState('');
  const [editPrecio, setEditPrecio] = useState('');
  const [editDividendos, setEditDividendos] = useState(false);
  const [editTipo, setEditTipo] = useState('ACC');
  const [editBroker, setEditBroker] = useState('ocean');
  const [editError, setEditError] = useState<string | null>(null);

  const [deletingSymbol, setDeletingSymbol] = useState<string | null>(null);
  const [updatingPrices, setUpdatingPrices] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  type SortField = 'default' | 'titulo' | 'cantidad' | 'precio_actual' | 'importe_total' | 'porcentaje';
  type GroupByMode = 'none' | 'tipo' | 'broker';
  const [sortField, setSortField] = useState<SortField>('default');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [groupBy, setGroupBy] = useState<GroupByMode>('none');

  const handleSortClick = (field: Exclude<SortField, 'default'>) => {
    if (sortField !== field) {
      setSortField(field);
      setSortDir(field === 'titulo' ? 'asc' : 'desc');
    } else if (sortDir === (field === 'titulo' ? 'asc' : 'desc')) {
      setSortDir(field === 'titulo' ? 'desc' : 'asc');
    } else {
      setSortField('default');
      setSortDir('asc');
    }
  };

  const handleGroupToggle = (mode: 'tipo' | 'broker') => {
    setGroupBy((prev) => (prev === mode ? 'none' : mode));
  };

  const getSortIndicator = (field: Exclude<SortField, 'default'>) => {
    if (sortField !== field) return ' ⇅';
    return sortDir === 'asc' ? ' ▲' : ' ▼';
  };

  const compareAssets = (a: Asset, b: Asset) => {
    if (sortField === 'titulo') {
      const cmp = a.titulo.localeCompare(b.titulo, 'es', { sensitivity: 'base' });
      return sortDir === 'asc' ? cmp : -cmp;
    }
    if (sortField === 'cantidad') {
      const diff = a.cantidad - b.cantidad;
      return sortDir === 'asc' ? diff : -diff;
    }
    if (sortField === 'precio_actual') {
      const diff = a.precio_actual - b.precio_actual;
      return sortDir === 'asc' ? diff : -diff;
    }
    if (sortField === 'importe_total' || sortField === 'porcentaje') {
      const diff = a.importe_total - b.importe_total;
      return sortDir === 'asc' ? diff : -diff;
    }

    const oa = ORDEN_TIPOS[a.tipo_activo] ?? 99;
    const ob = ORDEN_TIPOS[b.tipo_activo] ?? 99;
    if (oa !== ob) return oa - ob;
    return a.simbolo.localeCompare(b.simbolo);
  };

  const sortedAssets = useMemo(() => {
    return [...assets].sort(compareAssets);
  }, [assets, sortField, sortDir]);

  const groupedSections = useMemo(() => {
    if (groupBy === 'none') {
      return [{ key: 'all', label: '', items: sortedAssets }];
    }
    if (groupBy === 'tipo') {
      const keys = Array.from(new Set([...TIPOS_ACTIVO, ...assets.map((a) => a.tipo_activo)]));
      return keys
        .map((k) => ({
          key: k,
          label: `TIPO: ${k}`,
          items: sortedAssets.filter((a) => a.tipo_activo === k)
        }))
        .filter((g) => g.items.length > 0);
    }
    // groupBy === 'broker'
    const keys = Array.from(new Set([...BROKERS, ...assets.map((a) => a.broker)]));
    return keys
      .map((k) => ({
        key: k,
        label: `BROKER: ${k.toUpperCase()}`,
        items: sortedAssets.filter((a) => a.broker === k)
      }))
      .filter((g) => g.items.length > 0);
  }, [assets, sortedAssets, groupBy]);

  const totalGeneral = useMemo(
    () => assets.reduce((sum, item) => sum + item.importe_total, 0),
    [assets]
  );

  const totalAcciones = useMemo(
    () => assets.reduce((sum, item) => sum + item.cantidad, 0),
    [assets]
  );

  const maxMetrics = useMemo(() => {
    if (assets.length === 0) {
      return { maxCantidad: 0, maxPrecio: 0, maxImporte: 0 };
    }
    return {
      maxCantidad: Math.max(...assets.map((a) => a.cantidad)),
      maxPrecio: Math.max(...assets.map((a) => a.precio_actual)),
      maxImporte: Math.max(...assets.map((a) => a.importe_total))
    };
  }, [assets]);

  const totalesTipo = useMemo(() => {
    const map: Record<string, number> = {};
    TIPOS_ACTIVO.forEach((tipo) => {
      map[tipo] = assets
        .filter((a) => a.tipo_activo === tipo)
        .reduce((s, a) => s + a.importe_total, 0);
    });
    return map;
  }, [assets]);

  const totalesBroker = useMemo(() => {
    const map: Record<string, number> = {};
    BROKERS_RESUMEN_ORDER.forEach((b) => {
      map[b] = assets
        .filter((a) => a.broker === b)
        .reduce((s, a) => s + a.importe_total, 0);
    });
    return map;
  }, [assets]);

  const totalesTipoCant = useMemo(() => {
    const map: Record<string, number> = {};
    TIPOS_ACTIVO.forEach((tipo) => {
      map[tipo] = assets
        .filter((a) => a.tipo_activo === tipo)
        .reduce((s, a) => s + a.cantidad, 0);
    });
    return map;
  }, [assets]);

  const totalesBrokerCant = useMemo(() => {
    const map: Record<string, number> = {};
    BROKERS_RESUMEN_ORDER.forEach((b) => {
      map[b] = assets
        .filter((a) => a.broker === b)
        .reduce((s, a) => s + a.cantidad, 0);
    });
    return map;
  }, [assets]);

  const chartItems = useMemo(() => {
    return TIPOS_ACTIVO.map((tipo) => ({
      label: tipo,
      value: totalesTipo[tipo] || 0,
      color: COLORES_TIPO_ACTIVO[tipo] || '#ffffff'
    }));
  }, [totalesTipo]);

  const openEditModal = (asset: Asset) => {
    setEditingAsset(asset);
    setEditCantidad(String(asset.cantidad));
    setEditPrecio(String(asset.precio_actual));
    setEditDividendos(asset.dividendos === 'Sí');
    setEditTipo(asset.tipo_activo);
    setEditBroker(asset.broker);
    setEditError(null);
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingAsset) return;

    if (!/^\d+$/.test(editCantidad.trim())) {
      setEditError('La cantidad debe ser un número entero válido.');
      return;
    }
    const nuevaCantidad = parseInt(editCantidad.trim(), 10);
    const nuevoPrecio = parseFloat(editPrecio.replace(',', '.'));
    if (Number.isNaN(nuevoPrecio)) {
      setEditError('El precio debe ser un número válido.');
      return;
    }

    const updated: Asset = {
      ...editingAsset,
      cantidad: nuevaCantidad,
      precio_actual: nuevoPrecio,
      dividendos: editDividendos ? 'Sí' : 'No',
      tipo_activo: editTipo,
      broker: editBroker,
      importe_total: nuevaCantidad * nuevoPrecio
    };

    await onUpdateAsset(editingAsset.simbolo, updated);
    setEditingAsset(null);
    setStatusMessage(`Elemento "${editingAsset.simbolo}" editado correctamente.`);
    setTimeout(() => setStatusMessage(null), 3500);
  };

  const handleConfirmDelete = async () => {
    if (!deletingSymbol) return;
    const sym = deletingSymbol;
    await onDeleteAsset(sym);
    setDeletingSymbol(null);
    setStatusMessage(`Elemento "${sym}" eliminado.`);
    setTimeout(() => setStatusMessage(null), 3500);
  };

  const handleRefreshMarketPrices = async () => {
    if (assets.length === 0) return;
    setUpdatingPrices(true);
    setStatusMessage(null);
    try {
      const symbols = assets.map((a) => a.simbolo);
      const precios = await obtenerPreciosActuales(symbols);
      let updatedCount = 0;
      const newAssets = assets.map((asset) => {
        const nuevoPrecio = precios[asset.simbolo];
        if (nuevoPrecio && nuevoPrecio > 0) {
          updatedCount++;
          return {
            ...asset,
            precio_actual: nuevoPrecio,
            importe_total: asset.cantidad * nuevoPrecio
          };
        }
        return asset;
      });
      if (updatedCount > 0) {
        await onBulkUpdateAssets(newAssets);
        setStatusMessage(`Cotizaciones actualizadas para ${updatedCount} activos.`);
      } else {
        setStatusMessage('No se encontraron nuevos precios en Yahoo Finance (se mantienen los actuales).');
      }
    } finally {
      setUpdatingPrices(false);
      setTimeout(() => setStatusMessage(null), 4000);
    }
  };

  if (assets.length === 0) {
    return (
      <div className="panel-card text-center py-12">
        <h2>Ver Cartera</h2>
        <p className="empty-msg">No hay elementos en la cartera.</p>
        <button type="button" className="btn-green-action mt-4" onClick={onNavigateAdd}>
          Añadir Nuevos Activos
        </button>
      </div>
    );
  }

  return (
    <div className="cartera-view-container">
      <div className="panel-header">
        <h2>Ver Cartera</h2>
        <div className="header-actions">
          <div className="group-by-toolbar">
            <span className="group-by-label">Agrupar:</span>
            <button
              type="button"
              className={`btn-group-toggle ${groupBy === 'none' ? 'active' : ''}`}
              onClick={() => setGroupBy('none')}
            >
              Sin agrupar
            </button>
            <button
              type="button"
              className={`btn-group-toggle ${groupBy === 'tipo' ? 'active' : ''}`}
              onClick={() => handleGroupToggle('tipo')}
            >
              Por Tipo
            </button>
            <button
              type="button"
              className={`btn-group-toggle ${groupBy === 'broker' ? 'active' : ''}`}
              onClick={() => handleGroupToggle('broker')}
            >
              Por Broker
            </button>
          </div>
          <button
            type="button"
            className="btn-secondary"
            onClick={handleRefreshMarketPrices}
            disabled={updatingPrices}
          >
            {updatingPrices ? 'Actualizando precios...' : 'Actualizar Precios (Yahoo Finance)'}
          </button>
          <button type="button" className="btn-primary" onClick={onNavigateAdd}>
            Añadir Nuevos Activos
          </button>
        </div>
      </div>

      {statusMessage && <div className="alert-banner alert-success">{statusMessage}</div>}

      {/* Tabla principal de Cartera */}
      <div className="table-scroll-container cartera-table-scroll">
        <table className="tk-table cartera-table">
          <thead>
            <tr className="tk-header-darkgray">
              <th className="text-center">SIMBOLO</th>
              <th
                className="text-left tk-sortable-th"
                onClick={() => handleSortClick('titulo')}
                title="Ordenar por Título"
              >
                TITULO{getSortIndicator('titulo')}
              </th>
              <th
                className="text-center tk-sortable-th"
                onClick={() => handleSortClick('cantidad')}
                title="Ordenar por Cantidad"
              >
                CANTIDAD{getSortIndicator('cantidad')}
              </th>
              <th
                className="text-center tk-sortable-th"
                onClick={() => handleSortClick('precio_actual')}
                title="Ordenar por Precio"
              >
                PRECIO{getSortIndicator('precio_actual')}
              </th>
              <th
                className="text-center tk-sortable-th"
                onClick={() => handleSortClick('importe_total')}
                title="Ordenar por Importe"
              >
                IMPORTE{getSortIndicator('importe_total')}
              </th>
              <th
                className="text-center tk-sortable-th"
                onClick={() => handleSortClick('porcentaje')}
                title="Ordenar por %"
              >
                %{getSortIndicator('porcentaje')}
              </th>
              <th
                className="text-center tk-sortable-th"
                onClick={() => handleGroupToggle('tipo')}
                title="Agrupar por Tipo"
              >
                TIPO{groupBy === 'tipo' ? ' (Agrupado)' : ''}
              </th>
              <th
                className="text-center tk-sortable-th"
                onClick={() => handleGroupToggle('broker')}
                title="Agrupar por Broker"
              >
                BROKER{groupBy === 'broker' ? ' (Agrupado)' : ''}
              </th>
              <th className="text-center" colSpan={2}>
                MODIFICAR
              </th>
            </tr>
          </thead>
          <tbody>
            {groupedSections.map((section) => {
              const groupCantidad = section.items.reduce((s, a) => s + a.cantidad, 0);
              const groupImporte = section.items.reduce((s, a) => s + a.importe_total, 0);
              const groupPct = totalGeneral > 0 ? (groupImporte / totalGeneral) * 100 : 0;

              return (
                <React.Fragment key={section.key}>
                  {groupBy !== 'none' && (
                    <tr className="tk-group-header-row">
                      <td colSpan={2} className="text-left font-bold">
                        {section.label} ({section.items.length} posiciones)
                      </td>
                      <td className="text-center font-bold">{groupCantidad}</td>
                      <td className="text-center">—</td>
                      <td className="text-center font-bold">{groupImporte.toFixed(2)}€</td>
                      <td className="text-center font-bold">{groupPct.toFixed(2)}%</td>
                      <td colSpan={4}></td>
                    </tr>
                  )}
                  {section.items.map((row) => {
                    const bgColor = COLORES_TIPO_ACTIVO[row.tipo_activo] || '#ffffff';
                    const bgImporteColor =
                      COLORES_TIPO_ACTIVO_CLARO[row.tipo_activo] || '#ffffff';
                    const tipoTextColor = COLORES_TEXTO_TIPO_ACTIVO[row.tipo_activo];
                    const brokerStyle = COLORES_BROKER[row.broker.toLowerCase()];
                    const porcentaje =
                      totalGeneral > 0 ? (row.importe_total / totalGeneral) * 100 : 0;

                    const isMaxCantidad =
                      maxMetrics.maxCantidad > 0 && row.cantidad === maxMetrics.maxCantidad;
                    const isMaxPrecio =
                      maxMetrics.maxPrecio > 0 && row.precio_actual === maxMetrics.maxPrecio;
                    const isMaxImporte =
                      maxMetrics.maxImporte > 0 && row.importe_total === maxMetrics.maxImporte;
                    const isMaxPorcentaje = isMaxImporte;
                    const isDarkRow = row.tipo_activo === 'FON';

                    return (
                      <tr
                        key={row.simbolo}
                        style={{
                          backgroundColor: bgColor,
                          color: isDarkRow ? '#ffffff' : undefined
                        }}
                      >
                        <td className="text-center font-mono font-semibold">{row.simbolo}</td>
                        <td className="text-left">{row.titulo}</td>
                        <td
                          className={`text-center ${
                            isMaxCantidad ? 'tk-cell-max-highlight' : ''
                          }`}
                        >
                          {row.cantidad}
                        </td>
                        <td
                          className={`text-center ${
                            isMaxPrecio ? 'tk-cell-max-highlight' : ''
                          }`}
                        >
                          {row.precio_actual}
                        </td>
                        <td
                          className={`text-center font-semibold ${
                            isMaxImporte ? 'tk-cell-max-highlight' : ''
                          }`}
                          style={{ backgroundColor: bgImporteColor, color: '#0f172a' }}
                        >
                          {row.importe_total.toFixed(2)}
                        </td>
                        <td
                          className={`text-center ${
                            isMaxPorcentaje ? 'tk-cell-max-highlight' : ''
                          }`}
                        >
                          {porcentaje.toFixed(2)}%
                        </td>
                        <td
                          className="text-center font-bold"
                          style={tipoTextColor ? { color: tipoTextColor } : undefined}
                        >
                          {row.tipo_activo}
                        </td>
                        <td
                          className="text-center font-semibold"
                          style={
                            brokerStyle
                              ? { backgroundColor: brokerStyle.bg, color: brokerStyle.fg }
                              : undefined
                          }
                        >
                          {row.broker}
                        </td>
                        <td
                          className="text-center action-cell"
                          style={{ backgroundColor: '#ffffff' }}
                        >
                          <button
                            type="button"
                            className="btn-table-action"
                            onClick={() => openEditModal(row)}
                          >
                            Editar
                          </button>
                        </td>
                        <td
                          className="text-center action-cell"
                          style={{ backgroundColor: '#ffffff' }}
                        >
                          <button
                            type="button"
                            className="btn-table-action btn-table-danger"
                            onClick={() => setDeletingSymbol(row.simbolo)}
                          >
                            Eliminar
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Sección inferior: Gráficos (izquierda) y Resúmenes (derecha) */}
      <div className="cartera-bottom-grid">
        <div className="cartera-charts-area">
          <AssetBarChart
            title="Importe por Tipo de Activo"
            yAxisLabel="Importe (€)"
            items={chartItems}
            formatValueLabel={(val) => `${val.toFixed(0)}€`}
          />
          <AssetPieChart
            title="Distribución por Tipo de Activo"
            items={chartItems}
            showCurrencyInSlice={false}
            startAngleDeg={140}
          />
        </div>

        <div className="cartera-summaries-area">
          {/* Bloque Importe Total */}
          <div className="summary-section">
            <div className="summary-headline-red">
              IMPORTE TOTAL: {totalGeneral.toFixed(2)}€
            </div>
            <div className="summary-boxes-row">
              <fieldset className="tk-labelframe">
                <legend>Totales por Tipo</legend>
                {TIPOS_ACTIVO.map((tipo) => {
                  const total = totalesTipo[tipo] || 0;
                  if (total <= 0) return null;
                  return (
                    <div key={tipo} className="summary-line">
                      <strong>{tipo}:</strong> {total.toFixed(2)}€
                    </div>
                  );
                })}
              </fieldset>

              <fieldset className="tk-labelframe">
                <legend>Totales por Broker</legend>
                {BROKERS_RESUMEN_ORDER.map((broker) => {
                  const total = totalesBroker[broker] || 0;
                  if (total <= 0) return null;
                  return (
                    <div key={broker} className="summary-line">
                      <strong>{broker}:</strong> {total.toFixed(2)}€
                    </div>
                  );
                })}
              </fieldset>
            </div>
          </div>

          {/* Bloque Total Acciones */}
          <div className="summary-section">
            <div className="summary-headline-blue">TOTAL ACCIONES: {totalAcciones}</div>
            <div className="summary-boxes-row">
              <fieldset className="tk-labelframe">
                <legend>Acciones por Tipo</legend>
                {TIPOS_ACTIVO.map((tipo) => {
                  const total = totalesTipoCant[tipo] || 0;
                  if (total <= 0) return null;
                  return (
                    <div key={tipo} className="summary-line">
                      <strong>{tipo}:</strong> {total}
                    </div>
                  );
                })}
              </fieldset>

              <fieldset className="tk-labelframe">
                <legend>Acciones por Broker</legend>
                {BROKERS_RESUMEN_ORDER.map((broker) => {
                  const total = totalesBrokerCant[broker] || 0;
                  if (total <= 0) return null;
                  return (
                    <div key={broker} className="summary-line">
                      <strong>{broker}:</strong> {total}
                    </div>
                  );
                })}
              </fieldset>
            </div>
          </div>
        </div>
      </div>

      {/* Modal Editar Elemento */}
      {editingAsset && (
        <div className="modal-backdrop" onClick={() => setEditingAsset(null)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                Editar elemento: {editingAsset.simbolo} ({editingAsset.titulo})
              </h3>
              <button
                type="button"
                className="modal-close"
                onClick={() => setEditingAsset(null)}
              >
                ×
              </button>
            </div>
            {editError && <div className="alert-banner alert-error">{editError}</div>}
            <form onSubmit={handleSaveEdit} className="modal-form">
              <div className="form-group">
                <label>Cantidad:</label>
                <input
                  type="number"
                  min="1"
                  step="1"
                  value={editCantidad}
                  onChange={(e) => setEditCantidad(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Precio actual:</label>
                <input
                  type="number"
                  step="any"
                  value={editPrecio}
                  onChange={(e) => setEditPrecio(e.target.value)}
                />
              </div>
              <div className="form-group checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={editDividendos}
                    onChange={(e) => setEditDividendos(e.target.checked)}
                  />
                  <span>Tiene dividendos</span>
                </label>
              </div>
              <div className="form-group">
                <label>Tipo de activo:</label>
                <select value={editTipo} onChange={(e) => setEditTipo(e.target.value)}>
                  {TIPOS_ACTIVO.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Broker:</label>
                <select value={editBroker} onChange={(e) => setEditBroker(e.target.value)}>
                  {BROKERS.map((b) => (
                    <option key={b} value={b}>
                      {b}
                    </option>
                  ))}
                </select>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setEditingAsset(null)}
                >
                  Cancelar
                </button>
                <button type="submit" className="btn-green-action">
                  Guardar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Confirmar Eliminación */}
      {deletingSymbol && (
        <div className="modal-backdrop" onClick={() => setDeletingSymbol(null)}>
          <div className="modal-dialog modal-sm" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Confirmar</h3>
              <button
                type="button"
                className="modal-close"
                onClick={() => setDeletingSymbol(null)}
              >
                ×
              </button>
            </div>
            <p className="py-4">
              ¿Está seguro de que desea eliminar el elemento <strong>{deletingSymbol}</strong>?
            </p>
            <div className="modal-footer">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setDeletingSymbol(null)}
              >
                No
              </button>
              <button
                type="button"
                className="btn-danger"
                onClick={handleConfirmDelete}
              >
                Sí, eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

