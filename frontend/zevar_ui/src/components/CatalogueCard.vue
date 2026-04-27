<template>
	<a
		:href="catalogue.url"
		target="_blank"
		rel="noopener noreferrer"
		class="group block bg-white dark:bg-warm-dark-900/80 backdrop-blur-sm rounded-2xl border border-gray-100 dark:border-gray-800/50 overflow-hidden transition-all hover:shadow-2xl hover:shadow-[#D4AF37]/10 hover:border-[#D4AF37]/40 hover:-translate-y-1"
	>
		<!-- Header with gradient -->
		<div
			class="h-24 sm:h-28 relative overflow-hidden bg-gradient-to-br from-[#1a1a1a] via-[#252525] to-[#1a1a1a]"
		>
			<!-- Subtle pattern -->
			<div
				class="absolute inset-0 opacity-10"
				style="
					background-image: radial-gradient(
						circle at 2px 2px,
						rgba(212, 175, 55, 0.3) 1px,
						transparent 0
					);
					background-size: 20px 20px;
				"
			></div>

			<!-- Gold accent line -->
			<div
				class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-[#D4AF37] to-transparent"
			></div>

			<!-- Logo/Initial -->
			<div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
				<div
					class="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl bg-gradient-to-br from-[#D4AF37] to-amber-600 flex items-center justify-center text-black font-bold text-lg sm:text-xl shadow-xl shadow-[#D4AF37]/30 group-hover:scale-110 transition-transform"
				>
					{{ catalogue.name.charAt(0) }}
				</div>
			</div>

			<!-- Product count badge -->
			<div
				class="absolute top-3 right-3 px-2 py-1 rounded-lg bg-white/10 backdrop-blur-sm border border-white/10 text-white text-[10px] sm:text-xs font-medium"
			>
				{{ catalogue.productCount }} items
			</div>
		</div>

		<!-- Content -->
		<div class="p-4 sm:p-5">
			<h3
				class="text-base sm:text-lg font-bold text-gray-900 dark:text-white mb-1.5 group-hover:text-[#D4AF37] transition-colors"
			>
				{{ catalogue.name }}
			</h3>
			<p
				class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-3 sm:mb-4"
			>
				{{ catalogue.description }}
			</p>

			<!-- Features -->
			<div class="flex flex-wrap gap-1.5 sm:gap-2 mb-3 sm:mb-4">
				<span
					v-for="feature in catalogue.features"
					:key="feature"
					class="px-2 py-1 rounded-lg bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-400 text-[10px] sm:text-xs border border-gray-200 dark:border-warm-border"
				>
					{{ feature }}
				</span>
			</div>

			<!-- CTA -->
			<div
				class="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-gray-800"
			>
				<span class="text-xs sm:text-sm text-gray-500 dark:text-gray-400"
					>Visit Catalog</span
				>
				<div
					class="w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-gradient-to-r from-[#D4AF37] to-amber-500 flex items-center justify-center group-hover:scale-110 transition-transform"
				>
					<svg
						class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-black"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
						></path>
					</svg>
				</div>
			</div>
		</div>
	</a>
</template>

<script setup>
defineProps({
	catalogue: {
		type: Object,
		required: true,
	},
})
</script>

<style scoped>
.line-clamp-2 {
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
}
</style>
