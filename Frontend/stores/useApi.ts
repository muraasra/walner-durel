


// composables/useApi.ts
import { useAuthStore } from '@/stores/auth'

export async function useApi<T = unknown>(path: string, options: any = {}) {
  const { public: { apiBase } } = useRuntimeConfig()
  const auth = useAuthStore()
  const url = path.startsWith('http') ? path : `${apiBase}${path.startsWith('/') ? path : '/' + path}`

  try {
    const data = await $fetch<T>(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
        ...(options.headers || {})
      }
    })
    return { data: ref(data as T), error: ref(null) }
  } catch (err: any) {
    // err.data = payload d’erreur DRF (ex: { boutique: ["This field is required."] })
    console.error('API Error:', err?.data || err)
    return { data: ref(null), error: ref(err?.data || err) }
  }
}
