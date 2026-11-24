// Owner: Issue 4 - Sample Size
import { useState } from 'react'
import { post } from '../api/client.js'
import NumberInput from '../components/NumberInput.jsx'
import StepsViewer from '../components/StepsViewer.jsx'
import ErrorMessage from '../components/ErrorMessage.jsx'
import PlotCard from '../components/PlotCard.jsx'

const CONF_PRESETS = [0.90, 0.95, 0.99]

export default function SampleSize() {
  const [confidence, setConfidence] = useState(0.95)
  const [customConf, setCustomConf] = useState('')
  const [useCustomConf, setUseCustomConf] = useState(false)
  const [sigmaOrS, setSigmaOrS] = useState('')
  const [margin, setMargin] = useState('')
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
      const data = await post('/ci/sample-size', {
        confidence: effectiveConf,
        sigma: Number(sigmaOrS),
        margin: Number(margin),
      })
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
  const plot = result?.plot

  // Build chart traces from plot data
  const chartTraces = plot ? [
    {
      x: plot.margins,
      y: plot.ns,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Required n',
      line: { color: '#3B4CCA', width: 2 },
      marker: { size: 4 },
    },
    {
      x: [plot.highlighted_margin],
      y: [plot.highlighted_n],
      type: 'scatter',
      mode: 'markers',
      name: 'Your selection',
      marker: { size: 12, color: '#0E9F8E', symbol: 'star' },
    },
  ] : null

  return (
    <div>
      <h1 className="page-title">Sample Size</h1>
      <p className="page-desc">
        How many observations do you need for a desired margin of error?
        Always rounds <strong>up</strong> so the margin of error is not exceeded.
      </p>

      <form onSubmit={handleSubmit}>
        {/* Confidence level */}
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
        </div>

        {/* Parameters */}
        <div className="card">
          <h2 className="card-title">Parameters</h2>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(220px,1fr))' }}>
            <NumberInput
              label="Std deviation (σ or s)"
              value={sigmaOrS}
              onChange={setSigmaOrS}
              hint="Must be positive"
            />
            <NumberInput
              label="Desired margin of error (E)"
              value={margin}
              onChange={setMargin}
              hint="Must be positive"
            />
          </div>
        </div>

        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Computing…' : 'Compute sample size'}
        </button>
      </form>

      <ErrorMessage message={error} />

      {/* Result */}
      {r && (
        <>
          <div className="card" style={{ textAlign: 'center', padding: '32px 24px', marginTop: 24 }}>
            <p style={{ color: '#5B6478', margin: '0 0 8px', fontSize: 14 }}>
              Required sample size for {(r.confidence * 100).toFixed(0)}% confidence
              with margin E = {r.margin}
            </p>
            <p style={{ fontSize: 48, fontWeight: 700, color: '#3B4CCA', margin: '0 0 8px' }}>
              n = {r.n}
            </p>
            <p style={{ color: '#5B6478', margin: 0, fontSize: 14 }}>
              Exact: n = ({r.z} × {r.sigma} / {r.margin})² = {r.n_exact}
              &nbsp;→ rounded up to {r.n}
            </p>
          </div>

          {/* n vs margin chart */}
          {chartTraces && (
            <PlotCard
              title="Required n vs margin of error"
              data={chartTraces}
              layout={{
                xaxis: { title: 'Margin of error (E)' },
                yaxis: { title: 'Required n' },
                legend: { orientation: 'h', y: -0.2 },
              }}
              ariaLabel="Chart of required sample size vs margin of error"
            />
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
