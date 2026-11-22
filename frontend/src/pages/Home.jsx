// Owner: Issue 1 - Foundation
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { get } from '../api/client.js'
import { MODULES } from '../nav.js'
import StepsViewer from '../components/StepsViewer.jsx'
import PlotCard from '../components/PlotCard.jsx'
import ErrorMessage from '../components/ErrorMessage.jsx'

// Standard normal curve, used only to prove PlotCard works.
const xs = Array.from({ length: 121 }, (_, i) => -3 + i * 0.05)
const ys = xs.map((x) => Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI))

function ApiStatus() {
  const [status, setStatus] = useState('checking')
  const [error, setError] = useState('')

  useEffect(() => {
    get('/health')
      .then(() => setStatus('online'))
      .catch(() => {
        setStatus('offline')
        setError('The API is not reachable. Start the backend (docker compose up, or uvicorn) and reload.')
      })
  }, [])

  return (
    <section className="card">
      <h2 className="card-title">Backend connection</h2>
      <p className={`status status-${status}`}>{status === 'checking' ? 'Checking…' : status === 'online' ? 'API is online' : 'API is offline'}</p>
      <ErrorMessage message={error} />
    </section>
  )
}

export default function Home() {
  return (
    <>
      <h1 className="page-title">Stats Lab</h1>
      <p className="page-desc">Calculators with full solution steps, and simulations that show why the formulas work.</p>

      <div className="grid">
        {MODULES.map((m) => (
          <Link key={m.path} to={m.path} className="card module-card">
            <h2 className="card-title">{m.label}</h2>
            <p className="muted">{m.summary}</p>
          </Link>
        ))}
      </div>

      <h2 className="section-title">Foundation check</h2>
      <p className="muted">Shared components and the API connection. Remove this section once every module is in.</p>
      <div className="grid">
        <ApiStatus />
        <StepsViewer title="StepsViewer (KaTeX)" steps={[String.raw`1-\alpha = 0.95 \Rightarrow \alpha = 0.05`, String.raw`z_{\alpha/2} = 1.96`, 'x^2 + 1 = 2']} />
      </div>
      <PlotCard title="PlotCard (Plotly): standard normal curve" x={xs} y={ys} />
    </>
  )
}
