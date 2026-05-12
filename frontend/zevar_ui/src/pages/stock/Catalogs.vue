<template>
	<AppLayout>
		<div class="flex flex-col items-center justify-center h-full py-20">
			<div class="premium-card !p-8 text-center max-w-md">
				<svg
					class="w-16 h-16 mx-auto mb-4 text-[#D4AF37]"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="1"
						d="M4 19.5A2.5 2.5 0 016.5 17H20"
					/>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="1"
						d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"
					/>
				</svg>
				<h2 class="premium-title !text-xl mb-2">Catalogs</h2>
				<p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
					Manage your product catalogs and collections
				</p>
				<router-link
					to="/catalogues"
					class="inline-flex items-center gap-2 px-4 py-2 bg-[#D4AF37] text-white rounded-lg text-sm font-bold hover:bg-[#C4A030] transition"
				>
					Open Catalog Manager
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M13 7l5 5m0 0l-5 5m5-5H6"
						/>
					</svg>
				</router-link>
			</div>
		</div>
	</AppLayout>
</template>
<script setup>
import AppLayout from '@/components/AppLayout.vue'
</script>
