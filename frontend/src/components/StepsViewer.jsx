import katex from 'katex'
import 'katex/dist/katex.min.css'

/**
 * Renders solution steps. `steps` is an array of LaTeX strings, e.g. ["z_{\\alpha/2} = 1.96"].
 * Invalid LaTeX is shown as red text instead of crashing the page.
 */
export default function StepsViewer({ steps = [], title = 'Solution steps' }) {
  if (!steps.length) return null
  return (
    <section className="card">
      <h2 className="card-title">{title}</h2>
      <ol className="steps">
        {steps.map((latex, i) => (
          <li key={i} dangerouslySetInnerHTML={{ __html: katex.renderToString(latex, { throwOnError: false, displayMode: false }) }} />
        ))}
      </ol>
    </section>
  )
}
