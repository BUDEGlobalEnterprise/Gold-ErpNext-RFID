<template>
  <a v-if="certNumber && lab" class="cert-link-badge" :class="labClass" :href="certUrl" target="_blank" @click.stop>
    <span class="lab-name">{{ lab }}</span>
    <span class="cert-num">#{{ certNumber }}</span>
    <svg class="external-icon" width="10" height="10" viewBox="0 0 12 12"><path d="M3 1h8v8M11 1L1 11" stroke="currentColor" stroke-width="1.5" fill="none"/></svg>
  </a>
  <span v-else-if="lab" class="cert-link-badge uncertified">
    {{ lab }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  lab: { type: String, default: '' },
  certNumber: { type: String, default: '' }
})

const labClass = computed(() => {
  const map = { GIA: 'lab-gia', IGI: 'lab-igi', HRD: 'lab-hrd', AGS: 'lab-ags' }
  return map[props.lab] || 'lab-other'
})

const certUrl = computed(() => {
  if (props.lab === 'GIA') return `https://www.gia.edu/report-check?reportno=${props.certNumber}`
  if (props.lab === 'IGI') return `https://www.igi.org/verify-your-report?r=${props.certNumber}`
  return '#'
})
</script>

<style scoped>
.cert-link-badge { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; text-decoration: none; transition: all 0.15s; cursor: pointer; }
.cert-link-badge:hover { filter: brightness(0.95); transform: translateY(-1px); }
.lab-gia { background: #dbeafe; color: #1e40af; }
.lab-igi { background: #fef3c7; color: #92400e; }
.lab-hrd { background: #e0e7ff; color: #3730a3; }
.lab-ags { background: #dcfce7; color: #166534; }
.lab-other { background: #f1f5f9; color: #475569; }
.uncertified { background: #fef2f2; color: #991b1b; }
.cert-num { opacity: 0.8; }
.external-icon { opacity: 0.5; }
</style>
