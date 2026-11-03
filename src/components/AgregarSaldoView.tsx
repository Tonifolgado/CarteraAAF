import React, { useMemo, useState } from 'react';
import { MESES_LARGOS } from '../types';
import { formatFloatToEuroStr, parseEuroInput } from '../utils/formatters';

interface AgregarSaldoViewProps {
  onAddSaldo: (ano: string, mes: string, ingresos: number, gastos: number) => Promise<void>;
  onNavigateSaldos: () => void;
}

export const AgregarSaldoView: React.FC<AgregarSaldoViewProps> = ({
  onAddSaldo,
  onNavigateSaldos
}) => {
  const [ano, setAno] = useState(String(new Date().getFullYear()));
  const [mes, setMes] = useState(MESES_LARGOS[0]);
  const [ingresosStr, setIngresosStr] = useState('');
  const [gastosStr, setGastosStr] = useState('');
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; msg: string } | null>(
    null
  );

  const saldoDisplay = useMemo(() => {
    const ing = parseEuroInput(ingresosStr);
    const gas = parseEuroInput(gastosStr);
    if (Number.isNaN(ing) || Number.isNaN(gas)) {
      return 'Error';
    }
    return formatFloatToEuroStr(ing - gas);
  }, [ingresosStr, gastosStr]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback(null);

    const anoClean = ano.trim();
    if (!/^\d{4}$/.test(anoClean)) {
      setFeedback({ type: 'error', msg: 'El año debe ser un número de 4 dígitos.' });
      return;
    }

    const ingresos = parseEuroInput(ingresosStr);
    const gastos = parseEuroInput(gastosStr);

    if (Number.isNaN(ingresos) || Number.isNaN(gastos)) {
      setFeedback({ type: 'error', msg: 'Ingresos y Gastos deben ser números válidos.' });
      return;
    }

    setSaving(true);
    try {
      await onAddSaldo(anoClean, mes, ingresos, gastos);
      setFeedback({ type: 'success', msg: 'Saldo mensual añadido correctamente.' });
      setIngresosStr('');
      setGastosStr('');
    } catch (err: any) {
      setFeedback({
        type: 'error',
        msg: `No se pudo guardar el saldo: ${err?.message || 'Error desconocido'}`
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="panel-card max-w-500 mx-auto">
      <div className="panel-header">
        <h2>Añadir Nuevo Saldo Mensual</h2>
        <button type="button" className="btn-secondary" onClick={onNavigateSaldos}>
          Ver Saldos Mensuales
        </button>
      </div>

      {feedback && (
        <div className={`alert-banner ${feedback.type === 'error' ? 'alert-error' : 'alert-success'}`}>
          {feedback.msg}
        </div>
      )}

      <form onSubmit={handleSubmit} className="form-single-col">
        <div className="form-group-inline">
          <label htmlFor="ano_saldo">Año (YYYY):</label>
          <input
            id="ano_saldo"
            type="text"
            maxLength={4}
            value={ano}
            onChange={(e) => setAno(e.target.value)}
            placeholder="2026"
          />
        </div>

        <div className="form-group-inline">
          <label htmlFor="mes_saldo">Mes:</label>
          <select id="mes_saldo" value={mes} onChange={(e) => setMes(e.target.value)}>
            {MESES_LARGOS.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group-inline">
          <label htmlFor="ingresos_saldo">Ingresos (€):</label>
          <input
            id="ingresos_saldo"
            type="text"
            inputMode="decimal"
            value={ingresosStr}
            onChange={(e) => setIngresosStr(e.target.value)}
            placeholder="0,00"
          />
        </div>

        <div className="form-group-inline">
          <label htmlFor="gastos_saldo">Gastos (€):</label>
          <input
            id="gastos_saldo"
            type="text"
            inputMode="decimal"
            value={gastosStr}
            onChange={(e) => setGastosStr(e.target.value)}
            placeholder="0,00"
          />
        </div>

        <div className="form-group-inline">
          <label htmlFor="saldo_calc">Saldo (€):</label>
          <input
            id="saldo_calc"
            type="text"
            readOnly
            value={saldoDisplay}
            className="input-readonly font-bold"
          />
        </div>

        <div className="form-actions-center mt-4">
          <button type="submit" className="btn-green-action" disabled={saving}>
            {saving ? 'Guardando...' : 'Guardar Saldo'}
          </button>
        </div>
      </form>
    </div>
  );
};

