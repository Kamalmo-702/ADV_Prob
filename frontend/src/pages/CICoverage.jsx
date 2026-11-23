// Owner: Issue 5 - CI Coverage Demo
import { useEffect, useState } from 'react'
import { post } from '../api/client.js'
import ErrorMessage from '../components/ErrorMessage.jsx'
import NumberInput from '../components/NumberInput.jsx'
import PlotCard from '../components/PlotCard.jsx'
import StepsViewer from '../components/StepsViewer.jsx'

function formatApiError(err) {
  const detail = err?.response?.data?.detail
  if (Array.isArray(detail)) {
    return detail.map((d) => `${d.loc?.slice(-1)[0] || 'input'}: ${d.msg}`).join('; ')
  }
  if (typeof detail === 'string') return detail
  return err?.message || 'Failed to simulate confidence intervals.'
}

export default function CICoverage() {
  const [mu, setMu] = useState(50)
  const [sigma, setSigma] = useState(10)
  const [n, setN] = useState(25)
  const [confidence, setConfidence] = useState(0.95)
  const [intervalsCount, setIntervalsCount] = useState(100)
  const [seed, setSeed] = useState(42)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState(null)

  async function runCoverage(overrides = {}) {
    setLoading(true)
    setError('')
    try {
      const payload = {
        mu: Number(overrides.mu ?? mu),
        sigma: Number(overrides.sigma ?? sigma),
        n: Number(overrides.n ?? n),
        confidence: Number(overrides.confidence ?? confidence),
        intervals: Number(overrides.intervals ?? intervalsCount),
        ...(seed !== '' ? { seed: Number(seed) } : {}),
      }
      const res = await post('/clt/coverage', payload)
      setData(res)
    } catch (err) {
      setError(formatApiError(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    runCoverage()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function handleSubmit(e) {
    e.preventDefault()
    runCoverage()
  }

  const res = data?.result

  const buildTraces = () => {
    if (!res?.intervals) return []
    const hitX = []
    const hitY = []
    const missX = []
    const missY = []

    for (const iv of res.intervals) {
      if (iv.contains_mu) {
        hitX.push(iv.lower, iv.upper, null)
        hitY.push(iv.index, iv.index, null)
      } else {
        missX.push(iv.lower, iv.upper, null)
        missY.push(iv.index, iv.index, null)
      }
    }

    return [
      {
        x: hitX,
        y: hitY,
        type: 'scatter',
        mode: 'lines',
        name: 'Contains μ',
        line: { color: '#0E9F8E', width: 2 },
      },
      {
        x: missX,
        y: missY,
        type: 'scatter',
        mode: 'lines',
        name: 'Misses μ',
        line: { color: '#B3261E', width: 2.5 },
      },
      {
        x: [res.mu, res.mu],
        y: [0, res.total_intervals + 1],
        type: 'scatter',
        mode: 'lines',
        name: `True μ = ${res.mu}`,
        line: { color: '#3B4CCA', width: 2, dash: 'dash' },
      },
    ]
  }

  return (
    <>
      <h1 className="page-title">CI Coverage Demo</h1>
      <p className="page-desc">
        See how many of {intervalsCount || 100} confidence intervals really contain the true mean μ.
      </p>

      <form className="card" onSubmit={handleSubmit}>
        <h2 className="card-title">Simulation settings</h2>
        <div className="grid">
          <label className="field">
            <span className="field-label">Confidence level</span>
            <select
              value={[0.9, 0.95, 0.99].includes(Number(confidence)) ? String(confidence) : 'custom'}
              onChange={(e) => {
                if (e.target.value !== 'custom') {
                  const val = Number(e.target.value)
                  setConfidence(val)
                  runCoverage({ confidence: val })
                }
              }}
            >
              <option value="0.9">90% (0.90)</option>
              <option value="0.95">95% (0.95)</option>
              <option value="0.99">99% (0.99)</option>
              <option value="custom">Custom</option>
            </select>
          </label>

          <NumberInput
            label="Confidence (exact)"
            value={confidence}
            min={0.01}
            max={0.999}
            step={0.01}
            onChange={setConfidence}
            hint="Between 0 and 1 (e.g. 0.95)"
          />

          <NumberInput
            label="Sample size (n)"
            value={n}
            min={1}
            max={10000}
            step={1}
            onChange={setN}
            hint="Larger n makes intervals narrower"
          />

          <NumberInput
            label="True mean (μ)"
            value={mu}
            step="any"
            onChange={setMu}
          />

          <NumberInput
            label="Known SD (σ)"
            value={sigma}
            min={0.0001}
            step="any"
            onChange={setSigma}
          />

          <NumberInput
            label="Number of intervals"
            value={intervalsCount}
            min={1}
            max={500}
            step={1}
            onChange={setIntervalsCount}
            hint="Default: 100"
          />

          <NumberInput
            label="Random seed (optional)"
            value={seed}
            step={1}
            onChange={setSeed}
            hint="Clear for new random samples"
          />
        </div>

        <div style={{ marginTop: '20px', display: 'flex', gap: '12px', alignItems: 'center' }}>
          <button type="submit" className="btn" disabled={loading}>
            {loading ? 'Simulating…' : 'Generate intervals'}
          </button>
          <button
            type="button"
            className="btn"
            style={{ background: '#0E9F8E' }}
            disabled={loading}
            onClick={() => {
              const nextSeed = Math.floor(Math.random() * 100000)
              setSeed(nextSeed)
              runCoverage({ seed: nextSeed })
            }}
          >
            New random draw
          </button>
        </div>

        {error && (
          <div style={{ marginTop: '14px' }}>
            <ErrorMessage message={error} />
          </div>
        )}
      </form>

      {res && (
        <>
          <section className="card">
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <h2 className="card-title" style={{ marginBottom: '4px' }}>
                  {res.covered_count} of {res.total_intervals} contain μ ({(res.coverage_rate * 100).toFixed(1)}%)
                </h2>
                <p className="muted">
                  Nominal confidence: {(res.confidence * 100).toFixed(1)}% · z* = {res.z_critical.toFixed(4)} · Margin of error = ±{res.margin.toFixed(4)}
                </p>
              </div>
              <span className="badge">
                {res.covered_count} hit · {res.total_intervals - res.covered_count} miss
              </span>
            </div>
          </section>

          <PlotCard
            title={`Simulated ${(res.confidence * 100).toFixed(0)}% Confidence Intervals around μ = ${res.mu}`}
            data={buildTraces()}
            layout={{
              height: 520,
              xaxis: { title: 'Value' },
              yaxis: { title: 'Sample #', range: [0, res.total_intervals + 1] },
              legend: { orientation: 'h', y: 1.08 },
            }}
          />

          <StepsViewer steps={data.steps} />
        </>
      )}
    </>
  )
}