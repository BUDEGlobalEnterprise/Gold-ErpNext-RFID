<template>
	<AppLayout>
		<CatalogueView :isEmbedded="true" />
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import CatalogueView from '@/components/CatalogueView.vue'
</script>
