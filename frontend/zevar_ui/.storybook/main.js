/** @type { import('@storybook/vue3-vite').StorybookConfig } */
const config = {
	stories: ['../src/**/*.stories.@(js|jsx|ts|tsx|mdx)'],
	addons: ['@storybook/addon-viewport', '@storybook/addon-a11y'],
	framework: {
		name: '@storybook/vue3-vite',
		options: {},
	},
	docs: {
		autodocs: 'tag',
	},
	viewport: {
		viewports: {
			xs: { name: 'XS (375px)', styles: { width: '375px', height: '667px' } },
			sm: { name: 'SM (640px)', styles: { width: '640px', height: '960px' } },
			md: { name: 'MD (768px)', styles: { width: '768px', height: '1024px' } },
			lg: { name: 'LG (1024px)', styles: { width: '1024px', height: '768px' } },
			xl: { name: 'XL (1280px)', styles: { width: '1280px', height: '800px' } },
			'2xl': { name: '2XL (1536px)', styles: { width: '1536px', height: '900px' } },
		},
		defaultViewport: 'md',
	},
}
export default config
