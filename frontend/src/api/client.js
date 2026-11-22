import axios from 'axios'

// Base URL comes from frontend/.env (see .env.example).
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 15000,
})

/**
 * Every backend endpoint returns { result, steps, plot, notes }.
 * Example: const data = await post('/normal/probability', { mu: 0, sigma: 1, a: 1.96 })
 */
export async function post(path, body) {
  const { data } = await api.post(path, body)
  return data
}

export async function get(path) {
  const { data } = await api.get(path)
  return data
}

export default api
