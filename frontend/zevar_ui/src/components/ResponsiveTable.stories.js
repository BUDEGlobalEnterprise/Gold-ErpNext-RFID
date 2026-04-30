import ResponsiveTable from './ResponsiveTable.vue'

export default {
	title: 'Responsive/ResponsiveTable',
	component: ResponsiveTable,
	parameters: {
		viewport: {
			defaultViewport: 'lg',
		},
	},
	argTypes: {
		rowKey: { control: 'text' },
		emptyText: { control: 'text' },
	},
}

const Template = (args) => ({
	components: { ResponsiveTable },
	setup() { return { args } },
	template: '<ResponsiveTable v-bind="args" />',
})

const sampleColumns = [
	{ key: 'name', label: 'Item', primary: true },
	{ key: 'code', label: 'SKU', secondary: true },
	{ key: 'metal', label: 'Metal' },
	{ key: 'stock', label: 'Stock', align: 'right' },
	{ key: 'price', label: 'Price', align: 'right', format: (v) => '$' + v.toLocaleString() },
	{ key: 'status', label: 'Status', hideMobile: true },
]

const sampleRows = [
	{ name: 'Diamond Ring 14K', code: 'DR-001', metal: 'Gold 14K', stock: 3, price: 2450, status: 'In Stock' },
	{ name: 'Gold Chain 22K', code: 'GC-042', metal: 'Gold 22K', stock: 1, price: 890, status: 'Low Stock' },
	{ name: 'Silver Bracelet', code: 'SB-015', metal: 'Silver 925', stock: 12, price: 185, status: 'In Stock' },
	{ name: 'Pearl Earrings', code: 'PE-008', metal: 'Pearl', stock: 0, price: 320, status: 'Out of Stock' },
	{ name: 'Platinum Band', code: 'PB-003', metal: 'Platinum', stock: 2, price: 3200, status: 'In Stock' },
]

export const Default = Template.bind({})
Default.args = {
	columns: sampleColumns,
	rows: sampleRows,
	rowKey: 'code',
	emptyText: 'No items found',
}

export const Empty = Template.bind({})
Empty.args = {
	columns: sampleColumns,
	rows: [],
	rowKey: 'code',
	emptyText: 'No items match your filters',
}

// Viewport stories — use Storybook viewport addon to switch
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
