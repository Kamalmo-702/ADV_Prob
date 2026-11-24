// Owner: Issue 3 - Sampling Distributions
import { useState } from 'react'
import ErrorMessage from '../../components/ErrorMessage.jsx'
import NumberInput from '../../components/NumberInput.jsx'
import SamplingResult from './SamplingResult.jsx'
import useSolve from './useSolve.js'

export default function MeanTab() {
  const [mu, setMu] = useState(200)
  const [n, setN] = useState(16)
  const [sdKnown, setSdKnown] = useState('known')
  const [sd, setSd] = useState(6)
  const [normal, setNormal] = useState(true)
  const [a, setA] = useState(199)
  const [b, setB] = useState('')
  const { data, error, loading, run } = useSolve('/sampling/mean')

  function submit(e) {
    e.preventDefault()
    run({ mu, n, a, b, population_normal: normal, ...(sdKnown === 'known' ? { sigma: sd } : { s: sd }) })
  }

  return (
    <>
      <form className="card" onSubmit={submit}>
        <h2 className="card-title">Sampling distribution of the mean</h2>
        <div className="grid">
          <NumberInput label="Population mean (μ)" value={mu} onChange={setMu} />
          <NumberInput label="Sample size (n)" value={n} min={1} step={1} onChange={setN} />
          <label className="field">
            <span className="field-label">Standard deviation</span>
            <select value={sdKnown} onChange={(e) => setSdKnown(e.target.value)}>
              <option value="known">σ is known</option>
              <option value="unknown">σ is unknown (use sample s)</option>
            </select>
          </label>
          <NumberInput label={sdKnown === 'known' ? 'σ' : 's'} value={sd} min={0} onChange={setSd} />
          <NumberInput label="a" value={a} onChange={setA} hint="For P(x̄ < a) and P(x̄ > a)" />
          <NumberInput label="b (optional)" value={b} onChange={setB} hint="For P(a < x̄ < b)" />
        </div>
        <label style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 16 }}>
          <input type="checkbox" checked={normal} onChange={(e) => setNormal(e.target.checked)} />
          <span>Population is (approximately) normal</span>
        </label>
        <div style={{ marginTop: 20 }}>
          <button type="submit" className="btn" disabled={loading}>{loading ? 'Calculating…' : 'Calculate'}</button>
        </div>
        {error && <div style={{ marginTop: 14 }}><ErrorMessage message={error} /></div>}
      </form>
      {data && <SamplingResult data={data} />}
    </>
  )
}
