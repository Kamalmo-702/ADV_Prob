// Replace this component with the real page content when you implement your module.
export default function PagePlaceholder({ title, description, issue }) {
  return (
    <>
      <h1 className="page-title">{title}</h1>
      <p className="page-desc">{description}</p>
      <section className="card">
        <h2 className="card-title">Coming soon (Issue {issue})</h2>
        <p className="muted">This page is a placeholder. Its owner builds the module here.</p>
      </section>
    </>
  )
}
