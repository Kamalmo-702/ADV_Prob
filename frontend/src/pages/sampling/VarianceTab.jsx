// Owner: Issue 3 - Sampling Distributions
import { useState } from 'react'
import ErrorMessage from '../../components/ErrorMessage.jsx'
import NumberInput from '../../components/NumberInput.jsx'
import SamplingResult from './SamplingResult.jsx'
import useSolve from './useSolve.js'

export default function VarianceTab() {
  const [n, setN] = useState(25)
  const [sigma2, setSigma2] = useState(6)
  const [a, setA] = useState(3.462)
  const [b, setB] = useState(10.745)
  const { data, error, loading, run } = useSolve('/sampling/variance')

  function submit(e) {
    e.preventDefault()
    run({ n, sigma2, a, b })
  }

  return (
    <>
      <form className="card" onSubmit={submit}>
        <h2 className="card-title">Sampling distribution of the variance</h2>
        <div className="grid">
          <NumberInput label="Sample size (n)" value={n} min={2} step={1} onChange={setN} />
          <NumberInput label="Population variance (σ²)" value={sigma2} min={0} onChange={setSigma2} />
          <NumberInput label="a" value={a} min={0} onChange={setA} hint="For P(s² < a) and P(s² > a)" />
          <NumberInput label="b (optional)" value={b} min={0} onChange={setB} hint="For P(a < s² < b)" />
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
