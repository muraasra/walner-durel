// composables/useApi.ts
import { useFetch } from '#app'
import { useAuthStore } from '@/stores/auth'

export async function useApi<T = unknown>(url: string, options = {}) {
  const auth = useAuthStore()
  
  try {
    const { data, error } = await useFetch<T>(url, {
      headers: {
        'Content-Type': 'application/json',
        ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {})
      },
      ...options,
      onRequestError({ response }) {
        if (response?.status === 401) {
          auth.logout()
          navigateTo('/login')
        }
      }
    })

    return { data, error }
  } catch (e) {
    console.error('API Error:', e)
    return { 
      data: ref(null),
      error: ref(e instanceof Error ? e : new Error('Une erreur est survenue'))
    }
  }
}