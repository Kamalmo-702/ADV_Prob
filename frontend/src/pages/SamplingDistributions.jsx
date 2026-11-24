// Owner: Issue 3 - Sampling Distributions
import { useState } from 'react'
import MeanTab from './sampling/MeanTab.jsx'
import ProportionTab from './sampling/ProportionTab.jsx'
import VarianceTab from './sampling/VarianceTab.jsx'

const TABS = [
  { key: 'mean', label: 'Mean (X̄)', Component: MeanTab },
  { key: 'variance', label: 'Variance (s²)', Component: VarianceTab },
  { key: 'proportion', label: 'Proportion (p̂)', Component: ProportionTab },
]

export default function SamplingDistributions() {
  const [active, setActive] = useState('mean')
  const Active = TABS.find((t) => t.key === active).Component

  return (
    <>
      <h1 className="page-title">Sampling Distributions</h1>
      <p className="page-desc">
        Probabilities for the sample mean, sample variance and sample proportion, with the solution steps.
      </p>

      <div role="tablist" style={{ display: 'flex', gap: 6, borderBottom: '1px solid #E3E6EF', marginBottom: 24, flexWrap: 'wrap' }}>
        {TABS.map((t) => (
          <button key={t.key} role="tab" type="button" aria-selected={active === t.key} onClick={() => setActive(t.key)}
            style={{ border: 0, background: 'none', font: 'inherit', padding: '10px 18px', cursor: 'pointer',
              marginBottom: -1, color: active === t.key ? '#3B4CCA' : '#5B6478', fontWeight: active === t.key ? 600 : 400,
              borderBottom: `2px solid ${active === t.key ? '#3B4CCA' : 'transparent'}` }}>
            {t.label}
          </button>
        ))}
      </div>

      <Active />
    </>
  )
}
