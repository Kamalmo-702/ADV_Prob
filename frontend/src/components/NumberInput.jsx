import { useId } from 'react'

export default function NumberInput({ label, value, onChange, step = 'any', min, max, hint }) {
  const id = useId()
  return (
    <label className="field" htmlFor={id}>
      <span className="field-label">{label}</span>
      <input
        id={id}
        type="number"
        inputMode="decimal"
        value={value}
        step={step}
        min={min}
        max={max}
        onChange={(e) => onChange(e.target.value === '' ? '' : Number(e.target.value))}
      />
      {hint && <span className="field-hint">{hint}</span>}
    </label>
  )
}
