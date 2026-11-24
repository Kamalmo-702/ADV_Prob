// Owner: Issue 3 - Sampling Distributions
import { useState } from 'react'
import { post } from '../../api/client.js'

export function formatApiError(err) {
  const detail = err?.response?.data?.detail
  if (Array.isArray(detail)) {
    return detail.map((d) => `${d.loc?.slice(-1)[0] || 'input'}: ${d.msg}`).join('; ')
  }
  if (typeof detail === 'string') return detail
  return err?.message || 'Request failed.'
}

/** Posts to a /sampling endpoint. Empty-string fields are dropped from the body. */
export default function useSolve(path) {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function run(body) {
    const clean = Object.fromEntries(Object.entries(body).filter(([, v]) => v !== '' && v !== null))
    setLoading(true)
    setError('')
    try {
      setData(await post(path, clean))
    } catch (err) {
      setError(formatApiError(err))
    } finally {
      setLoading(false)
    }
  }

  return { data, error, loading, run }
}
