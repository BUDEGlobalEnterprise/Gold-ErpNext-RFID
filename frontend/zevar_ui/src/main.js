import './index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

import { Button, setConfig, frappeRequest, resourcesPlugin } from 'frappe-ui'

import { hardwareService } from '@/services/HardwareService.js'
hardwareService.connect()

const app = createApp(App)
const pinia = createPinia()

setConfig('resourceFetcher', frappeRequest)

app.use(pinia)
// Ensure the theme store runs on boot so .dark class is applied before first paint
import { useUIStore } from '@/stores/ui.js'
// Call once to initialize (sets .dark class on <html> if stored preference is dark)
useUIStore()
app.use(router)
app.use(resourcesPlugin)

app.component('Button', Button)
app.mount('#app')

// Register Service Worker for offline support
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/api/method/zevar_core.api.pos.serve_sw?v=13', { scope: '/pos/' })
      .then((registration) => {
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              newWorker.postMessage({ type: 'SKIP_WAITING' })
            }
          })
        })

        setInterval(() => registration.update(), 5 * 60 * 1000)
      })
      .catch((error) => {
        console.error('[App] Service Worker registration failed:', error)
      })

    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (window.__swReloadPending) return
      window.__swReloadPending = true
      window.location.reload()
    })
  })
}
