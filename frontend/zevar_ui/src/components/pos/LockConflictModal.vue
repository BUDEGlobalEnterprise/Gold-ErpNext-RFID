<template>
  <transition name="modal-fade">
    <div v-if="visible" class="modal-overlay" @click.self="$emit('cancel')">
      <div class="modal-card">
        <div class="modal-icon">🔒</div>
        <h3 class="modal-title">Resource Locked</h3>
        <p class="modal-desc">
          This item is currently being modified by another user.
        </p>

        <div class="lock-details">
          <div class="detail-row">
            <span class="detail-label">Locked by</span>
            <span class="detail-value">{{ lockedBy }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Session</span>
            <span class="detail-value session-id">{{ sessionId }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Expires in</span>
            <span class="detail-value countdown" :class="{ urgent: remainingSeconds <= 10 }">
              {{ remainingFormatted }}
            </span>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-retry" @click="$emit('retry')" :disabled="retrying">
            <span v-if="retrying" class="spinner"></span>
            {{ retrying ? 'Retrying...' : '🔄 Retry' }}
          </button>
          <button class="btn-cancel" @click="$emit('cancel')">Cancel</button>
          <button
            v-if="canOverride"
            class="btn-override"
            @click="$emit('override')"
          >
            ⚡ Override (Manager)
          </button>
        </div>

        <p v-if="retryCount > 0" class="retry-info">
          Attempt {{ retryCount }}/3
        </p>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  lockedBy: { type: String, default: 'Unknown User' },
  sessionId: { type: String, default: '' },
  expiresAt: { type: String, default: '' },
  canOverride: { type: Boolean, default: false },
  retrying: { type: Boolean, default: false },
  retryCount: { type: Number, default: 0 }
})

defineEmits(['retry', 'cancel', 'override'])

const remainingSeconds = ref(0)
let timer = null

const remainingFormatted = computed(() => {
  const s = remainingSeconds.value
  if (s <= 0) return 'Expired'
  const m = Math.floor(s / 60)
  const sec = s % 60
  return m > 0 ? `${m}m ${sec}s` : `${sec}s`
})

function updateCountdown() {
  if (!props.expiresAt) { remainingSeconds.value = 0; return }
  const diff = Math.max(0, Math.floor((new Date(props.expiresAt) - Date.now()) / 1000))
  remainingSeconds.value = diff
}

watch(() => props.visible, (v) => {
  if (v) {
    updateCountdown()
    timer = setInterval(updateCountdown, 1000)
  } else {
    clearInterval(timer)
  }
}, { immediate: true })

onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1100; display: flex; align-items: center; justify-content: center; }
.modal-card { background: white; border-radius: 12px; padding: 32px; width: 400px; max-width: 90vw; text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.15); }
.modal-icon { font-size: 40px; margin-bottom: 12px; }
.modal-title { font-size: 18px; font-weight: 700; margin: 0 0 8px; }
.modal-desc { font-size: 13px; color: #64748b; margin: 0 0 20px; }
.lock-details { background: #f8fafc; border-radius: 8px; padding: 12px; margin-bottom: 20px; }
.detail-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f1f5f9; }
.detail-row:last-child { border-bottom: none; }
.detail-label { font-size: 12px; color: #94a3b8; }
.detail-value { font-size: 12px; font-weight: 600; }
.session-id { font-family: monospace; color: #6366f1; }
.countdown { color: #f59e0b; }
.countdown.urgent { color: #dc2626; animation: pulse 1s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.modal-actions { display: flex; gap: 8px; justify-content: center; margin-bottom: 12px; }
.btn-retry { padding: 8px 16px; border: 1px solid #3b82f6; border-radius: 6px; background: #3b82f6; color: white; cursor: pointer; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px; }
.btn-retry:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-cancel { padding: 8px 16px; border: 1px solid #e2e8f0; border-radius: 6px; background: white; cursor: pointer; font-size: 13px; }
.btn-override { padding: 8px 16px; border: 1px solid #f59e0b; border-radius: 6px; background: #fffbeb; color: #92400e; cursor: pointer; font-size: 13px; font-weight: 600; }
.btn-override:hover { background: #fef3c7; }
.retry-info { font-size: 11px; color: #94a3b8; margin: 0; }
.spinner { width: 12px; height: 12px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.6s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.2s; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
</style>
