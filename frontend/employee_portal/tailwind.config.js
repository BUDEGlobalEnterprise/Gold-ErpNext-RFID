const colors = require('tailwindcss/colors')

module.exports = {
	darkMode: "class",
	presets: [require("frappe-ui/tailwind")],
	content: [
		"./index.html",
		"./src/**/*.{vue,js,ts,jsx,tsx}",
		"./node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}",
	],
	theme: {
		fontFamily: {
			sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
			portal: ["Plus Jakarta Sans", "sans-serif"],
		},
		extend: {
			colors: {
				emerald: colors.emerald,
				amber: colors.amber,
				red: colors.red,
				blue: colors.blue,
				slate: colors.slate,
				gray: colors.gray,
				primary: {
					DEFAULT: "#044434",
					50: "#ecfdf5",
					100: "#d1fae5",
					200: "#a7f3d0",
					300: "#6ee7b7",
					400: "#34d399",
					500: "#10b981",
					600: "#059669",
					700: "#047857",
					800: "#044434",
					900: "#022c22",
					950: "#011c16",
				},
				"background-light": "#f8f9fa",
				"background-dark": "#05070a",
				"card-bg": "#ffffff",
				"emerald-glow": "#10b981",
				"gold-accent": "#c5a059", // More metallic gold
				"diamond-white": "#f1f5f9",
				"glass-border": "rgba(0, 0, 0, 0.04)",
			},
			fontFamily: {
				sans: ["Inter", "sans-serif"],
				display: ["Plus Jakarta Sans", "sans-serif"],
				serif: ["Cinzel", "serif"],
			},
			borderRadius: {
				xl: "0.75rem",
				"2xl": "1rem",
				"3xl": "1.5rem",
				"4xl": "2.5rem",
			},
			transitionDuration: {
				400: "400ms",
			},
			boxShadow: {
				"premium": "0 10px 30px -10px rgba(0, 0, 0, 0.1)",
				"premium-hover": "0 20px 40px -15px rgba(0, 0, 0, 0.15)",
				"glow-emerald": "0 0 20px rgba(16, 185, 129, 0.2)",
			},
		},
	},
	plugins: [],
};
