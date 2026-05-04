<template>
	<Teleport to="body">
		<Transition
			enter-active-class="transition-opacity duration-200"
			enter-from-class="opacity-0"
			enter-to-class="opacity-100"
			leave-active-class="transition-opacity duration-150"
			leave-from-class="opacity-100"
			leave-to-class="opacity-0"
		>
			<div
				v-if="show"
				class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[1000] p-4"
				@click.self="$emit('cancel')"
			>
				<div
					class="bg-white dark:bg-warm-card rounded-2xl shadow-2xl max-w-md w-full overflow-hidden"
				>
					<div class="p-6 bg-red-500/10 border-b border-red-500/20">
						<div class="flex items-center gap-3">
							<div
								class="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center shrink-0"
							>
								<svg
									class="w-5 h-5 text-red-500"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
									/>
								</svg>
							</div>
							<div>
								<h3 class="font-bold text-gray-900 dark:text-white">
									Manager Override Required
								</h3>
								<p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
									Cash variance exceeds the allowed threshold
								</p>
							</div>
						</div>
					</div>

					<div class="p-6 space-y-4">
						<div
							class="flex justify-between text-sm bg-gray-50 dark:bg-warm-dark-700/50 p-3 rounded-lg"
						>
							<span class="text-gray-500 dark:text-gray-400">Variance Amount</span>
							<span class="font-mono font-bold text-red-500">
								${{ formatAmount(Math.abs(variance)) }}
							</span>
						</div>
						<div
							class="flex justify-between text-sm bg-gray-50 dark:bg-warm-dark-700/50 p-3 rounded-lg"
						>
							<span class="text-gray-500 dark:text-gray-400">Allowed Threshold</span>
							<span class="font-mono font-bold text-gray-700 dark:text-gray-300">
								${{ formatAmount(threshold) }}
							</span>
						</div>

						<div>
							<label
								class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2"
								>Manager PIN</label
							>
							<input
								ref="pinInputRef"
								v-model="pin"
								type="password"
								placeholder="Enter manager PIN"
								maxlength="8"
								class="w-full px-4 py-3 bg-white dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-gray-900 dark:text-white text-center text-lg tracking-[0.3em] focus:ring-2 focus:ring-[#D4AF37] focus:border-[#D4AF37] outline-none font-mono"
								@keyup.enter="verifyPin"
							/>
						</div>

						<div
							v-if="errorMessage"
							class="text-sm text-red-500 bg-red-50 dark:bg-red-500/10 p-3 rounded-lg"
						>
							{{ errorMessage }}
						</div>
					</div>

					<div
						class="p-4 border-t border-gray-100 dark:border-warm-border/50 flex gap-3"
					>
						<button
							@click="$emit('cancel')"
							:disabled="verifying"
							class="flex-1 py-2.5 rounded-lg font-medium text-sm border border-gray-200 dark:border-warm-border text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition disabled:opacity-50"
						>
							Cancel
						</button>
						<button
							@click="verifyPin"
							:disabled="verifying || !pin || pin.length < 4"
							class="flex-1 py-2.5 rounded-lg font-bold text-sm bg-[#D4AF37] text-black hover:bg-[#b5952f] transition disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
						>
							{{ verifying ? 'Verifying...' : 'Authorize Override' }}
						</button>
					</div>
				</div>
			</div>
		</Transition>
	</Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { createResource } from 'frappe-ui'

const props = defineProps({
	show: Boolean,
	variance: { type: Number, default: 0 },
	threshold: { type: Number, default: 5 },
})

const emit = defineEmits(['approved', 'cancel'])

const pin = ref('')
const verifying = ref(false)
const errorMessage = ref('')
const pinInputRef = ref(null)

const verifyPinResource = createResource({
	url: 'zevar_core.api.permissions.verify_manager_pin',
	auto: false,
})

function formatAmount(amount) {
	if (amount === null || amount === undefined) return '0.00'
	return Number(amount).toFixed(2)
}

async function verifyPin() {
	if (!pin.value || pin.value.length < 4) {
		errorMessage.value = 'PIN must be at least 4 characters'
		return
	}

	verifying.value = true
	errorMessage.value = ''

	try {
		const result = await verifyPinResource.submit({ pin: pin.value })
		if (result && result.user) {
			emit('approved', { manager_user: result.user, manager_name: result.full_name })
			pin.value = ''
		} else {
			errorMessage.value = 'Invalid PIN. Please try again.'
			pin.value = ''
		}
	} catch (err) {
		errorMessage.value = 'Invalid manager PIN.'
		pin.value = ''
	} finally {
		verifying.value = false
	}
}

watch(
	() => props.show,
	async (val) => {
		if (val) {
			pin.value = ''
			errorMessage.value = ''
			await nextTick()
			pinInputRef.value?.focus()
		}
	}
)
</script>
