import ResponsiveModal from './ResponsiveModal.vue'
import { ref } from 'vue'

export default {
	title: 'Responsive/ResponsiveModal',
	component: ResponsiveModal,
	parameters: {
		viewport: {
			defaultViewport: 'lg',
		},
	},
}

const Template = (args) => ({
	components: { ResponsiveModal },
	setup() {
		const show = ref(true)
		return { args, show }
	},
	template: `
		<button @click="show = true" class="px-4 py-2 bg-blue-600 text-white rounded-lg">Open Modal</button>
		<ResponsiveModal v-bind="args" :show="show" @close="show = false">
			<template #header>
				<h3 class="text-heading-sm text-gray-900 dark:text-white">Sample Modal</h3>
			</template>
			<div class="p-6">
				<p class="text-body text-gray-600 dark:text-gray-400">
					This modal adapts: bottom-sheet on mobile, centered modal on desktop.
					Try resizing the viewport or switching viewports in the toolbar.
				</p>
				<p class="text-body mt-4">On mobile, swipe down to dismiss.</p>
			</div>
			<template #footer>
				<button @click="show = false" class="px-4 py-2 bg-gray-200 rounded-lg text-sm font-medium">Cancel</button>
				<button @click="show = false" class="px-4 py-2 bg-[#D4AF37] text-white rounded-lg text-sm font-bold">Confirm</button>
			</template>
		</ResponsiveModal>
	`,
})

export const Default = Template.bind({})
Default.args = {
	persistent: false,
	scrollable: true,
}

export const Persistent = Template.bind({})
Persistent.args = {
	persistent: true,
}

export const MobileView = Template.bind({})
MobileView.args = { ...Default.args }
MobileView.parameters = {
	viewport: { defaultViewport: 'xs' },
}

export const TabletView = Template.bind({})
TabletView.args = { ...Default.args }
TabletView.parameters = {
	viewport: { defaultViewport: 'md' },
}

export const DesktopView = Template.bind({})
DesktopView.args = { ...Default.args }
DesktopView.parameters = {
	viewport: { defaultViewport: 'xl' },
}
