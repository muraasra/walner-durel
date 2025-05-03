// composables/useApi.ts
import { useAuthStore } from '@/stores/auth'

export function useApi<T = unknown>(url: string, options = {}) {
  const auth = useAuthStore()
  return useFetch<T>(url, {
    headers: auth.token
      ? { Authorization: `Bearer ${auth.token}` }
      : {},
    ...options,
    onRequestError({ response}){
      if (response?.status === 401) {
        auth.logout()
        navigateTo('/login')
      } 
    }
  })
}