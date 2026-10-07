const API_URL = import.meta.env.VITE_API_URL || '/api'

export function getUserId() {
  let id = localStorage.getItem('ltss_user_id')
  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem('ltss_user_id', id)
  }
  return id
}

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', 'X-User-ID': getUserId(), ...(options.headers || {}) },
    ...options,
  })
  if (!response.ok) {
    const body = await response.text()
    throw new Error(body || `API error ${response.status}`)
  }
  return response.json()
}

export const api = {
  health: () => request('/health'),
  modes: () => request('/modes'),
  createSession: (mode) => request('/sessions', {
    method: 'POST',
    body: JSON.stringify({ user_id: getUserId(), mode }),
  }),
  sessions: () => request(`/sessions/${getUserId()}`),
  messages: (conversationId) => request(`/sessions/${conversationId}/messages`),
  send: (conversationId, content) => request(`/sessions/${conversationId}/messages`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  }),
}
