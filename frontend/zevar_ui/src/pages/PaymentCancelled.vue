<template>
	<div class="min-h-screen bg-gray-50 dark:bg-[#0F1115] flex items-center justify-center p-4">
		<div class="max-w-md w-full text-center" data-testid="payment-cancelled-view">
			<div
				class="bg-white dark:bg-[#1a1c23] rounded-2xl shadow-xl border border-gray-100 dark:border-gray-800 p-8 mb-6"
			>
				<div
					class="w-20 h-20 mx-auto mb-6 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center"
				>
					<svg
						class="w-10 h-10 text-amber-600 dark:text-amber-400"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				</div>

				<h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
					Payment Cancelled
				</h1>
				<p class="text-gray-500 dark:text-gray-400 mb-4">
					Your payment was not processed. No charges have been made.
				</p>

				<div
					v-if="repairOrder"
					class="bg-gray-50 dark:bg-[#15171e] rounded-xl p-4 border border-gray-100 dark:border-gray-800"
				>
					<p class="text-sm text-gray-500 dark:text-gray-400">
						Repair Order:
						<span class="font-mono font-bold text-gray-900 dark:text-white">{{
							repairOrder
						}}</span>
					</p>
				</div>
			</div>

			<router-link
				to="/repair-portal"
				class="block w-full py-3 bg-gray-900 dark:bg-[#D4AF37] text-white dark:text-black text-center rounded-xl font-bold hover:opacity-90 transition mb-3"
				data-testid="return-to-portal-btn"
			>
				Return to Repair Portal
			</router-link>

			<p class="text-xs text-gray-400 dark:text-gray-600">
				You can try again from the Repair Portal at any time.
			</p>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const repairOrder = computed(() => route.query.repair || '')
</script>
