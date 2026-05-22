module.exports = {
	darkMode: 'class',
	presets: [require('frappe-ui/tailwind')],
	content: [
		'./index.html',
		'./src/**/*.{vue,js,ts,jsx,tsx}',
		'./node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
	],
	theme: {
		// We define fontFamily HERE to override defaults, not in 'extend'
		fontFamily: {
			sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
			serif: ['Cinzel', 'ui-serif', 'Georgia', 'serif'],
			display: ['Spline Sans', 'sans-serif'],
			portal: ['Plus Jakarta Sans', 'sans-serif'],
			mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
		},
		// Breakpoint bands aligned with plan DEC-UI-001
		screens: {
			xs: '375px',
			sm: '640px',
			md: '768px',
			lg: '1024px',
			xl: '1280px',
			'2xl': '1536px',
		},
		extend: {
			colors: {
				white: '#FAF8F5',
				'portal-primary': '#25c0f4',
				'portal-accent-teal': '#1de9b6',
				'portal-accent-indigo': '#536dfe',
				'portal-accent-peach': '#ffccb3',
				'portal-bg-dark': '#0a0f12',
				'portal-bg-purple': '#191022',
				// Warm amber dark theme (jewelry POS)
				'warm-dark-950': '#1a1610',
				'warm-dark-900': '#1f1a12',
				'warm-dark-800': '#2a2318',
				'warm-dark-700': '#3a3225',
				'warm-dark-600': '#4a4235',
				'warm-card': '#1c1810',
				'warm-border': '#3a3225',
				'warm-border-subtle': '#2a2518',
				// Gold palette
				gold: {
					DEFAULT: '#D4AF37',
					light: '#F2E6A0',
					dark: '#B8941E',
				},
			},
			spacing: {
				'safe-top': 'env(safe-area-inset-top, 0px)',
				'safe-bottom': 'env(safe-area-inset-bottom, 0px)',
				'safe-left': 'env(safe-area-inset-left, 0px)',
				'safe-right': 'env(safe-area-inset-right, 0px)',
			},
			minHeight: {
				touch: '44px',
			},
			minWidth: {
				touch: '44px',
			},
		},
	},
	plugins: [
		// Touch target plugin — adds .touch-target utility
		function ({ addUtilities }) {
			addUtilities({
				'.touch-target': {
					'min-width': '44px',
					'min-height': '44px',
					'display': 'inline-flex',
					'align-items': 'center',
					'justify-content': 'center',
				},
				'.dvh-full': {
					height: '100dvh',
				},
				'.dvh-screen': {
					'min-height': '100dvh',
				},
				'.no-scrollbar': {
					'-ms-overflow-style': 'none',
					'scrollbar-width': 'none',
				},
				'.no-scrollbar::-webkit-scrollbar': {
					display: 'none',
				},
				'.bottom-sheet-radius': {
					'border-radius': '16px 16px 0 0',
				},
			})
		},
	],
}
