// Owner: Issue 5 - CLT Simulator
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
  return err?.message || 'Failed to run CLT simulation.'
}

export default function CLTSimulator() {
  const [population, setPopulation] = useState('exponential')
  const [n, setN] = useState(30)
  const [samples, setSamples] = useState(2000)
  const [seed, setSeed] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState(null)

  async function runSimulation(overrideN = n) {
    setLoading(true)
    setError('')
    try {
      const payload = {
        population,
        n: Number(overrideN),
        samples: Number(samples),
        ...(seed !== '' ? { seed: Number(seed) } : {}),
      }
      const res = await post('/clt/simulate', payload)
      setData(res)
    } catch (err) {
      setError(formatApiError(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    runSimulation(30)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function handleSubmit(e) {
    e.preventDefault()
    runSimulation()
  }

  const res = data?.result
  const plot = data?.plot

  const popTraces = plot
    ? [
        {
          x: plot.population_hist.centers,
          y: plot.population_hist.counts,
          width: plot.population_hist.widths,
          type: 'bar',
          name: 'Population density',
          marker: { color: 'rgba(59, 76, 202, 0.72)', line: { color: '#3B4CCA', width: 1 } },
        },
      ]
    : []

  const meansTraces = plot
    ? [
        {
          x: plot.means_hist.centers,
          y: plot.means_hist.counts,
          width: plot.means_hist.widths,
          type: 'bar',
          name: 'Simulated sample means',
          marker: { color: 'rgba(14, 159, 142, 0.65)', line: { color: '#0E9F8E', width: 1 } },
        },
        {
          x: plot.normal_curve.x,
          y: plot.normal_curve.y,
          type: 'scatter',
          mode: 'lines',
          name: 'CLT Normal PDF',
          line: { color: '#3B4CCA', width: 3 },
        },
      ]
    : []

  return (
    <>
      <h1 className="page-title">CLT Simulator</h1>
      <p className="page-desc">
        Watch sample means become bell-shaped as the sample size grows, regardless of the population shape.
      </p>

      <form className="card" onSubmit={handleSubmit}>
        <h2 className="card-title">Simulation parameters</h2>
        <div className="grid">
          <label className="field">
            <span className="field-label">Population distribution</span>
            <select value={population} onChange={(e) => setPopulation(e.target.value)}>
              <option value="uniform">Uniform(0, 1)</option>
              <option value="exponential">Exponential (right-skewed)</option>
              <option value="skewed">Skewed (Chi-square, df = 3)</option>
              <option value="bimodal">Bimodal (two peaks)</option>
            </select>
          </label>

          <label className="field">
            <span className="field-label">Sample size (n): {n}</span>
            <input
              type="range"
              min={1}
              max={500}
              value={n === '' ? 1 : n}
              onChange={(e) => setN(Number(e.target.value))}
            />
            <span className="field-hint">Slide from 1 to 500 (try n = 1, 5, 30, 100)</span>
          </label>

          <NumberInput
            label="Sample size (exact n)"
            value={n}
            min={1}
            max={500}
            step={1}
            onChange={setN}
            hint="1 to 500"
          />

          <NumberInput
            label="Number of samples"
            value={samples}
            min={100}
            max={20000}
            step={100}
            onChange={setSamples}
            hint="100 to 20,000"
          />

          <NumberInput
            label="Random seed (optional)"
            value={seed}
            step={1}
            onChange={setSeed}
            hint="Leave blank for random draws"
          />
        </div>

        <div style={{ marginTop: '20px', display: 'flex', gap: '12px', alignItems: 'center' }}>
          <button type="submit" className="btn" disabled={loading}>
            {loading ? 'Running…' : 'Run simulation'}
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
          <div className="grid">
            <section className="card">
              <span className="field-label">Population Mean (μ)</span>
              <div style={{ fontSize: '24px', fontWeight: 700, color: '#3B4CCA' }}>
                {res.pop_mean.toFixed(4)}
              </div>
              <span className="field-hint">Simulated mean of means: {res.mean_of_means.toFixed(4)}</span>
            </section>

            <section className="card">
              <span className="field-label">Population SD (σ)</span>
              <div style={{ fontSize: '24px', fontWeight: 700 }}>{res.pop_sd.toFixed(4)}</div>
              <span className="field-hint">True spread of single observations</span>
            </section>

            <section className="card">
              <span className="field-label">Theoretical SE (σ / √n)</span>
              <div style={{ fontSize: '24px', fontWeight: 700, color: '#3B4CCA' }}>
                {res.theoretical_se.toFixed(4)}
              </div>
              <span className="field-hint">Predicted SD of sample means</span>
            </section>

            <section className="card">
              <span className="field-label">Simulated SD of Means</span>
              <div style={{ fontSize: '24px', fontWeight: 700, color: '#0E9F8E' }}>
                {res.sd_of_means.toFixed(4)}
              </div>
              <span className="field-hint">Empirical spread across {res.samples} samples</span>
            </section>
          </div>

          <div className="grid">
            <PlotCard
              title="Population Distribution"
              data={popTraces}
              layout={{
                xaxis: { title: 'x' },
                yaxis: { title: 'Density' },
                bargap: 0.04,
                showlegend: false,
              }}
            />

            <PlotCard
              title={`Distribution of Sample Means (n = ${res.n})`}
              data={meansTraces}
              layout={{
                xaxis: { title: 'Sample mean (x̄)' },
                yaxis: { title: 'Density' },
                bargap: 0.04,
                legend: { orientation: 'h', y: 1.14 },
              }}
            />
          </div>

          {data.notes?.length > 0 && (
            <section className="card">
              <h2 className="card-title">Interpretation</h2>
              {data.notes.map((note, idx) => (
                <p key={idx} className="muted">
                  {note}
                </p>
              ))}
            </section>
          )}

          <StepsViewer steps={data.steps} />
        </>
      )}
    </>
  )
}