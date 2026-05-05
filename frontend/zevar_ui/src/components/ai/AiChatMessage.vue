<template>
  <div class="ai-msg" :class="[`ai-msg--${message.role}`, { 'ai-msg--error': message.isError }]">
    <!-- User message -->
    <div v-if="message.role === 'user'" class="ai-msg__bubble ai-msg__bubble--user">
      {{ message.content }}
    </div>

    <!-- Assistant message -->
    <div v-else class="ai-msg__assistant">
      <div class="ai-msg__bubble ai-msg__bubble--assistant">
        <div class="ai-msg__text" v-html="formattedContent"></div>
      </div>

      <!-- Sources -->
      <div v-if="message.sources?.length" class="ai-msg__sources">
        <button class="ai-sources-toggle" @click="showSources = !showSources">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
            <polyline points="13 2 13 9 20 9"/>
          </svg>
          {{ message.sources.length }} source{{ message.sources.length > 1 ? 's' : '' }}
          <svg
            width="12" height="12" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" stroke-width="2"
            :class="{ 'ai-rotate': showSources }"
          >
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </button>
        <div v-if="showSources" class="ai-sources-list">
          <div v-for="(src, i) in message.sources" :key="i" class="ai-source-item">
            <span class="ai-source-type">{{ src.type }}</span>
            <span class="ai-source-label">{{ src.label }}</span>
            <span class="ai-source-score">{{ (src.similarity * 100).toFixed(0) }}%</span>
          </div>
        </div>
      </div>

      <!-- Recommendations -->
      <div v-if="message.recommendations?.length" class="ai-msg__recs">
        <div
          v-for="rec in message.recommendations"
          :key="rec.item_code"
          class="ai-rec-card"
        >
          <div class="ai-rec-image">
            <img v-if="rec.image" :src="rec.image" :alt="rec.item_name" />
            <div v-else class="ai-rec-placeholder">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
              </svg>
            </div>
          </div>
          <div class="ai-rec-info">
            <div class="ai-rec-name">{{ rec.item_name }}</div>
            <div class="ai-rec-tags">
              <span v-if="rec.metal" class="ai-rec-tag">{{ rec.metal }}</span>
              <span v-if="rec.purity" class="ai-rec-tag">{{ rec.purity }}</span>
            </div>
            <div class="ai-rec-footer">
              <span v-if="rec.msrp" class="ai-rec-price">${{ rec.msrp.toLocaleString() }}</span>
              <span class="ai-rec-reason">{{ rec.reasoning }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Meta info -->
      <div v-if="message.provider || message.latencyMs" class="ai-msg__meta">
        <span v-if="message.provider" class="ai-meta-tag">{{ message.provider }}</span>
        <span v-if="message.latencyMs" class="ai-meta-tag">{{ message.latencyMs }}ms</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  message: {
    type: Object,
    required: true,
  },
})

const showSources = ref(false)

const formattedContent = computed(() => {
  const content = props.message.content || ''
  // Basic markdown: bold, italic, line breaks
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
})
</script>

<style scoped>
.ai-msg {
  display: flex;
  flex-direction: column;
}

.ai-msg--user {
  align-items: flex-end;
}

.ai-msg--assistant {
  align-items: flex-start;
}

.ai-msg__assistant {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: 100%;
}

.ai-msg__bubble {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
}

.ai-msg__bubble--user {
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  color: white;
  border-bottom-right-radius: 4px;
}

.ai-msg__bubble--assistant {
  background: #f3f4f6;
  color: #1f2937;
  border-bottom-left-radius: 4px;
}

.dark .ai-msg__bubble--assistant {
  background: #374151;
  color: #f3f4f6;
}

.ai-msg--error .ai-msg__bubble--assistant {
  background: #fef2f2;
  color: #991b1b;
}

.ai-msg__text :deep(strong) {
  font-weight: 600;
}

.ai-msg__text :deep(br) {
  display: block;
  margin: 4px 0;
}

.ai-msg__sources {
  margin-left: 4px;
}

.ai-sources-toggle {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  font-size: 11px;
  color: #6b7280;
  background: none;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}

.dark .ai-sources-toggle {
  color: #9ca3af;
  border-color: #4b5563;
}

.ai-sources-toggle:hover {
  background: #f3f4f6;
}

.dark .ai-sources-toggle:hover {
  background: #374151;
}

.ai-rotate {
  transform: rotate(180deg);
}

.ai-sources-list {
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.ai-source-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  font-size: 12px;
  background: #f9fafb;
  border-radius: 6px;
}

.dark .ai-source-item {
  background: #1f2937;
}

.ai-source-type {
  padding: 1px 6px;
  border-radius: 4px;
  background: #e0e7ff;
  color: #4338ca;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
}

.dark .ai-source-type {
  background: #312e81;
  color: #a5b4fc;
}

.ai-source-label {
  flex: 1;
  color: #4b5563;
}

.dark .ai-source-label {
  color: #d1d5db;
}

.ai-source-score {
  font-size: 10px;
  color: #9ca3af;
  font-variant-numeric: tabular-nums;
}

.ai-msg__meta {
  display: flex;
  gap: 6px;
  margin-left: 4px;
}

.ai-meta-tag {
  font-size: 10px;
  color: #9ca3af;
  padding: 1px 6px;
  border-radius: 4px;
  background: #f3f4f6;
}

.dark .ai-meta-tag {
  background: #1f2937;
  color: #6b7280;
}

/* Recommendation cards */
.ai-msg__recs {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-left: 4px;
}

.ai-rec-card {
  display: flex;
  gap: 10px;
  padding: 8px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  background: #fafafa;
  transition: border-color 0.15s;
}

.dark .ai-rec-card {
  border-color: #374151;
  background: #1f2937;
}

.ai-rec-card:hover {
  border-color: #8b5cf6;
}

.ai-rec-image {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.ai-rec-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ai-rec-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  color: #9ca3af;
}

.dark .ai-rec-placeholder {
  background: #374151;
}

.ai-rec-info {
  flex: 1;
  min-width: 0;
}

.ai-rec-name {
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ai-rec-tags {
  display: flex;
  gap: 4px;
  margin: 3px 0;
}

.ai-rec-tag {
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 4px;
  background: #e0e7ff;
  color: #4338ca;
}

.dark .ai-rec-tag {
  background: #312e81;
  color: #a5b4fc;
}

.ai-rec-footer {
  display: flex;
  align-items: center;
  gap: 6px;
}

.ai-rec-price {
  font-size: 12px;
  font-weight: 600;
  color: #059669;
}

.ai-rec-reason {
  font-size: 10px;
  color: #9ca3af;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
