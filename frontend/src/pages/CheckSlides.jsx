// Owner: Issue 5 - Check the Slides
import { useEffect, useMemo, useState } from 'react'
import { get } from '../api/client.js'
import ErrorMessage from '../components/ErrorMessage.jsx'
import StepsViewer from '../components/StepsViewer.jsx'

export default function CheckSlides() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [errorsOnly, setErrorsOnly] = useState(false)

  useEffect(() => {
    get('/verify/slides')
      .then((res) => setData(res))
      .catch((err) => setError(err?.response?.data?.detail || err?.message || 'Failed to load slide verification data.'))
      .finally(() => setLoading(false))
  }, [])

  const res = data?.result
  const items = res?.items || []

  const groupedByLecture = useMemo(() => {
    const filtered = errorsOnly ? items.filter((item) => item.category === 'error') : items
    const groups = new Map()
    for (const item of filtered) {
      if (!groups.has(item.lecture)) {
        groups.set(item.lecture, [])
      }
      groups.get(item.lecture).push(item)
    }
    return Array.from(groups.entries())
  }, [items, errorsOnly])

  return (
    <>
      <h1 className="page-title">Check the Slides</h1>
      <p className="page-desc">
        Lecture slide answers compared against exact values computed with SciPy.
      </p>

      {error && <ErrorMessage message={error} />}
      {loading && <p className="muted">Loading lecture audit…</p>}

      {res && (
        <>
          <section className="card">
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', alignItems: 'center' }}>
                <span className="badge" style={{ background: '#FCEBEA', color: '#B3261E' }}>
                  {res.error_count} slide errors
                </span>
                <span className="badge">
                  {res.rounding_count} rounding differences
                </span>
              </div>

              <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '14px', fontWeight: 600 }}>
                <input
                  type="checkbox"
                  checked={errorsOnly}
                  onChange={(e) => setErrorsOnly(e.target.checked)}
                />
                Errors only
              </label>
            </div>
          </section>

          {groupedByLecture.map(([lecture, lectureItems]) => (
            <section className="card" key={lecture}>
              <h2 className="card-title">{lecture}</h2>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #E3E6EF', textAlign: 'left' }}>
                      <th style={{ padding: '10px 8px' }}>Example</th>
                      <th style={{ padding: '10px 8px' }}>Slide Answer</th>
                      <th style={{ padding: '10px 8px' }}>Exact (SciPy)</th>
                      <th style={{ padding: '10px 8px' }}>Type</th>
                      <th style={{ padding: '10px 8px' }}>Explanation</th>
                    </tr>
                  </thead>
                  <tbody>
                    {lectureItems.map((item) => {
                      const isError = item.category === 'error'
                      return (
                        <tr key={item.id} style={{ borderBottom: '1px solid #E3E6EF', verticalAlign: 'top' }}>
                          <td style={{ padding: '10px 8px', fontWeight: 600 }}>{item.topic}</td>
                          <td style={{ padding: '10px 8px', color: isError ? '#B3261E' : '#5B6478', fontFamily: 'monospace' }}>
                            {item.slide_answer}
                          </td>
                          <td style={{ padding: '10px 8px', color: '#0B6B5F', fontWeight: 600, fontFamily: 'monospace' }}>
                            {item.exact_answer}
                          </td>
                          <td style={{ padding: '10px 8px' }}>
                            <span
                              className="badge"
                              style={
                                isError
                                  ? { background: '#FCEBEA', color: '#B3261E' }
                                  : { background: '#EEF0FD', color: '#3B4CCA' }
                              }
                            >
                              {isError ? 'Error' : 'Rounding'}
                            </span>
                          </td>
                          <td style={{ padding: '10px 8px', color: '#14213D' }}>{item.explanation}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </section>
          ))}

          <StepsViewer steps={data.steps} title="Audit method" />
        </>
      )}
    </>
  )
}