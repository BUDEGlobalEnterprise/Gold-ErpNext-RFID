/**
 * AI Assistant Composable
 *
 * Provides reactive state and methods for the AI assistant.
 * Wraps the Pinia store with additional UI logic.
 */
import { computed, ref } from 'vue'
import { useAiStore } from '@/stores/ai.js'

export function useAiAssistant() {
	const store = useAiStore()
	const inputText = ref('')

	const isOpen = computed(() => store.isOpen)
	const messages = computed(() => store.messages)
	const isLoading = computed(() => store.isLoading)
	const hasMessages = computed(() => store.hasMessages)
	const history = computed(() => store.history)
	const currentChatId = computed(() => store.currentChatId)

	function sendMessage() {
		const text = inputText.value.trim()
		if (!text) return

		store.ask(text)
		inputText.value = ''
	}

	function sendQuickAction(action) {
		store.ask(action.question, action.contextType)
	}

	function togglePanel() {
		store.togglePanel()
	}

	function closePanel() {
		store.closePanel()
	}

	function newChat() {
		store.newChat()
	}

	function greet() {
		store.greet()
	}

	function loadFromHistory(chatId) {
		store.loadFromHistory(chatId)
	}

	function getRecommendations(customer, occasion = null) {
		store.getRecommendations(customer, occasion)
	}

	return {
		inputText,
		isOpen,
		messages,
		history,
		currentChatId,
		isLoading,
		hasMessages,
		sendMessage,
		sendQuickAction,
		getRecommendations,
		togglePanel,
		closePanel,
		newChat,
		greet,
		loadFromHistory,
	}
}
