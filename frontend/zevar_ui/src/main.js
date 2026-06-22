import './index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import router from './router'
import App from './App.vue'

import { Button, setConfig, frappeRequest, resourcesPlugin } from 'frappe-ui'

import { hardwareService } from '@/services/HardwareService.js'
hardwareService.connect()

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

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
			.register('/api/method/zevar_core.api.pos.serve_sw?v=24', { scope: '/pos/' })
			.then((registration) => {
				// Auto-activate new SW immediately
				registration.addEventListener('updatefound', () => {
					const newWorker = registration.installing
					newWorker.addEventListener('statechange', () => {
						if (newWorker.state === 'installed') {
							newWorker.postMessage({ type: 'SKIP_WAITING' })
						}
					})
				})

				// Check for updates every 2 minutes
				setInterval(() => registration.update(), 2 * 60 * 1000)
			})
			.catch((error) => {
				console.error('[App] Service Worker registration failed:', error)
			})

		navigator.serviceWorker.addEventListener('controllerchange', () => {
			if (window.__swReloadPending) return
			window.__swReloadPending = true
			window.location.reload()
		})

		// Listen for cache cleared messages
		navigator.serviceWorker.addEventListener('message', (event) => {
			if (event.data?.type === 'CACHE_CLEARED') {
				window.location.reload()
			}
		})
	})
}

// Global force refresh utility
window.__zevarForceRefresh = async function () {
	if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
		return new Promise((resolve) => {
			const mc = new MessageChannel()
			mc.port1.onmessage = () => {
				window.location.reload()
				resolve()
			}
			navigator.serviceWorker.controller.postMessage({ type: 'CLEAR_CACHE' }, [mc.port2])
			// Fallback reload after 2s if SW doesn't respond
			setTimeout(() => {
				window.location.reload()
				resolve()
			}, 2000)
		})
	} else {
		// No SW — just hard reload
		window.location.reload()
	}
}
