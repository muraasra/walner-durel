import { useTokenCheck } from '~/stores/useTokenCheck' // ou ~/composables/ selon ton organisation

export default defineNuxtRouteMiddleware(async (to) => {
  const PUBLIC_ROUTES = ['/login', '/register']

  // Laisse passer les routes publiques
  if (PUBLIC_ROUTES.includes(to.path)) {
    return
  }

  const token = useCookie<string | null>('auth_token')

  if (!token.value) {
    console.warn('[Middleware] Aucun token trouvé')
    return navigateTo('/login')
  }

  const isValid = await useTokenCheck()
  if (!isValid) {
    console.warn('[Middleware] Token invalide ou expiré')
    return navigateTo('/login')
  }

  console.log('[Middleware] Accès autorisé à', to.path)
})