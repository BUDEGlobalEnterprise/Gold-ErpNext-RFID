<template>
	<BaseModal :show="true" max-width="max-w-sm" @close="$emit('close')">
		<template #header>
			<h3 class="text-lg font-bold text-gray-900 dark:text-white">Repair Claim Ticket</h3>
		</template>

		<div class="p-6">
			<div class="text-center">
				<div
					class="bg-white dark:bg-gray-950 p-4 rounded-lg border-2 border-dashed border-gray-300 dark:border-warm-border mb-4"
				>
					<div
						class="mx-auto mb-3 h-40 w-40 rounded-lg border border-gray-200 dark:border-gray-800 bg-[linear-gradient(45deg,#111_25%,transparent_25%,transparent_75%,#111_75%,#111),linear-gradient(45deg,#111_25%,transparent_25%,transparent_75%,#111_75%,#111)] bg-[length:24px_24px] bg-[position:0_0,12px_12px] opacity-80"
						aria-hidden="true"
					></div>
					<p class="text-xs text-gray-500 dark:text-gray-400">Scan placeholder</p>
				</div>

				<div class="space-y-2 text-left mb-4">
					<p class="text-2xl font-bold text-[#D4AF37] font-mono">{{ order.name }}</p>
					<p class="text-gray-600 dark:text-gray-400">{{ order.customer_name }}</p>
					<p class="text-sm text-gray-500">
						{{ formatDate(order.received_date || order.creation) }}
					</p>
				</div>

				<div class="rounded-lg bg-gray-50 dark:bg-warm-dark-900 p-3 text-left mb-4">
					<p class="text-xs uppercase tracking-wide text-gray-500 mb-1">Lookup Link</p>
					<p class="text-xs break-all text-gray-700 dark:text-gray-300">
						{{ lookupUrl }}
					</p>
				</div>
			</div>
		</div>

		<template #footer>
			<button
				@click="copyLookupUrl"
				class="flex-1 py-2 bg-gray-100 dark:bg-warm-dark-900 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-warm-dark-800"
			>
				Copy Link
			</button>
			<button
				@click="printQR"
				class="flex-1 py-2 bg-[#D4AF37] text-black rounded-lg text-sm font-medium hover:bg-[#c9a432]"
			>
				Print
			</button>
		</template>
	</BaseModal>
</template>

<script setup>
import { defineEmits, defineProps } from 'vue'
import { toast } from 'frappe-ui'
import { formatDate } from '@/utils/dates.js'
import BaseModal from './BaseModal.vue'

const props = defineProps({
	order: { type: Object, required: true },
})

defineEmits(['close'])

const lookupUrl = `${window.location.origin}/pos/repair-lookup#${props.order.name}`

async function copyLookupUrl() {
	try {
		await navigator.clipboard.writeText(lookupUrl)
		toast({
			title: 'Copied',
			message: 'Repair lookup link copied to clipboard',
			icon: 'check',
			intent: 'success',
		})
	} catch {
		toast({
			title: 'Copy Failed',
			message: 'Unable to copy the lookup link',
			icon: 'alert-triangle',
			intent: 'error',
		})
	}
}

function printQR() {
	const w = window.open('', '_blank')
	if (!w) return

	w.document.write(`
		<html><head><title>Repair Ticket - ${props.order.name}</title>
		<style>
			body { font-family: sans-serif; text-align: center; padding: 20px; }
			.ticket { border: 2px dashed #ccc; padding: 20px; display: inline-block; max-width: 320px; }
			.code {
				width: 160px;
				height: 160px;
				margin: 0 auto 12px;
				background-image:
					linear-gradient(45deg, #111 25%, transparent 25%, transparent 75%, #111 75%, #111),
					linear-gradient(45deg, #111 25%, transparent 25%, transparent 75%, #111 75%, #111);
				background-size: 24px 24px;
				background-position: 0 0, 12px 12px;
			}
			.link { font-size: 11px; word-break: break-all; color: #666; }
		</style></head><body>
		<div class="ticket">
			<h2>ZEVAR JEWELERS</h2>
			<h1>${props.order.name}</h1>
			<div class="code"></div>
			<p>${props.order.customer_name || ''}</p>
			<p>Use this link to check status:</p>
			<p class="link">${lookupUrl}</p>
		</div>
		</body></html>
	`)
	w.document.close()
	w.print()
}
</script>
