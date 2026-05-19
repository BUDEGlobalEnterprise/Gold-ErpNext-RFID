<template>
	<router-view />
	<ToastNotification ref="toast" />
</template>

<script setup>
import { provide, ref } from 'vue'
import ToastNotification from '@/components/ToastNotification.vue'

const toast = ref(null)
provide('toast', toast)
</script>
