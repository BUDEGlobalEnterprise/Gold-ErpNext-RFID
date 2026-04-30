<template>
	<BaseModal :show="show" max-width="max-w-lg" @close="close">
		<template #header>
			<h2 class="text-lg font-bold text-gray-900 dark:text-white">Profile Settings</h2>
		</template>

		<div class="p-6">
			<!-- User Info -->
			<div
				class="flex items-center gap-4 p-4 bg-gray-50 dark:bg-warm-dark-700 rounded-xl mb-6"
			>
				<div
					class="w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg"
				>
					{{ userInitials }}
				</div>
				<div>
					<h3 class="text-sm font-semibold text-gray-900 dark:text-white">
						{{ user?.full_name || user?.email || 'User' }}
					</h3>
					<p class="text-xs text-gray-500 dark:text-gray-400">{{ user?.email }}</p>
				</div>
			</div>

			<!-- Settings Sections -->
			<div class="space-y-6">
				<div>
					<h4
						class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
					>
						Display Settings
					</h4>

					<div class="space-y-3">
						<div
							class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
						>
							<div class="flex-1">
								<span
									class="block text-sm font-medium text-gray-900 dark:text-white"
									>Dark Mode</span
								>
								<span class="block text-xs text-gray-500 dark:text-gray-400 mt-0.5"
									>Use dark theme throughout the app</span
								>
							</div>
							<label class="relative inline-flex items-center cursor-pointer">
								<input
									type="checkbox"
									v-model="settings.dark_mode"
									@change="saveSettings"
									class="sr-only peer"
								/>
								<div
									class="w-11 h-6 bg-gray-200 dark:bg-warm-dark-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
								></div>
							</label>
						</div>

						<div
							class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
						>
							<div class="flex-1">
								<span
									class="block text-sm font-medium text-gray-900 dark:text-white"
									>Compact View</span
								>
								<span class="block text-xs text-gray-500 dark:text-gray-400 mt-0.5"
									>Reduce spacing in lists and cards</span
								>
							</div>
							<label class="relative inline-flex items-center cursor-pointer">
								<input
									type="checkbox"
									v-model="settings.compact_view"
									@change="saveSettings"
									class="sr-only peer"
								/>
								<div
									class="w-11 h-6 bg-gray-200 dark:bg-warm-dark-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
								></div>
							</label>
						</div>

						<div
							class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
						>
							<div class="flex-1">
								<span
									class="block text-sm font-medium text-gray-900 dark:text-white"
									>Currency Display</span
								>
								<span class="block text-xs text-gray-500 dark:text-gray-400 mt-0.5"
									>How to show prices</span
								>
							</div>
							<select
								v-model="settings.currency_display"
								@change="saveSettings"
								class="px-3 py-1.5 bg-gray-100 dark:bg-white/10 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white min-w-[120px]"
							>
								<option value="symbol">$ Symbol</option>
								<option value="code">USD Code</option>
								<option value="name">US Dollar</option>
							</select>
						</div>
					</div>
				</div>

				<div>
					<h4
						class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
					>
						Notification Settings
					</h4>

					<div class="space-y-3">
						<div
							class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
						>
							<div class="flex-1">
								<span
									class="block text-sm font-medium text-gray-900 dark:text-white"
									>Sound Alerts</span
								>
								<span class="block text-xs text-gray-500 dark:text-gray-400 mt-0.5"
									>Play sound on order completion</span
								>
							</div>
							<label class="relative inline-flex items-center cursor-pointer">
								<input
									type="checkbox"
									v-model="settings.sound_alerts"
									@change="saveSettings"
									class="sr-only peer"
								/>
								<div
									class="w-11 h-6 bg-gray-200 dark:bg-warm-dark-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
								></div>
							</label>
						</div>

						<div
							class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
						>
							<div class="flex-1">
								<span
									class="block text-sm font-medium text-gray-900 dark:text-white"
									>Low Stock Alerts</span
								>
								<span class="block text-xs text-gray-500 dark:text-gray-400 mt-0.5"
									>Alert when items are low in stock</span
								>
							</div>
							<label class="relative inline-flex items-center cursor-pointer">
								<input
									type="checkbox"
									v-model="settings.low_stock_alerts"
									@change="saveSettings"
									class="sr-only peer"
								/>
								<div
									class="w-11 h-6 bg-gray-200 dark:bg-warm-dark-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
								></div>
							</label>
						</div>
					</div>
				</div>

				<div>
					<h4
						class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
					>
						Language & Region
					</h4>

					<div class="space-y-3">
						<div
							class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
						>
							<div class="flex-1">
								<span
									class="block text-sm font-medium text-gray-900 dark:text-white"
									>Language</span
								>
							</div>
							<select
								v-model="settings.language"
								@change="saveSettings"
								class="px-3 py-1.5 bg-gray-100 dark:bg-white/10 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white min-w-[120px]"
							>
								<option value="en">English</option>
								<option value="es">Spanish</option>
								<option value="ar">Arabic</option>
							</select>
						</div>

						<div
							class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
						>
							<div class="flex-1">
								<span
									class="block text-sm font-medium text-gray-900 dark:text-white"
									>Timezone</span
								>
							</div>
							<select
								v-model="settings.timezone"
								@change="saveSettings"
								class="px-3 py-1.5 bg-gray-100 dark:bg-white/10 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white min-w-[120px]"
							>
								<option value="America/New_York">Eastern Time</option>
								<option value="America/Chicago">Central Time</option>
								<option value="America/Denver">Mountain Time</option>
								<option value="America/Los_Angeles">Pacific Time</option>
							</select>
						</div>
					</div>
				</div>
			</div>
		</div>

		<template #footer>
			<button
				class="px-4 py-2 text-sm font-semibold text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-warm-border rounded-lg hover:bg-gray-50 dark:hover:bg-white/10 transition"
				@click="resetSettings"
			>
				Reset to Defaults
			</button>
			<button
				class="px-4 py-2 text-sm font-semibold bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
				@click="close"
			>
				Done
			</button>
		</template>
	</BaseModal>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import BaseModal from './BaseModal.vue'

const props = defineProps({
	show: { type: Boolean, default: false },
	user: { type: Object, default: null },
})

const emit = defineEmits(['close'])

const defaultSettings = {
	dark_mode: true,
	compact_view: false,
	currency_display: 'symbol',
	sound_alerts: true,
	low_stock_alerts: true,
	language: 'en',
	timezone: 'America/New_York',
}

const settings = ref({ ...defaultSettings })

const userInitials = computed(() => {
	const name = props.user?.full_name || props.user?.email || 'U'
	return name
		.split(' ')
		.map((n) => n[0])
		.join('')
		.toUpperCase()
		.slice(0, 2)
})

function saveSettings() {
	localStorage.setItem('pos_settings', JSON.stringify(settings.value))
}

function loadSettings() {
	const stored = localStorage.getItem('pos_settings')
	if (stored) {
		try {
			settings.value = { ...defaultSettings, ...JSON.parse(stored) }
		} catch {
			settings.value = { ...defaultSettings }
		}
	}
}

function resetSettings() {
	settings.value = { ...defaultSettings }
	saveSettings()
}

function close() {
	emit('close')
}

watch(
	() => props.show,
	(val) => {
		if (val) loadSettings()
	}
)

onMounted(loadSettings)
</script>
