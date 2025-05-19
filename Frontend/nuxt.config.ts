export default defineNuxtConfig({
  ssr: true,

  nitro: {
    preset: 'node-server'
  },

  devtools: { enabled: true },
  modules: ['@nuxt/ui', '@pinia/nuxt'],

  app: {
    head: {
      title: 'WALNER TECH',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'WALNER TECH - Gestion de stock et facturation' }
      ]
    }
  },

  css: ['~/assets/css/main.css'],

  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
    },
  },

  compatibilityDate: '2025-05-19'
})