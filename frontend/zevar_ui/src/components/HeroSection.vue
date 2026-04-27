<template>
	<section class="relative py-12 lg:py-16 overflow-hidden">
		<!-- Subtle Background -->
		<div class="absolute inset-0">
			<div
				class="absolute inset-0 bg-gradient-to-b from-transparent via-[#D4AF37]/3 to-transparent dark:from-transparent dark:via-[#D4AF37]/5 dark:to-transparent"
			></div>
			<div
				class="absolute top-0 left-1/3 w-72 h-72 bg-amber-400/5 rounded-full blur-3xl"
			></div>
			<div
				class="absolute bottom-0 right-1/4 w-96 h-96 bg-[#D4AF37]/5 rounded-full blur-3xl"
			></div>
		</div>

		<div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
				<!-- Left: Title and Search -->
				<div class="flex-1 max-w-2xl">
					<!-- Badge -->
					<div
						class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#D4AF37]/10 border border-[#D4AF37]/20 mb-4"
					>
						<span class="w-1.5 h-1.5 bg-[#D4AF37] rounded-full animate-pulse"></span>
						<span class="text-[#D4AF37] text-xs font-medium tracking-wide uppercase"
							>Live Catalogue</span
						>
					</div>

					<!-- Title -->
					<h1
						class="text-3xl lg:text-4xl font-serif font-bold text-gray-900 dark:text-white mb-3"
					>
						Premium Jewelry
						<span
							class="bg-gradient-to-r from-[#D4AF37] to-amber-500 bg-clip-text text-transparent"
							>Collections</span
						>
					</h1>

					<p class="text-gray-600 dark:text-gray-400 text-sm mb-6 max-w-lg">
						Explore curated pieces from verified partners. Updated daily.
					</p>

					<!-- Compact Search -->
					<div class="relative max-w-md">
						<div class="relative flex items-center">
							<svg
								class="absolute left-4 w-4 h-4 text-gray-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
								></path>
							</svg>
							<input
								type="text"
								v-model="searchQuery"
								@input="$emit('search', searchQuery)"
								placeholder="Search jewelry..."
								class="w-full bg-white dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-xl text-gray-900 dark:text-white placeholder-gray-400 pl-11 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 focus:border-[#D4AF37] transition-all"
							/>
						</div>
					</div>
				</div>

				<!-- Right: Stats Cards -->
				<div class="flex gap-4 lg:gap-6">
					<div class="glass-stat-card px-6 py-4 rounded-2xl text-center min-w-[100px]">
						<p class="text-2xl font-bold text-[#D4AF37]">500K+</p>
						<p class="text-xs text-gray-500 dark:text-gray-400">Products</p>
					</div>
					<div class="glass-stat-card px-6 py-4 rounded-2xl text-center min-w-[100px]">
						<p class="text-2xl font-bold text-emerald-500">5</p>
						<p class="text-xs text-gray-500 dark:text-gray-400">Partners</p>
					</div>
					<div class="glass-stat-card px-6 py-4 rounded-2xl text-center min-w-[100px]">
						<p class="text-2xl font-bold text-blue-500">24/7</p>
						<p class="text-xs text-gray-500 dark:text-gray-400">Access</p>
					</div>
				</div>
			</div>
		</div>
	</section>
</template>

<script setup>
import { ref } from 'vue'

const searchQuery = ref('')

defineEmits(['search'])
</script>

<style scoped>
.glass-stat-card {
	background: rgba(255, 255, 255, 0.8);
	backdrop-filter: blur(10px);
	border: 1px solid rgba(0, 0, 0, 0.05);
}

.dark .glass-stat-card {
	background: rgba(255, 255, 255, 0.05);
	border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
