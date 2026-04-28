import './index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

import { Button, setConfig, frappeRequest, resourcesPlugin } from 'frappe-ui'

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
			.register('/pos/sw.js', { scope: '/pos/' })
			.then((registration) => {
				// Service Worker registered
			})
			.catch((error) => {
				console.error('[App] Service Worker registration failed:', error)
			})
	})
}
