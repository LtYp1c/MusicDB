export function setAuth({ userId, role, username }) {
  localStorage.setItem('auth_user_id', String(userId || ''))
  localStorage.setItem('auth_role', role || 'user')
  if (username) localStorage.setItem('auth_username', username)
}

export function clearAuth() {
  localStorage.removeItem('auth_user_id')
  localStorage.removeItem('auth_role')
  localStorage.removeItem('auth_username')
}

export function getRole() {
  return localStorage.getItem('auth_role') || 'user'
}

export function getUserId() {
  const id = localStorage.getItem('auth_user_id')
  return id ? Number(id) : null
}

export function isAdmin() {
  return getRole() === 'admin'
}

export function isAuthed() {
  return !!localStorage.getItem('auth_role')
}

export function getUsername() {
  return localStorage.getItem('auth_username') || null
}