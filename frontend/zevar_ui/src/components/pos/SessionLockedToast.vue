<template>
  <transition name="toast-slide">
    <div v-if="visible" class="session-toast" :class="toastClass">
      <div class="toast-icon">{{ icon }}</div>
      <div class="toast-body">
        <p class="toast-title">{{ title }}</p>
        <p class="toast-message">{{ message }}</p>
        <p v-if="sessionId" class="toast-session">Session: <code>{{ sessionId }}</code></p>
      </div>
      <div class="toast-actions">
        <button v-if="canOverride" class="btn-override" @click="$emit('override')">
          Override
        </button>
        <button class="btn-dismiss" @click="$emit('dismiss')">&times;</button>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed, watch, onUnmounted } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  type: { type: String, default: 'warning' }, // warning | error | info
  title: { type: String, default: 'Session Locked' },
  message: { type: String, default: '' },
  sessionId: { type: String, default: '' },
  canOverride: { type: Boolean, default: false },
  autoDismissMs: { type: Number, default: 8000 }
})

const emit = defineEmits(['dismiss', 'override'])

const icon = computed(() => {
  const map = { warning: '⚠️', error: '🚫', info: 'ℹ️' }
  return map[props.type] || '⚠️'
})

const toastClass = computed(() => `toast-${props.type}`)

let dismissTimer = null

watch(() => props.visible, (v) => {
  clearTimeout(dismissTimer)
  if (v && props.autoDismissMs > 0) {
    dismissTimer = setTimeout(() => emit('dismiss'), props.autoDismissMs)
  }
})

onUnmounted(() => clearTimeout(dismissTimer))
</script>

<style scoped>
.session-toast { position: fixed; bottom: 24px; right: 24px; z-index: 1200; display: flex; align-items: flex-start; gap: 12px; padding: 14px 18px; border-radius: 10px; max-width: 420px; box-shadow: 0 8px 32px rgba(0,0,0,0.15); animation: toast-enter 0.3s ease; }
.toast-warning { background: #fffbeb; border: 1px solid #fbbf24; }
.toast-error { background: #fef2f2; border: 1px solid #ef4444; }
.toast-info { background: #eff6ff; border: 1px solid #3b82f6; }
.toast-icon { font-size: 20px; flex-shrink: 0; }
.toast-body { flex: 1; }
.toast-title { font-size: 13px; font-weight: 700; margin: 0 0 4px; }
.toast-message { font-size: 12px; color: #475569; margin: 0 0 4px; }
.toast-session { font-size: 11px; color: #94a3b8; margin: 0; }
.toast-session code { background: rgba(0,0,0,0.05); padding: 1px 4px; border-radius: 3px; font-size: 10px; }
.toast-actions { display: flex; flex-direction: column; gap: 4px; flex-shrink: 0; }
.btn-override { padding: 4px 10px; border: 1px solid #f59e0b; border-radius: 4px; background: #fef3c7; color: #92400e; cursor: pointer; font-size: 11px; font-weight: 600; }
.btn-override:hover { background: #fde68a; }
.btn-dismiss { background: none; border: none; font-size: 18px; cursor: pointer; color: #94a3b8; }
.btn-dismiss:hover { color: #475569; }
.toast-slide-enter-active { transition: all 0.3s ease; }
.toast-slide-leave-active { transition: all 0.2s ease; }
.toast-slide-enter-from { transform: translateX(100%); opacity: 0; }
.toast-slide-leave-to { transform: translateY(20px); opacity: 0; }
</style>
