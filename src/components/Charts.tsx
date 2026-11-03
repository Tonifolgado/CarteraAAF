import React, { useState } from 'react';

export interface BarChartItem {
  label: string;
  value: number;
  color: string;
}

interface BarChartProps {
  title: string;
  yAxisLabel?: string;
  items: BarChartItem[];
  formatValueLabel?: (val: number) => string;
  size?: 'normal' | 'large';
}

export const AssetBarChart: React.FC<BarChartProps> = ({
  title,
  yAxisLabel = 'Importe (€)',
  items,
  formatValueLabel = (v) => `${Math.round(v)}€`,
  size = 'normal'
}) => {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  const isLarge = size === 'large';
  const width = isLarge ? 720 : 400;
  const height = isLarge ? 420 : 290;
  const padTop = isLarge ? 56 : 44;
  const padBottom = isLarge ? 50 : 40;
  const padLeft = isLarge ? 80 : 66;
  const padRight = isLarge ? 30 : 20;

  const plotW = width - padLeft - padRight;
  const plotH = height - padTop - padBottom;

  const maxVal = Math.max(...items.map((i) => i.value), 1);
  // Nice upper bound for y axis
  const yMax = maxVal * 1.15;
  const yTicks = 5;
  const tickValues = Array.from({ length: yTicks + 1 }, (_, i) => (yMax / yTicks) * i);

  const barSlotWidth = plotW / Math.max(items.length, 1);
  const barWidth = Math.min(isLarge ? 82 : 54, barSlotWidth * 0.62);

  return (
    <div className={`chart-box ${isLarge ? 'chart-box-large' : ''}`}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className={`chart-svg ${isLarge ? 'chart-svg-bar-large' : ''}`}
        role="img"
        aria-label={title}
      >
        {/* Title */}
        <text
          x={width / 2}
          y={isLarge ? 28 : 22}
          textAnchor="middle"
          fontSize={isLarge ? '16' : '13'}
          fontWeight="700"
          fill="#1e293b"
        >
          {title}
        </text>

        {/* Y-axis label */}
        <text
          transform={`translate(${isLarge ? 20 : 16}, ${padTop + plotH / 2}) rotate(-90)`}
          textAnchor="middle"
          fontSize={isLarge ? '13' : '11'}
          fontWeight="600"
          fill="#475569"
        >
          {yAxisLabel}
        </text>

        {/* Grid lines & Y ticks */}
        {tickValues.map((tv, idx) => {
          const y = padTop + plotH - (tv / yMax) * plotH;
          return (
            <g key={idx}>
              <line
                x1={padLeft}
                y1={y}
                x2={width - padRight}
                y2={y}
                stroke={idx === 0 ? '#334155' : '#e2e8f0'}
                strokeWidth={idx === 0 ? 1.2 : 1}
                strokeDasharray={idx === 0 ? undefined : '3,3'}
              />
              <text
                x={padLeft - 8}
                y={y + 4}
                textAnchor="end"
                fontSize={isLarge ? '12' : '10'}
                fill="#475569"
              >
                {Math.round(tv).toLocaleString('es-ES')}
              </text>
            </g>
          );
        })}

        {/* Left axis line */}
        <line
          x1={padLeft}
          y1={padTop}
          x2={padLeft}
          y2={padTop + plotH}
          stroke="#334155"
          strokeWidth={1.2}
        />

        {/* Bars */}
        {items.map((item, idx) => {
          const barH = Math.max(0, (item.value / yMax) * plotH);
          const x = padLeft + idx * barSlotWidth + (barSlotWidth - barWidth) / 2;
          const y = padTop + plotH - barH;
          const isHovered = hoveredIdx === idx;

          return (
            <g
              key={item.label}
              onMouseEnter={() => setHoveredIdx(idx)}
              onMouseLeave={() => setHoveredIdx(null)}
              style={{ cursor: 'pointer' }}
            >
              <rect
                x={x}
                y={y}
                width={barWidth}
                height={barH}
                fill={item.color}
                stroke={isHovered ? '#0f172a' : '#475569'}
                strokeWidth={isHovered ? 1.8 : 1}
                rx={4}
              />
              {/* Value label on top of bar */}
              <text
                x={x + barWidth / 2}
                y={y - 8}
                textAnchor="middle"
                fontSize={isLarge ? '13' : '10.5'}
                fontWeight="700"
                fill="#0f172a"
              >
                {formatValueLabel(item.value)}
              </text>
              {/* X-axis category label */}
              <text
                x={x + barWidth / 2}
                y={padTop + plotH + (isLarge ? 24 : 18)}
                textAnchor="middle"
                fontSize={isLarge ? '13.5' : '11'}
                fontWeight="700"
                fill="#1e293b"
              >
                {item.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

export interface PieSliceItem {
  label: string;
  value: number;
  color: string;
}

interface PieChartProps {
  title: string;
  items: PieSliceItem[];
  showCurrencyInSlice?: boolean;
  startAngleDeg?: number;
  size?: 'normal' | 'large';
}

function formatEuroNumber(val: number): string {
  return val
    .toFixed(2)
    .replace('.', ',')
    .replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

export const AssetPieChart: React.FC<PieChartProps> = ({
  title,
  items,
  showCurrencyInSlice = false,
  startAngleDeg = 140,
  size = 'normal'
}) => {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  const positiveItems = items.filter((i) => i.value > 0);
  const total = positiveItems.reduce((acc, cur) => acc + cur.value, 0);

  const isLarge = size === 'large';
  const width = isLarge ? 540 : 400;
  const height = isLarge ? 400 : 290;
  const cx = width / 2;
  const cy = height / 2 + 14;
  const radius = isLarge ? 145 : 96;

  if (total <= 0) {
    return (
      <div className="chart-box chart-empty">
        <div className="chart-empty-title">{title}</div>
        <div className="chart-empty-sub">Sin datos positivos para graficar</div>
      </div>
    );
  }

  // Matplotlib counter-clockwise from startAngleDeg, or standard polar coordinates
  let currentAngle = -startAngleDeg * (Math.PI / 180);

  const slices = positiveItems.map((item, idx) => {
    const fraction = item.value / total;
    const angleSpan = fraction * Math.PI * 2;
    const startAngle = currentAngle;
    const endAngle = currentAngle + angleSpan;
    const midAngle = startAngle + angleSpan / 2;
    currentAngle = endAngle;

    const x1 = cx + radius * Math.cos(startAngle);
    const y1 = cy + radius * Math.sin(startAngle);
    const x2 = cx + radius * Math.cos(endAngle);
    const y2 = cy + radius * Math.sin(endAngle);
    const largeArc = angleSpan > Math.PI ? 1 : 0;

    const pathData =
      positiveItems.length === 1
        ? `M ${cx - radius} ${cy} A ${radius} ${radius} 0 1 1 ${cx + radius} ${cy} A ${radius} ${radius} 0 1 1 ${cx - radius} ${cy}`
        : `M ${cx} ${cy} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`;

    const labelRadius = radius * (showCurrencyInSlice ? 0.6 : 0.62);
    const lx = cx + labelRadius * Math.cos(midAngle);
    const ly = cy + labelRadius * Math.sin(midAngle);

    const outerLabelRadius = radius + 20;
    const ox = cx + outerLabelRadius * Math.cos(midAngle);
    const oy = cy + outerLabelRadius * Math.sin(midAngle);

    return {
      item,
      idx,
      fraction,
      pctText: `${(fraction * 100).toFixed(1)}%`,
      euroText: `${formatEuroNumber(item.value)} €`,
      pathData,
      midAngle,
      lx,
      ly,
      ox,
      oy
    };
  });

  return (
    <div className={`chart-box ${isLarge ? 'chart-box-large' : ''}`}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className={`chart-svg ${isLarge ? 'chart-svg-large' : ''}`}
        role="img"
        aria-label={title}
      >
        <text
          x={width / 2}
          y={26}
          textAnchor="middle"
          fontSize={isLarge ? '16' : '13'}
          fontWeight="700"
          fill="#1e293b"
        >
          {title}
        </text>

        {slices.map((s) => {
          const isHovered = hoveredIdx === s.idx;
          const offset = isHovered ? 6 : 0;
          const dx = Math.cos(s.midAngle) * offset;
          const dy = Math.sin(s.midAngle) * offset;

          return (
            <g
              key={s.item.label}
              transform={`translate(${dx}, ${dy})`}
              onMouseEnter={() => setHoveredIdx(s.idx)}
              onMouseLeave={() => setHoveredIdx(null)}
              style={{ cursor: 'pointer', transition: 'transform 0.15s ease' }}
            >
              <path
                d={s.pathData}
                fill={s.item.color}
                stroke="#334155"
                strokeWidth={isHovered ? 1.6 : 1}
              />
              {/* Outer category label */}
              <text
                x={s.ox}
                y={s.oy + 4}
                textAnchor={Math.cos(s.midAngle) >= 0 ? 'start' : 'end'}
                fontSize={isLarge ? '14' : '11'}
                fontWeight="700"
                fill="#0f172a"
              >
                {s.item.label}
              </text>

              {/* Inner percentage (and optional euro amount) */}
              {showCurrencyInSlice ? (
                <text
                  x={s.lx}
                  y={s.ly - 4}
                  textAnchor="middle"
                  fontSize={isLarge ? '12.5' : '9.5'}
                  fontWeight="700"
                  fill="#0f172a"
                >
                  <tspan x={s.lx} dy="0">
                    {s.pctText}
                  </tspan>
                  <tspan x={s.lx} dy={isLarge ? '16' : '12'}>
                    {s.euroText}
                  </tspan>
                </text>
              ) : (
                <text
                  x={s.lx}
                  y={s.ly + 4}
                  textAnchor="middle"
                  fontSize={isLarge ? '13' : '10'}
                  fontWeight="700"
                  fill="#0f172a"
                >
                  {s.pctText}
                </text>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
};

