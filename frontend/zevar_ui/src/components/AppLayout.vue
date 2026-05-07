<template>
	<!--
		AppLayout now delegates to AppShell for responsive behavior.
		All existing pages that import AppLayout will automatically get
		the mobile bottom nav, responsive sidebar, and bottom-sheet modals.
	-->
	<AppShell v-bind="$attrs">
		<slot></slot>
	</AppShell>
</template>

<script setup>
import AppShell from '@/components/AppShell.vue'
</script>
