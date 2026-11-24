// Owner: Issue 3 - Sampling Distributions
import { useState } from 'react'
import ErrorMessage from '../../components/ErrorMessage.jsx'
import NumberInput from '../../components/NumberInput.jsx'
import SamplingResult from './SamplingResult.jsx'
import useSolve from './useSolve.js'

export default function ProportionTab() {
  const [source, setSource] = useState('p')
  const [p, setP] = useState(0.35)
  const [bigN, setBigN] = useState(100)
  const [x, setX] = useState(20)
  const [n, setN] = useState(15)
  const [a, setA] = useState(0.2)
  const [b, setB] = useState('')
  const { data, error, loading, run } = useSolve('/sampling/proportion')

  function submit(e) {
    e.preventDefault()
    run({ n, a, b, ...(source === 'p' ? { p } : { population_size: bigN, population_successes: x }) })
  }

  return (
    <>
      <form className="card" onSubmit={submit}>
        <h2 className="card-title">Sampling distribution of the proportion</h2>
        <div className="grid">
          <label className="field">
            <span className="field-label">Population proportion given as</span>
            <select value={source} onChange={(e) => setSource(e.target.value)}>
              <option value="p">P directly</option>
              <option value="NX">Counts: N and X</option>
            </select>
          </label>
          {source === 'p' ? (
            <NumberInput label="Population proportion (P)" value={p} min={0} max={1} onChange={setP} />
          ) : (
            <>
              <NumberInput label="Population size (N)" value={bigN} min={1} step={1} onChange={setBigN} />
              <NumberInput label="Population successes (X)" value={x} min={0} step={1} onChange={setX} hint="P = X / N" />
            </>
          )}
          <NumberInput label="Sample size (n)" value={n} min={1} step={1} onChange={setN} />
          <NumberInput label="a" value={a} min={0} max={1} onChange={setA} hint="For P(p̂ < a) and P(p̂ > a)" />
          <NumberInput label="b (optional)" value={b} min={0} max={1} onChange={setB} hint="For P(a < p̂ < b)" />
        </div>
        <div style={{ marginTop: 20 }}>
          <button type="submit" className="btn" disabled={loading}>{loading ? 'Calculating…' : 'Calculate'}</button>
        </div>
        {error && <div style={{ marginTop: 14 }}><ErrorMessage message={error} /></div>}
      </form>
      {data && <SamplingResult data={data} />}
    </>
  )
}
