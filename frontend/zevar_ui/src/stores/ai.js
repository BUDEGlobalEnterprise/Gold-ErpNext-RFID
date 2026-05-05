/**
 * AI Assistant Pinia Store
 *
 * Manages state for the AI assistant: chat messages, loading state,
 * and API interaction.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'
import { AiHistoryService } from '@/services/AiHistoryService.js'

export const useAiStore = defineStore('ai', () => {
  // State
  const isOpen = ref(false)
  const history = ref(AiHistoryService.loadHistory())
  const currentChatId = ref(history.value[0]?.id || Date.now().toString())
  const messages = ref(history.value[0]?.messages || [])
  const isLoading = ref(false)
  const error = ref(null)
  const searchResults = ref([])
  const isSearching = ref(false)

  // Computed
  const hasMessages = computed(() => messages.value.length > 0)
  const lastMessage = computed(() =>
    messages.value.length > 0 ? messages.value[messages.value.length - 1] : null
  )

  // Resources
  const askResource = createResource({
    url: 'zevar_core.rag.api.assistant.ask',
    method: 'POST',
    onSuccess(data) {
      isLoading.value = false
      if (data) {
        messages.value.push({
          role: 'assistant',
          content: data.answer || 'No answer generated.',
          sources: data.sources || [],
          queryId: data.query_id,
          domain: data.domain,
          confidence: data.confidence,
          provider: data.provider,
          latencyMs: data.latency_ms,
          timestamp: new Date(),
        })
        saveToHistory()
      }
    },
    onError(err) {
      isLoading.value = false
      error.value = err?.message || 'Failed to get a response.'
      messages.value.push({
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        sources: [],
        isError: true,
        timestamp: new Date(),
      })
    },
  })

  const searchResource = createResource({
    url: 'zevar_core.rag.api.assistant.search_products',
    method: 'POST',
    onSuccess(data) {
      isSearching.value = false
      searchResults.value = data?.results || []
    },
    onError() {
      isSearching.value = false
      searchResults.value = []
    },
  })

  const recommendResource = createResource({
    url: 'zevar_core.rag.api.assistant.get_recommendations',
    onSuccess(data) {
      isLoading.value = false
      if (data) {
        const recs = data.recommendations || []
        const profile = data.profile_summary || {}
        const lines = [`Recommendations for ${data.customer_name || data.customer}:`]
        if (data.occasion) lines.push(`Occasion: ${data.occasion}`)
        lines.push('')
        if (recs.length === 0) {
          lines.push('No matching products found. Try rebuilding the search index.')
        } else {
          recs.forEach((r, i) => {
            lines.push(`${i + 1}. ${r.item_name} - $${(r.msrp || 0).toLocaleString()}`)
            if (r.metal) lines.push(`   ${r.metal} ${r.purity || ''}`)
            if (r.reasoning) lines.push(`   ${r.reasoning}`)
          })
        }
        if (profile.preferences) {
          const prefs = Object.entries(profile.preferences)
          if (prefs.length) lines.push(`\nBased on: ${prefs.map(([, v]) => v).join(', ')}`)
        }
        messages.value.push({
          role: 'assistant',
          content: lines.join('\n'),
          sources: [],
          recommendations: recs,
          domain: 'customer',
          provider: 'recommender',
          latencyMs: data.latency_ms,
          timestamp: new Date(),
        })
        saveToHistory()
      }
    },
    onError(err) {
      isLoading.value = false
      messages.value.push({
        role: 'assistant',
        content: 'Could not load recommendations. ' + (err?.message || ''),
        sources: [],
        isError: true,
        timestamp: new Date(),
      })
    },
  })

  // Actions
  function saveToHistory() {
    const updatedHistory = AiHistoryService.archiveChat(currentChatId.value, messages.value)
    if (updatedHistory) {
      history.value = updatedHistory
    }
  }

  function loadFromHistory(chatId) {
    const chat = history.value.find(h => h.id === chatId)
    if (chat) {
      messages.value = [...chat.messages]
      currentChatId.value = chat.id
    }
  }

  function greet() {
    if (messages.value.length === 0) {
      messages.value.push({
        role: 'assistant',
        content: "Hello! I'm Zev, your AI retail assistant. How can I help you today?",
        timestamp: new Date()
      })
      saveToHistory()
    }
  }

  function newChat() {
    saveToHistory()
    messages.value = []
    currentChatId.value = Date.now().toString()
    error.value = null
    greet()
  }

  function ask(question, contextType = null) {
    if (!question?.trim() || isLoading.value) return

    messages.value.push({
      role: 'user',
      content: question.trim(),
      timestamp: new Date(),
    })

    isLoading.value = true
    error.value = null

    askResource.fetch({
      question: question.trim(),
      context_type: contextType,
    })
  }

  function searchProducts(query) {
    if (!query?.trim() || isSearching.value) return

    isSearching.value = true
    searchResource.fetch({
      query: query.trim(),
      limit: 10,
    })
  }

  function getRecommendations(customer, occasion = null) {
    if (!customer || isLoading.value) return

    messages.value.push({
      role: 'user',
      content: `Recommend products for customer ${customer}${occasion ? ` (${occasion})` : ''}`,
      timestamp: new Date(),
    })

    isLoading.value = true
    error.value = null
    recommendResource.fetch({ customer, occasion, limit: 5 })
  }

  function togglePanel() {
    isOpen.value = !isOpen.value
  }

  function openPanel() {
    isOpen.value = true
  }

  function closePanel() {
    isOpen.value = false
  }

  function clearMessages() {
    messages.value = []
    error.value = null
  }

  return {
    // State
    isOpen,
    messages,
    history,
    currentChatId,
    isLoading,
    error,
    searchResults,
    isSearching,
    // Computed
    hasMessages,
    lastMessage,
    // Actions
    ask,
    searchProducts,
    getRecommendations,
    saveToHistory,
    loadFromHistory,
    newChat,
    togglePanel,
    openPanel,
    closePanel,
    clearMessages,
  }
})
