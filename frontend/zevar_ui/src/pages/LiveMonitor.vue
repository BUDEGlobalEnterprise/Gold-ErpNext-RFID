<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center gap-3 mb-4 flex-shrink-0 flex-wrap">
				<div class="w-10 h-10 rounded-xl flex items-center justify-center bg-red-500/10">
					<span class="material-symbols-outlined !text-xl text-red-500">monitor_heart</span>
				</div>
				<div>
					<h2 class="premium-title !text-xl">Live Monitor</h2>
					<p class="text-[10px] text-gray-400">Real-time store activity</p>
				</div>
			</div>
			<div class="flex-1 flex items-center justify-center">
				<div class="text-center">
					<span class="material-symbols-outlined !text-4xl text-gray-300 mb-2 block">construction</span>
					<p class="text-sm text-gray-400">Use the Command Center or Admin Monitor for live data</p>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
</script>
