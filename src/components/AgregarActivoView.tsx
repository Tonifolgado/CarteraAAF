import React, { useState } from 'react';
import { Asset, BROKERS, TIPOS_ACTIVO } from '../types';
import { obtenerPreciosActuales } from '../services/api';

interface AgregarActivoViewProps {
  onAddAsset: (asset: Asset) => Promise<void>;
  onNavigateCartera: () => void;
}

export const AgregarActivoView: React.FC<AgregarActivoViewProps> = ({
  onAddAsset,
  onNavigateCartera
}) => {
  const [simbolo, setSimbolo] = useState('');
  const [titulo, setTitulo] = useState('');
  const [cantidad, setCantidad] = useState('');
  const [precioManual, setPrecioManual] = useState('');
  const [tipoActivo, setTipoActivo] = useState<string>('');
  const [dividendos, setDividendos] = useState(false);
  const [broker, setBroker] = useState<string>('');
  const [comision, setComision] = useState('0.0');
  const [loadingPrice, setLoadingPrice] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; msg: string } | null>(
    null
  );

  const cantNum = parseFloat(cantidad || '0');
  const precNum = parseFloat(precioManual || '0');
  const comisNum = parseFloat(comision || '0');
  const precioFinalPreview =
    !Number.isNaN(cantNum) && !Number.isNaN(precNum) && !Number.isNaN(comisNum)
      ? ((cantNum * precNum) + comisNum).toFixed(2)
      : '0.00';

  const handleConsultarYahoo = async () => {
    const sym = simbolo.trim();
    if (!sym) {
      setFeedback({ type: 'error', msg: 'Introduce primero un símbolo para consultar en Yahoo Finance.' });
      return;
    }
    setLoadingPrice(true);
    setFeedback(null);
    try {
      const precios = await obtenerPreciosActuales([sym]);
      const p = precios[sym] || 0.0;
      if (p > 0) {
        setPrecioManual(p.toString());
        setFeedback({
          type: 'success',
          msg: `Precio actual obtenido de Yahoo Finance para ${sym}: ${p} €`
        });
      } else {
        setFeedback({
          type: 'error',
          msg: `No se pudo obtener el precio automático para '${sym}'. Puedes introducir el precio manual.`
        });
      }
    } finally {
      setLoadingPrice(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback(null);

    const sym = simbolo.trim();
    const tit = titulo.trim();
    const cantStr = cantidad.trim();
    const precManStr = precioManual.trim();

    if (!sym || !tit || !/^\d+$/.test(cantStr)) {
      setFeedback({
        type: 'error',
        msg: 'Campos obligatorios incompletos o inválidos (Símbolo, Título y Cantidad entera).'
      });
      return;
    }

    const cantInt = parseInt(cantStr, 10);
    const comisFloat = parseFloat(comision || '0.0');
    if (Number.isNaN(comisFloat)) {
      setFeedback({ type: 'error', msg: 'La comisión debe ser un número válido.' });
      return;
    }

    setLoadingPrice(true);
    let precioActual = 0.0;
    try {
      const preciosActuales = await obtenerPreciosActuales([sym]);
      precioActual = preciosActuales[sym] || 0.0;
    } finally {
      setLoadingPrice(false);
    }

    if (precioActual === 0.0) {
      if (!precManStr) {
        setFeedback({
          type: 'error',
          msg: 'El precio no se encontró en Yahoo Finance y no se ingresó manualmente.'
        });
        return;
      }
      const parsedManual = parseFloat(precManStr.replace(',', '.'));
      if (Number.isNaN(parsedManual) || parsedManual <= 0) {
        setFeedback({ type: 'error', msg: 'El precio ingresado manualmente no es válido.' });
        return;
      }
      precioActual = parsedManual;
    }

    const precioFinal = cantInt * precioActual + comisFloat;

    const nuevoAsset: Asset = {
      simbolo: sym,
      titulo: tit,
      cantidad: cantInt,
      precio_actual: precioActual,
      importe_total: precioFinal,
      dividendos: dividendos ? 'Sí' : 'No',
      tipo_activo: tipoActivo || 'ACC',
      broker: broker || 'ocean'
    };

    await onAddAsset(nuevoAsset);
    setFeedback({ type: 'success', msg: 'Elemento añadido a la cartera correctamente.' });

    // Reset form as in Python
    setSimbolo('');
    setTitulo('');
    setCantidad('');
    setPrecioManual('');
    setComision('0.0');
    setDividendos(false);
    setTipoActivo('');
    setBroker('');
  };

  return (
    <div className="panel-card max-w-700 mx-auto">
      <div className="panel-header">
        <h2>Agregar Nuevos Activos</h2>
        <button type="button" className="btn-secondary" onClick={onNavigateCartera}>
          Ir a Ver Cartera
        </button>
      </div>

      {feedback && (
        <div className={`alert-banner ${feedback.type === 'error' ? 'alert-error' : 'alert-success'}`}>
          {feedback.msg}
        </div>
      )}

      <form onSubmit={handleSubmit} className="form-grid-2col">
        <div className="form-group">
          <label htmlFor="simbolo">Símbolo:</label>
          <div className="input-with-btn">
            <input
              id="simbolo"
              type="text"
              value={simbolo}
              onChange={(e) => setSimbolo(e.target.value)}
              placeholder="Ej. AAPL, IBE.MC, ENO"
            />
            <button
              type="button"
              className="btn-small"
              onClick={handleConsultarYahoo}
              disabled={loadingPrice}
              title="Consultar precio actual en Yahoo Finance"
            >
              {loadingPrice ? '...' : 'Cotización YF'}
            </button>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="titulo">Título:</label>
          <input
            id="titulo"
            type="text"
            value={titulo}
            onChange={(e) => setTitulo(e.target.value)}
            placeholder="Nombre descriptivo del activo"
          />
        </div>

        <div className="form-group">
          <label htmlFor="cantidad">Cantidad:</label>
          <input
            id="cantidad"
            type="number"
            min="1"
            step="1"
            value={cantidad}
            onChange={(e) => setCantidad(e.target.value)}
            placeholder="0"
          />
        </div>

        <div className="form-group">
          <label htmlFor="precio_manual">Precio manual (€):</label>
          <input
            id="precio_manual"
            type="number"
            step="any"
            value={precioManual}
            onChange={(e) => setPrecioManual(e.target.value)}
            placeholder="Opcional si está en Yahoo Finance"
          />
        </div>

        <div className="form-group">
          <label htmlFor="tipo_activo">Tipo:</label>
          <select
            id="tipo_activo"
            value={tipoActivo}
            onChange={(e) => setTipoActivo(e.target.value)}
          >
            <option value="">-- Seleccionar --</option>
            {TIPOS_ACTIVO.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group checkbox-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={dividendos}
              onChange={(e) => setDividendos(e.target.checked)}
            />
            <span>Dividendos</span>
          </label>
        </div>

        <div className="form-group">
          <label htmlFor="broker">Broker:</label>
          <select id="broker" value={broker} onChange={(e) => setBroker(e.target.value)}>
            <option value="">-- Seleccionar --</option>
            {BROKERS.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="comision">Comisión (€):</label>
          <input
            id="comision"
            type="number"
            step="any"
            value={comision}
            onChange={(e) => setComision(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="precio_final">Precio final (€):</label>
          <input
            id="precio_final"
            type="text"
            value={precioFinalPreview}
            readOnly
            className="input-readonly"
          />
        </div>

        <div className="form-actions-span2">
          <button type="submit" className="btn-green-action" disabled={loadingPrice}>
            {loadingPrice ? 'OBTENIENDO PRECIO...' : 'AGREGAR ACTIVO'}
          </button>
        </div>
      </form>
    </div>
  );
};

