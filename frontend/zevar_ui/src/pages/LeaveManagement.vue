<template>
	<PortalLayout>
		<div class="px-10 pb-10 flex flex-col items-center font-portal">
			<div class="w-full max-w-6xl premium-card mt-4">
				<!-- Welcome Section -->
				<div
					class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-8"
				>
					<div>
						<h1 class="premium-title !text-4xl md:!text-5xl mb-2">
							Where to next, Alex?
						</h1>
						<p class="premium-subtitle text-lg">
							You've got 14 days of fun waiting for you.
						</p>
					</div>
					<button
						class="neon-glow flex items-center gap-3 bg-gradient-to-r from-[#7f13ec] to-[#a855f7] hover:scale-105 transition-transform px-8 py-4 rounded-full font-bold text-lg"
					>
						<span class="material-symbols-outlined">add_circle</span>
						Request Time Off
					</button>
				</div>

				<div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
					<!-- Calendar Section -->
					<div class="lg:col-span-7">
						<div class="flex items-center justify-between mb-8 px-4">
							<h3 class="premium-title !text-xl">February 2024</h3>
							<div class="flex gap-4">
								<button
									class="p-2 rounded-full hover:bg-white/5 transition-colors"
								>
									<span class="material-symbols-outlined text-white/60"
										>chevron_left</span
									>
								</button>
								<button
									class="p-2 rounded-full hover:bg-white/5 transition-colors"
								>
									<span class="material-symbols-outlined text-white/60"
										>chevron_right</span
									>
								</button>
							</div>
						</div>

						<!-- Calendar Grid -->
						<div
							class="grid grid-cols-7 gap-2 text-center text-[10px] font-black tracking-widest text-white/30 mb-4 uppercase"
						>
							<div>Sun</div>
							<div>Mon</div>
							<div>Tue</div>
							<div>Wed</div>
							<div>Thu</div>
							<div>Fri</div>
							<div>Sat</div>
						</div>
						<div class="grid grid-cols-7 gap-y-2">
							<div
								v-for="d in 28"
								:key="d"
								class="flex justify-center items-center h-8"
							>
								<div
									class="w-8 h-8 flex items-center justify-center rounded-full transition-all cursor-pointer font-bold"
									:class="{
										'bg-[#7f13ec] text-white neon-glow': d === 18,
										'bg-white/5 text-white/40 hover:bg-white/10 hover:text-white':
											d !== 18,
									}"
								>
									{{ d }}
								</div>
							</div>
						</div>
					</div>

					<!-- Side Panels -->
					<div class="lg:col-span-5 flex flex-col gap-8">
						<!-- Stats -->
						<div class="grid grid-cols-2 gap-4">
							<div
								class="premium-card !p-6 border border-gray-100 dark:border-warm-border hover:border-portal-primary/30 transition-colors"
							>
								<span class="status-label !mb-2">Vacation Left</span>
								<div class="flex items-end gap-1">
									<span class="text-3xl font-800 text-gray-900 dark:text-white"
										>12</span
									>
									<span class="text-gray-400 dark:text-white/40 text-sm mb-1"
										>days</span
									>
								</div>
							</div>
							<div
								class="premium-card !p-6 border border-gray-100 dark:border-warm-border hover:border-portal-accent-peach/30 transition-colors"
							>
								<span class="status-label !mb-2">Sick Leave</span>
								<div class="flex items-end gap-1">
									<span class="text-3xl font-800 text-gray-900 dark:text-white"
										>05</span
									>
									<span class="text-gray-400 dark:text-white/40 text-sm mb-1"
										>days</span
									>
								</div>
							</div>
						</div>

						<!-- Mood Tracker -->
						<div class="bg-white/5 rounded-xl p-6 border border-white/10">
							<h4
								class="text-[10px] font-bold text-white/40 uppercase tracking-widest mb-6"
							>
								Current Vibe
							</h4>
							<div class="flex justify-between items-center gap-2">
								<button
									class="flex flex-col items-center gap-2 group cursor-pointer"
								>
									<div
										class="w-10 h-10 rounded-full bg-red-500/10 flex items-center justify-center group-hover:scale-110 transition-transform"
									>
										<span
											class="material-symbols-outlined text-red-500 text-xl"
											>mood_bad</span
										>
									</div>
								</button>
								<button
									class="flex flex-col items-center gap-2 group cursor-pointer"
								>
									<div
										class="w-10 h-10 rounded-full bg-[#7f13ec]/20 flex items-center justify-center scale-125 transition-transform border border-[#7f13ec]/50"
									>
										<span
											class="material-symbols-outlined text-[#7f13ec] text-xl"
											>sentiment_satisfied</span
										>
									</div>
								</button>
								<button
									class="flex flex-col items-center gap-2 group cursor-pointer"
								>
									<div
										class="w-10 h-10 rounded-full bg-green-500/10 flex items-center justify-center group-hover:scale-110 transition-transform"
									>
										<span
											class="material-symbols-outlined text-green-500 text-xl"
											>sentiment_very_satisfied</span
										>
									</div>
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</PortalLayout>
</template>

<script setup>
import PortalLayout from '@/components/PortalLayout.vue'
</script>
