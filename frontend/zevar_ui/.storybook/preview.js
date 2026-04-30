/** @type { import('@storybook/vue3').Preview } */
import '../src/index.css'

const preview = {
	parameters: {
		actions: { argTypesRegex: '^on[A-Z].*' },
		controls: {
			matchers: {
				color: /(background|color)$/i,
				date: /Date$/i,
			},
		},
		viewport: {
			viewports: {
				xs: { name: 'XS Phone (375px)', styles: { width: '375px', height: '667px' } },
				sm: { name: 'SM Large Phone (640px)', styles: { width: '640px', height: '960px' } },
				md: { name: 'MD Tablet (768px)', styles: { width: '768px', height: '1024px' } },
				lg: { name: 'LG Laptop (1024px)', styles: { width: '1024px', height: '768px' } },
				xl: { name: 'XL Desktop (1280px)', styles: { width: '1280px', height: '800px' } },
				'2xl': { name: '2XL Wide (1536px)', styles: { width: '1536px', height: '900px' } },
			},
			defaultViewport: 'md',
		},
		backgrounds: {
			default: 'light',
			values: [
				{ name: 'light', value: '#FFEDD5' },
				{ name: 'dark', value: '#0F1115' },
			],
		},
	},
}

export default preview
