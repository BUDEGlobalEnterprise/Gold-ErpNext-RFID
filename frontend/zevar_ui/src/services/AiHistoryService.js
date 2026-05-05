/**
 * AI History Service
 * 
 * Handles persistence for AI chat history in localStorage.
 */

const STORAGE_KEY = 'ai-chat-history'

export const AiHistoryService = {
  loadHistory() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    } catch (e) {
      console.error('Failed to load AI history', e)
      return []
    }
  },

  saveHistory(history) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history))
    } catch (e) {
      console.error('Failed to save AI history', e)
    }
  },

  archiveChat(chatId, messages) {
    if (!messages || messages.length === 0) return
    
    const history = this.loadHistory()
    const existingIndex = history.findIndex(h => h.id === chatId)
    
    const userMsg = messages.find(m => m.role === 'user')?.content.trim()
    const title = userMsg 
      ? (userMsg.substring(0, 30) + (userMsg.length > 30 ? '...' : ''))
      : 'New Chat'

    const chatData = {
      id: chatId,
      title,
      messages: [...messages],
      updatedAt: new Date().toISOString()
    }

    if (existingIndex > -1) {
      history[existingIndex] = chatData
    } else {
      history.unshift(chatData)
    }
    
    // Limit to 20 items
    const limitedHistory = history.slice(0, 20)
    this.saveHistory(limitedHistory)
    return limitedHistory
  }
}
