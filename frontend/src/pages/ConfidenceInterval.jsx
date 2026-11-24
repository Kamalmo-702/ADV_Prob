// Owner: Issue 4 - Confidence Intervals
import { useState } from 'react'
import { post } from '../api/client.js'
import NumberInput from '../components/NumberInput.jsx'
import StepsViewer from '../components/StepsViewer.jsx'
import ErrorMessage from '../components/ErrorMessage.jsx'
import PlotCard from '../components/PlotCard.jsx'

/* ── Case badge colours ───────────────────────────────────────────────── */
const CASE_STYLES = {
  'Z with sigma': { background: '#EEF0FD', color: '#3B4CCA' },
  'Z with s':     { background: '#DDF5F0', color: '#0B6B5F' },
  'T with s':     { background: '#FFF4E5', color: '#8B5E00' },
}

/* ── Confidence presets ───────────────────────────────────────────────── */
const CONF_PRESETS = [0.90, 0.95, 0.99]

/* ── Number-line SVG ──────────────────────────────────────────────────── */
function NumberLine({ lower, upper, xbar, plotMin, plotMax }) {
  const W = 480, H = 72, PAD = 32
  const range = plotMax - plotMin || 1
  const toX = v => PAD + ((v - plotMin) / range) * (W - 2 * PAD)
  const lx = toX(lower), ux = toX(upper), mx = toX(xbar)

  return (
    <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', maxWidth: W, display: 'block', margin: '0 auto' }}>
      {/* axis line */}
      <line x1={PAD} y1={H / 2} x2={W - PAD} y2={H / 2} stroke="#C9CEDD" strokeWidth={2} />
      {/* shaded interval */}
      <rect x={lx} y={H / 2 - 12} width={ux - lx} height={24} fill="#EEF0FD" rx={4} />
      {/* lower tick */}
      <line x1={lx} y1={H / 2 - 14} x2={lx} y2={H / 2 + 14} stroke="#3B4CCA" strokeWidth={2} />
      {/* upper tick */}
      <line x1={ux} y1={H / 2 - 14} x2={ux} y2={H / 2 + 14} stroke="#3B4CCA" strokeWidth={2} />
      {/* x-bar marker */}
      <circle cx={mx} cy={H / 2} r={5} fill="#0E9F8E" />
      {/* labels */}
      <text x={lx} y={H / 2 - 18} textAnchor="middle" fontSize={11} fill="#3B4CCA">{lower.toFixed(2)}</text>
      <text x={ux} y={H / 2 - 18} textAnchor="middle" fontSize={11} fill="#3B4CCA">{upper.toFixed(2)}</text>
      <text x={mx} y={H / 2 + 24} textAnchor="middle" fontSize={11} fill="#0E9F8E">x̄ = {xbar.toFixed(2)}</text>
    </svg>
  )
}

/* ── Main component ───────────────────────────────────────────────────── */
export default function ConfidenceInterval() {
  const [mode, setMode] = useState('summary')
  const [confidence, setConfidence] = useState(0.95)
  const [customConf, setCustomConf] = useState('')
  const [useCustomConf, setUseCustomConf] = useState(false)
  const [populationNormal, setPopulationNormal] = useState(false)

  // summary fields
  const [xbar, setXbar] = useState('')
  const [n, setN] = useState('')
  const [sigma, setSigma] = useState('')
  const [s, setS] = useState('')
  const [sigmaKnown, setSigmaKnown] = useState(false)

  // raw mode
  const [rawData, setRawData] = useState('')

  // sums mode
  const [sumN, setSumN] = useState('')
  const [sumX, setSumX] = useState('')
  const [sumX2, setSumX2] = useState('')

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const effectiveConf = useCustomConf ? Number(customConf) : confidence

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setResult(null)
    setLoading(true)

    try {
      let body = {
        mode,
        confidence: effectiveConf,
        population_normal: populationNormal,
      }

      if (mode === 'summary') {
        body.x_bar = Number(xbar)
        body.n = Number(n)
        if (sigmaKnown && sigma !== '') body.sigma = Number(sigma)
        else if (s !== '') body.s = Number(s)
      } else if (mode === 'raw') {
        body.data = rawData.split(/[\s,]+/).filter(Boolean).map(Number)
      } else {
        body.n = Number(sumN)
        body.sum_x = Number(sumX)
        body.sum_x2 = Number(sumX2)
      }

      const data = await post('/ci/mean', body)
      setResult(data)
    } catch (err) {
      const detail = err?.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail.map(d => d.msg).join('; '))
      } else {
        setError(detail || err.message || 'An error occurred.')
      }
    } finally {
      setLoading(false)
    }
  }

  const r = result?.result
  const caseStyle = r ? (CASE_STYLES[r.case] || { background: '#EEF0FD', color: '#3B4CCA' }) : null

  return (
    <div>
      <h1 className="page-title">Confidence Intervals</h1>
      <p className="page-desc">
        Confidence interval for the mean — the case (Z/T, σ/s) is chosen automatically
        from the lecture's "Very Important Remark".
      </p>

      {/* Warning when n<30 and normality not assumed */}
      {mode !== 'raw' && !populationNormal &&
        (mode === 'summary' ? Number(n) : Number(sumN)) > 0 &&
        (mode === 'summary' ? Number(n) : Number(sumN)) < 30 && (
        <div className="error" style={{ marginBottom: 16 }}>
          ⚠️ n &lt; 30 and "population approximately normal" is not checked.
          A valid interval cannot be constructed — please check the box or collect more data.
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* ── Mode switch ── */}
        <div className="card">
          <h2 className="card-title">Input mode</h2>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {['summary', 'raw', 'sums'].map(m => (
              <button key={m} type="button"
                onClick={() => setMode(m)}
                style={{
                  padding: '8px 18px', borderRadius: 10, border: '1.5px solid',
                  borderColor: mode === m ? '#3B4CCA' : '#C9CEDD',
                  background: mode === m ? '#EEF0FD' : '#fff',
                  color: mode === m ? '#3B4CCA' : '#5B6478',
                  fontWeight: mode === m ? 700 : 400, cursor: 'pointer',
                }}>
                {m === 'summary' ? 'Summary stats' : m === 'raw' ? 'Raw data' : 'Sums (Σx, Σx²)'}
              </button>
            ))}
          </div>
        </div>

        {/* ── Confidence level ── */}
        <div className="card">
          <h2 className="card-title">Confidence level</h2>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
            {CONF_PRESETS.map(c => (
              <button key={c} type="button"
                onClick={() => { setUseCustomConf(false); setConfidence(c) }}
                style={{
                  padding: '8px 18px', borderRadius: 10, border: '1.5px solid',
                  borderColor: !useCustomConf && confidence === c ? '#3B4CCA' : '#C9CEDD',
                  background: !useCustomConf && confidence === c ? '#EEF0FD' : '#fff',
                  color: !useCustomConf && confidence === c ? '#3B4CCA' : '#5B6478',
                  fontWeight: !useCustomConf && confidence === c ? 700 : 400, cursor: 'pointer',
                }}>
                {(c * 100).toFixed(0)}%
              </button>
            ))}
            <button type="button"
              onClick={() => setUseCustomConf(true)}
              style={{
                padding: '8px 18px', borderRadius: 10, border: '1.5px solid',
                borderColor: useCustomConf ? '#3B4CCA' : '#C9CEDD',
                background: useCustomConf ? '#EEF0FD' : '#fff',
                color: useCustomConf ? '#3B4CCA' : '#5B6478',
                fontWeight: useCustomConf ? 700 : 400, cursor: 'pointer',
              }}>
              Custom
            </button>
          </div>
          {useCustomConf && (
            <NumberInput label="Custom confidence (e.g. 0.98)" value={customConf}
              onChange={setCustomConf} step="0.01" min="0.01" max="0.99"
              hint="Enter a value strictly between 0 and 1." />
          )}

          <div style={{ marginTop: 12 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontSize: 14 }}>
              <input type="checkbox" checked={populationNormal}
                onChange={e => setPopulationNormal(e.target.checked)} />
              Population is approximately normal (required when n &lt; 30 and σ unknown)
            </label>
          </div>
        </div>

        {/* ── Summary inputs ── */}
        {mode === 'summary' && (
          <div className="card">
            <h2 className="card-title">Sample statistics</h2>
            <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(200px,1fr))' }}>
              <NumberInput label="Sample mean (x̄)" value={xbar} onChange={setXbar} />
              <NumberInput label="Sample size (n)" value={n} onChange={setN} step={1} min={1} />
            </div>
            <div style={{ marginTop: 12 }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontSize: 14 }}>
                <input type="checkbox" checked={sigmaKnown}
                  onChange={e => setSigmaKnown(e.target.checked)} />
                Population std dev (σ) is known
              </label>
            </div>
            <div className="grid" style={{ marginTop: 12, gridTemplateColumns: 'repeat(auto-fit,minmax(200px,1fr))' }}>
              {sigmaKnown
                ? <NumberInput label="Population std dev (σ)" value={sigma} onChange={setSigma} hint="σ > 0" />
                : <NumberInput label="Sample std dev (s)" value={s} onChange={setS} hint="s > 0" />}
            </div>
          </div>
        )}

        {/* ── Raw data inputs ── */}
        {mode === 'raw' && (
          <div className="card">
            <h2 className="card-title">Raw data</h2>
            <label className="field">
              <span className="field-label">Data values (comma or space separated)</span>
              <textarea value={rawData} onChange={e => setRawData(e.target.value)}
                rows={4} style={{
                  width: '100%', padding: '10px 12px', borderRadius: 10,
                  border: '1px solid #C9CEDD', font: 'inherit', resize: 'vertical'
                }}
                placeholder="e.g. 12.1, 13.5, 11.8, 14.2 ..." />
            </label>
          </div>
        )}

        {/* ── Sums inputs ── */}
        {mode === 'sums' && (
          <div className="card">
            <h2 className="card-title">Summary sums</h2>
            <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))' }}>
              <NumberInput label="n" value={sumN} onChange={setSumN} step={1} min={2} />
              <NumberInput label="Σx (sum of values)" value={sumX} onChange={setSumX} />
              <NumberInput label="Σx² (sum of squares)" value={sumX2} onChange={setSumX2} />
            </div>
          </div>
        )}

        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Computing…' : 'Compute interval'}
        </button>
      </form>

      <ErrorMessage message={error} />

      {/* ── Result ── */}
      {r && (
        <>
          {/* Case badge */}
          <div style={{ marginTop: 24, marginBottom: 8 }}>
            <span style={{
              ...caseStyle, display: 'inline-block', padding: '6px 16px',
              borderRadius: 999, fontWeight: 700, fontSize: 14,
            }}>
              Case: {r.case}
            </span>
          </div>

          {/* Big result card */}
          <div className="card" style={{ textAlign: 'center', padding: '32px 24px' }}>
            <p style={{ color: '#5B6478', margin: '0 0 8px', fontSize: 14 }}>
              {(r.confidence * 100).toFixed(0)}% Confidence Interval for μ
            </p>
            <p style={{ fontSize: 32, fontWeight: 700, color: '#3B4CCA', margin: '0 0 4px' }}>
              ({r.lower.toFixed(4)}, {r.upper.toFixed(4)})
            </p>
            <p style={{ color: '#5B6478', margin: 0, fontSize: 14 }}>
              x̄ = {r.x_bar.toFixed(4)} &nbsp;|&nbsp; Margin of error E = {r.margin.toFixed(4)}
              &nbsp;|&nbsp; {r.case.startsWith('T') ? 't' : 'z'} = {r.critical_value.toFixed(4)}
              {r.s !== undefined ? ` | s = ${r.s.toFixed(4)}` : ''}
            </p>
          </div>

          {/* Number line */}
          {result.plot && result.plot.type === 'interval' && (
            <div className="card">
              <h2 className="card-title">Interval on the number line</h2>
              <NumberLine
                lower={result.plot.lower} upper={result.plot.upper}
                xbar={result.plot.x_bar}
                plotMin={result.plot.plot_min} plotMax={result.plot.plot_max}
              />
            </div>
          )}

          {/* Notes */}
          {result.notes?.length > 0 && (
            <div className="card" style={{ background: '#DDF5F0' }}>
              {result.notes.map((n, i) => (
                <p key={i} style={{ margin: i ? '8px 0 0' : 0, fontSize: 14, color: '#0B6B5F' }}>ℹ️ {n}</p>
              ))}
            </div>
          )}

          <StepsViewer steps={result.steps} title="Solution steps" />
        </>
      )}
    </div>
  )
}
