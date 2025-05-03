import { useAuthStore } from '@/stores/auth'

export async function useTokenCheck(): Promise<boolean> {
  const auth = useAuthStore()

  if (!auth.token) return false

  try {
    const { error } = await useFetch('http://127.0.0.1:8000/api/token/verify/', {
      method: 'POST',
      body: { token: auth.token },
      server: false // assure que ce composable fonctionne aussi côté client
    })

    if (error.value) {
      console.warn('[TokenCheck] Token invalide ou expiré.')
      auth.logout()
      return false
    }

    return true
  } catch (err) {
    console.error('[TokenCheck] Erreur réseau ou serveur :', err)
    auth.logout()
    return false
  }
}