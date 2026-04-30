<template>
	<AppLayout>
		<CategoryListing :isEmbedded="true" />
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import CategoryListing from '@/pages/CategoryListing.vue'
</script>
