<template>
  <div class="ai-search">
    <div class="ai-search__input-wrap">
      <svg class="ai-search__icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input
        v-model="query"
        class="ai-search__input"
        placeholder="Search with AI... (e.g., gold necklace under $500)"
        @keydown.enter="doSearch"
        @input="debouncedSearch"
      />
      <button
        v-if="query"
        class="ai-search__clear"
        @click="clearSearch"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
      <button
        class="ai-search__btn"
        :disabled="!query.trim()"
        @click="doSearch"
      >
        Search
      </button>
    </div>

    <!-- Results dropdown -->
    <div v-if="results.length > 0" class="ai-search__results">
      <div class="ai-search__results-header">
        <span>AI Results</span>
        <span class="ai-search__results-count">{{ results.length }} found</span>
      </div>
      <div
        v-for="item in results"
        :key="item.item_code"
        class="ai-search__result-item"
        @click="$emit('select', item)"
      >
        <div class="ai-search__result-image">
          <img v-if="item.image" :src="item.image" alt="" />
          <div v-else class="ai-search__result-placeholder">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
            </svg>
          </div>
        </div>
        <div class="ai-search__result-info">
          <div class="ai-search__result-name">{{ item.item_name }}</div>
          <div class="ai-search__result-details">
            <span v-if="item.metal">{{ item.metal }}</span>
            <span v-if="item.purity">{{ item.purity }}</span>
            <span v-if="item.msrp">${{ item.msrp.toLocaleString() }}</span>
          </div>
        </div>
        <div class="ai-search__result-match">
          {{ (item.similarity * 100).toFixed(0) }}%
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAiStore } from '@/stores/ai.js'

const emit = defineEmits(['select'])

const store = useAiStore()
const query = ref('')
const results = ref([])
let debounceTimer = null

function doSearch() {
  if (!query.value.trim()) return
  store.searchProducts(query.value)
  // Watch for results
  const unwatch = store.$subscribe((mutation, state) => {
    results.value = state.searchResults
    unwatch()
  })
}

function debouncedSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    if (query.value.trim().length >= 3) {
      doSearch()
    }
  }, 500)
}

function clearSearch() {
  query.value = ''
  results.value = []
}
</script>

<style scoped>
.ai-search {
  position: relative;
  width: 100%;
}

.ai-search__input-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  transition: border-color 0.15s;
}

.dark .ai-search__input-wrap {
  background: #1f2937;
  border-color: #4b5563;
}

.ai-search__input-wrap:focus-within {
  border-color: #6366f1;
}

.ai-search__icon {
  color: #9ca3af;
  flex-shrink: 0;
}

.ai-search__input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  background: transparent;
}

.ai-search__clear {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 2px;
  display: flex;
}

.ai-search__clear:hover {
  color: #6b7280;
}

.ai-search__btn {
  padding: 6px 16px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  color: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s;
}

.ai-search__btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.ai-search__btn:not(:disabled):hover {
  opacity: 0.9;
}

.ai-search__results {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  z-index: 50;
  max-height: 400px;
  overflow-y: auto;
}

.dark .ai-search__results {
  background: #1f2937;
  border-color: #4b5563;
}

.ai-search__results-header {
  display: flex;
  justify-content: space-between;
  padding: 10px 14px;
  font-size: 12px;
  color: #6b7280;
  border-bottom: 1px solid #e5e7eb;
}

.dark .ai-search__results-header {
  border-color: #4b5563;
  color: #9ca3af;
}

.ai-search__results-count {
  font-variant-numeric: tabular-nums;
}

.ai-search__result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.1s;
}

.ai-search__result-item:hover {
  background: #f3f4f6;
}

.dark .ai-search__result-item:hover {
  background: #374151;
}

.ai-search__result-image {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.ai-search__result-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ai-search__result-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  color: #9ca3af;
}

.dark .ai-search__result-placeholder {
  background: #374151;
}

.ai-search__result-info {
  flex: 1;
  min-width: 0;
}

.ai-search__result-name {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ai-search__result-details {
  display: flex;
  gap: 6px;
  font-size: 12px;
  color: #6b7280;
}

.ai-search__result-match {
  font-size: 12px;
  color: #6366f1;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
</style>
