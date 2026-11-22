import createPlotlyComponent from 'react-plotly.js/factory'
import Plotly from 'plotly.js-dist-min'

const Plot = createPlotlyComponent(Plotly)

/**
 * Card around a Plotly chart.
 * Simple use:   <PlotCard title="..." x={[...]} y={[...]} />
 * Full control: <PlotCard title="..." data={[trace1, trace2]} layout={{...}} />
 */
export default function PlotCard({ title, x, y, data, layout = {}, ariaLabel }) {
  const traces = data || [{ x, y, type: 'scatter', mode: 'lines', line: { color: '#3B4CCA', width: 3 } }]
  return (
    <section className="card" role="img" aria-label={ariaLabel || title}>
      {title && <h2 className="card-title">{title}</h2>}
      <Plot
        data={traces}
        layout={{
          autosize: true,
          margin: { t: 10, r: 10, b: 40, l: 45 },
          paper_bgcolor: 'rgba(0,0,0,0)',
          plot_bgcolor: 'rgba(0,0,0,0)',
          font: { family: 'Inter, system-ui, sans-serif', color: '#14213D' },
          ...layout,
        }}
        config={{ displaylogo: false, responsive: true }}
        useResizeHandler
        style={{ width: '100%', height: '320px' }}
      />
    </section>
  )
}
