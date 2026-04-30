<template>
	<div class="tag-print-preview" ref="previewRef">
		<div class="border border-gray-300 dark:border-warm-border rounded-lg p-4 bg-white dark:bg-warm-card print-area" :style="tagStyle">
			<div class="flex items-center justify-between mb-2">
				<span class="text-[10px] font-bold uppercase tracking-wider text-gray-500">Zevar Jewelers</span>
				<span class="text-[10px] text-gray-400">{{ itemData.storeCode || '' }}</span>
			</div>
			<div class="text-center my-3">
				<div class="text-lg font-bold text-gray-900 dark:text-white">
					{{ formatCurrency(itemData.price) }}
				</div>
				<div v-if="itemData.metal" class="text-xs text-gray-500 mt-1">
					{{ itemData.metal }} {{ itemData.purity ? `• ${itemData.purity}` : '' }}
				</div>
			</div>
			<div class="flex items-center justify-center my-3">
				<svg class="w-full h-10" :viewBox="`0 0 200 40`">
					<rect x="0" y="0" width="200" height="40" fill="white" stroke="black" stroke-width="0.5" />
					<text x="100" y="25" text-anchor="middle" font-size="10" font-family="monospace">
						{{ itemData.barcode || itemData.serialNo || '***' }}
					</text>
				</svg>
			</div>
			<div class="flex justify-between text-[9px] text-gray-400">
				<span>{{ itemData.itemCode || '' }}</span>
				<span>{{ itemData.vendorSku || '' }}</span>
			</div>
			<div v-if="itemData.weight" class="text-center text-[10px] text-gray-500 mt-1">
				{{ itemData.weight }}g
			</div>
		</div>
		<div class="flex gap-2 mt-3">
			<button
				@click="printTag"
				class="flex-1 py-2 bg-[#D4AF37] text-white rounded-lg text-sm font-medium hover:bg-[#C4A030] transition"
			>
				Print Tag
			</button>
			<button
				@click="$emit('close')"
				class="flex-1 py-2 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 transition"
			>
				Skip
			</button>
		</div>
	</div>
</template>

<script setup>
const props = defineProps({
	itemData: {
		type: Object,
		default: () => ({
			barcode: '',
			serialNo: '',
			itemCode: '',
			itemName: '',
			price: 0,
			metal: '',
			purity: '',
			weight: 0,
			vendorSku: '',
			storeCode: '',
		}),
	},
	tagStyle: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['close', 'printed'])

function formatCurrency(val) {
	if (!val) return '$0.00'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)
}

function printTag() {
	const printContent = document.querySelector('.print-area')
	if (!printContent) return
	const win = window.open('', '_blank', 'width=400,height=300')
	win.document.write(`
		<html><head><title>Tag</title>
		<style>body{margin:0;font-family:sans-serif;}${getComputedStyles(printContent)}</style>
		</head><body>${printContent.outerHTML}</body></html>
	`)
	win.document.close()
	win.focus()
	win.print()
	win.close()
	emit('printed')
}

function getComputedStyles(el) {
	return ''
}
</script>
