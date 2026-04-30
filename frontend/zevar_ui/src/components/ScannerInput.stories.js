import ScannerInput from './ScannerInput.vue'

export default {
	title: 'Responsive/ScannerInput',
	component: ScannerInput,
	parameters: {
		viewport: {
			defaultViewport: 'lg',
		},
	},
	argTypes: {
		placeholder: { control: 'text' },
		showCamera: { control: 'boolean' },
		autoFocus: { control: 'boolean' },
	},
}

const Template = (args) => ({
	components: { ScannerInput },
	setup() { return { args } },
	template: `
		<div class="max-w-md p-4">
			<ScannerInput v-bind="args" @scan="(v) => $data.lastScan = v" />
			<p class="mt-2 text-sm text-gray-500">Simulates barcode scanner input. Type and press Enter.</p>
		</div>
	`,
	data: () => ({ lastScan: '' }),
})

export const Default = Template.bind({})
Default.args = {
	placeholder: 'Scan barcode or RFID tag...',
	showCamera: true,
	autoFocus: true,
}

export const NoCamera = Template.bind({})
NoCamera.args = {
	placeholder: 'Scan barcode...',
	showCamera: false,
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
