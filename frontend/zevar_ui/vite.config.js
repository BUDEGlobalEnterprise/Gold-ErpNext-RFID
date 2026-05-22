import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import frappeui from 'frappe-ui/vite'
import Icons from 'unplugin-icons/vite'

export default defineConfig({
	base: '/assets/zevar_core/pos/',
	server: {
		port: 8080,
		strictPort: true,
		host: true,
		proxy: {
			'^/(app|api|assets|files|private)': {
				target: 'http://127.0.0.1:8000',
				ws: true,
				changeOrigin: true,
				headers: {
					'X-Frappe-Site-Name': 'zevar.localhost',
				},
			},
		},
	},
	plugins: [frappeui(), Icons({ compiler: 'vue3' }), vue()],
	resolve: {
		alias: {
			'@': path.resolve(__dirname, './src'),
		},
	},
	build: {
		outDir: path.resolve(__dirname, '../../zevar_core/public/pos'),
		emptyOutDir: true,
		target: 'es2015',
		manifest: true,
	},
	optimizeDeps: {
		exclude: ['frappe-ui'],
		include: ['showdown', 'engine.io-client'],
	},
	test: {
		globals: true,
		environment: 'jsdom',
		setupFiles: ['./tests/setup.js'],
		include: ['tests/**/*.spec.js'],
		alias: {
			'@': path.resolve(__dirname, './src'),
		},
	},
})
