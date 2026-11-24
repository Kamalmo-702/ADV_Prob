// Owner: Issue 3 - Sampling Distributions
import { useEffect, useState } from 'react'
import PlotCard from '../../components/PlotCard.jsx'
import StepsViewer from '../../components/StepsViewer.jsx'

const BADGE = {
  Z: { background: '#DDF5F0', color: '#0B6B5F' },
  T: { background: '#FDEEDE', color: '#B4530A' },
  'χ²': { background: '#EFE8FB', color: '#6B3FC4' },
}
const fmt = (x, d = 4) => (x === null || x === undefined ? '–' : Number(x).toFixed(d))

export default function SamplingResult({ data }) {
  const { result, plot, steps, notes } = data
  const symbol = plot.x_label
  const [mode, setMode] = useState('less')

  useEffect(() => {
    setMode(result.p_between !== null ? 'between' : 'less')
  }, [data, result.p_between])

  const chips = [
    { key: 'less', label: `P(${symbol} < a)`, value: result.p_less },
    { key: 'greater', label: `P(${symbol} > a)`, value: result.p_greater },
    { key: 'between', label: `P(a < ${symbol} < b)`, value: result.p_between },
  ]

  const region = plot.regions[mode]
  const curveTraces = [
    ...(region
      ? [{ x: region.x, y: region.y, type: 'scatter', mode: 'lines', fill: 'tozeroy',
          fillcolor: 'rgba(59, 76, 202, 0.30)', line: { width: 0 }, hoverinfo: 'skip', showlegend: false }]
      : []),
    { x: plot.curve.x, y: plot.curve.y, type: 'scatter', mode: 'lines', name: 'Sampling distribution',
      line: { color: '#14213D', width: 3 }, showlegend: false },
  ]
  const vline = (x, dash, color) => ({
    type: 'line', x0: x, x1: x, yref: 'paper', y0: 0, y1: 1, line: { color, width: 1.5, dash },
  })
  const shapes = [vline(plot.mean, 'dot', '#5B6478'), vline(plot.a, 'dash', '#3B4CCA')]
  const annotations = [{ x: plot.a, y: 1, yref: 'paper', text: 'a', showarrow: false, yshift: 10 }]
  if (plot.b !== null) {
    shapes.push(vline(plot.b, 'dash', '#3B4CCA'))
    annotations.push({ x: plot.b, y: 1, yref: 'paper', text: 'b', showarrow: false, yshift: 10 })
  }

  const se = plot.se_vs_n
  const seTraces = [
    { x: se.n, y: se.se, type: 'scatter', mode: 'lines', line: { color: '#14213D', width: 3 }, showlegend: false },
    { x: [se.current.n], y: [se.current.se], type: 'scatter', mode: 'markers+text',
      text: [`n = ${se.current.n}`], textposition: 'top right',
      marker: { color: '#3B4CCA', size: 11 }, showlegend: false },
  ]

  const statName = result.statistic === 'T' ? 't' : 'z'
  const facts = result.e_s2 !== undefined
    ? [['E(s²)', fmt(result.e_s2)], ['V(s²)', fmt(result.v_s2)], ['χ²(a)', fmt(result.chi2_a, 3)],
       ...(result.chi2_b !== null ? [['χ²(b)', fmt(result.chi2_b, 3)]] : [])]
    : [['Mean', fmt(result.mean_of_xbar ?? result.mean)], ['Standard error', fmt(result.standard_error)],
       [`${statName}(a)`, fmt(result.z_a, 3)], ...(result.z_b !== null ? [[`${statName}(b)`, fmt(result.z_b, 3)]] : [])]
  const badgeText = result.df ? `${result.statistic} · df = ${result.df}` : result.statistic

  return (
    <>
      <section className="card">
        <h2 className="card-title">Case chosen</h2>
        <div data-testid="case-badge" data-case={result.case}
          style={{ ...BADGE[result.statistic], display: 'inline-flex', gap: 12, alignItems: 'center',
            padding: '10px 16px', borderRadius: 12, flexWrap: 'wrap' }}>
          <strong style={{ fontSize: 20 }}>{badgeText}</strong>
          <span>{result.reason}</span>
        </div>

        {notes?.map((n, i) => (
          <div key={i} role="status" style={{ marginTop: 12, padding: '10px 14px', borderRadius: 10,
            background: '#FFF4E0', color: '#8A5A00', fontSize: 14 }}>
            ⚠ {n}
          </div>
        ))}

        <div className="grid" style={{ marginTop: 16 }}>
          {chips.map((c) => (
            <button key={c.key} type="button" disabled={c.value === null}
              aria-pressed={mode === c.key} onClick={() => setMode(c.key)}
              style={{ textAlign: 'left', padding: '12px 14px', borderRadius: 12, font: 'inherit',
                border: `1px solid ${mode === c.key ? '#3B4CCA' : '#E3E6EF'}`,
                background: mode === c.key ? '#EEF0FD' : '#fff', cursor: c.value === null ? 'default' : 'pointer',
                opacity: c.value === null ? 0.4 : 1, color: '#14213D' }}>
              <span className="field-label">{c.label}</span>
              <span style={{ fontSize: 24, fontWeight: 700 }}>{fmt(c.value)}</span>
            </button>
          ))}
        </div>
        <p className="muted" style={{ marginTop: 14, display: 'flex', gap: 20, flexWrap: 'wrap' }}>
          {facts.map(([k, v]) => (<span key={k}>{k} = <strong style={{ color: '#14213D' }}>{v}</strong></span>))}
        </p>
      </section>

      <PlotCard title={`Sampling distribution of ${symbol}`} data={curveTraces}
        layout={{ xaxis: { title: symbol }, yaxis: { title: 'Density' }, shapes, annotations, margin: { t: 24, r: 10, b: 45, l: 55 } }} />
      <StepsViewer steps={steps} />
      <PlotCard title="Standard error vs n" data={seTraces}
        layout={{ xaxis: { title: 'n' }, yaxis: { title: se.label } }}
        ariaLabel="Standard error versus sample size" />
    </>
  )
}
