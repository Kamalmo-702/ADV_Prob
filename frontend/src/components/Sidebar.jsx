import { Link, NavLink } from 'react-router-dom'
import { MODULES } from '../nav.js'

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <Link to="/" className="brand">
        <span className="brand-mark" aria-hidden="true" />
        <span className="brand-name">Stats Lab</span>
      </Link>
      <nav aria-label="Modules">
        {MODULES.map((m) => (
          <NavLink key={m.path} to={m.path} className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
            {m.label}
          </NavLink>
        ))}
      </nav>
      <p className="sidebar-foot">
        Advanced Statistics &amp; Probability
        <br />
        Horus University
      </p>
    </aside>
  )
}
