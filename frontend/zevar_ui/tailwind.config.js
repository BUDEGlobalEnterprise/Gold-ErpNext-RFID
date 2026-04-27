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
		},
		extend: {
			colors: {
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
			},
		},
	},
	plugins: [],
}
