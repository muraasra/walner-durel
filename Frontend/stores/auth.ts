import { defineStore } from 'pinia'
import { useCookie } from '#app'
import { ref } from 'vue'

interface User {
  id: number;
  username: string;
  email?: string;
  role?: string;
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)

  const cookieToken = useCookie<string | null>('auth_token', {
    default: () => null,
    maxAge: 60 * 60*24 , // 1 jour
    httpOnly: false
  })

  const token = ref(cookieToken.value)

  function setToken(newToken: string) {
    token.value = newToken
    cookieToken.value = newToken
    if (process.client) {
      localStorage.setItem('access_token', newToken)
    }
  }

  function setUser(data: User) {
    user.value = data
    if (process.client) {
      localStorage.setItem('user', JSON.stringify(data))
    }
  }

  function restoreUser() {
    if (process.client) {
      const storedUser = localStorage.getItem('user')
      if (storedUser) user.value = JSON.parse(storedUser)
    }
  }

  function logout() {
    token.value = null
    cookieToken.value = null
    user.value = null
    if (process.client) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
    }
    navigateTo('/login')
  }

  // restauration automatique si client
  if (process.client) {
    const storedToken = localStorage.getItem('access_token')
    if (storedToken) {
      token.value = storedToken
      cookieToken.value = storedToken
    }
    restoreUser()
  }

  return { user, token, setToken, setUser, logout }
})