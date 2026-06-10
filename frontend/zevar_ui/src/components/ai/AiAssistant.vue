<template>
	<!-- Floating AI Button -->
	<button
		v-if="!isOpen"
		class="ai-fab"
		:class="{ 'ai-fab--pulse': !hasMessages, 'ai-fab--dragging': isFabDragging }"
		:style="{ left: fabPosition.x + 'px', top: fabPosition.y + 'px' }"
		@mousedown="startFabDrag"
		@touchstart="startFabDrag"
		@click="handleFabClick"
		title="Zev AI Assistant"
	>
		<svg
			width="24"
			height="24"
			viewBox="0 0 24 24"
			fill="none"
			stroke="currentColor"
			stroke-width="2"
		>
			<path
				d="M12 2a7 7 0 0 1 7 7c0 2.5-1.3 4.8-3.5 6v1.5a1.5 1.5 0 0 1-1.5 1.5h-4a1.5 1.5 0 0 1-1.5-1.5V15C6.3 13.8 5 11.5 5 9a7 7 0 0 1 7-7z"
			/>
			<line x1="9" y1="21" x2="15" y2="21" />
		</svg>
		<span v-if="!hasMessages" class="ai-fab__badge">AI</span>
	</button>

	<!-- AI Chat Panel -->
	<Transition name="ai-slide">
		<div v-if="isOpen" class="ai-panel" :style="panelStyle">
			<!-- Header -->
			<div
				class="ai-panel__header"
				:class="{ 'ai-panel__header--dragging': isPanelDragging }"
				@mousedown="startPanelDrag"
				@touchstart="startPanelDrag"
			>
				<div class="ai-panel__title">
					<svg
						width="18"
						height="18"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<path
							d="M12 2a7 7 0 0 1 7 7c0 2.5-1.3 4.8-3.5 6v1.5a1.5 1.5 0 0 1-1.5 1.5h-4a1.5 1.5 0 0 1-1.5-1.5V15C6.3 13.8 5 11.5 5 9a7 7 0 0 1 7-7z"
						/>
					</svg>
					<span>Zev</span>
				</div>
				<div class="ai-panel__actions">
					<button
						class="ai-btn-icon"
						@click="isHistoryOpen = !isHistoryOpen"
						:class="{ 'ai-btn-icon--active': isHistoryOpen }"
						title="History"
					>
						<svg
							width="16"
							height="16"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					</button>
					<button class="ai-btn-icon" @click="newChat" title="New Chat">
						<svg
							width="16"
							height="16"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<line x1="12" y1="5" x2="12" y2="19" />
							<line x1="5" y1="12" x2="19" y2="12" />
						</svg>
					</button>
					<button class="ai-btn-icon" @click="closePanel" title="Close">
						<svg
							width="16"
							height="16"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<line x1="18" y1="6" x2="6" y2="18" />
							<line x1="6" y1="6" x2="18" y2="18" />
						</svg>
					</button>
				</div>
			</div>

			<!-- History Overlay -->
			<Transition name="ai-fade">
				<div v-if="isHistoryOpen" class="ai-history">
					<div class="ai-history__header">
						<span>Recent Chats</span>
					</div>
					<div class="ai-history__list">
						<div v-if="history.length === 0" class="ai-history__empty">
							No history yet
						</div>
						<button
							v-for="chat in history"
							:key="chat.id"
							class="ai-history__item"
							:class="{ 'ai-history__item--active': chat.id === currentChatId }"
							@click="
								loadFromHistory(chat.id)
								isHistoryOpen = false
							"
						>
							<div class="ai-history__item-title">{{ chat.title }}</div>
							<div class="ai-history__item-date">
								{{ new Date(chat.updatedAt).toLocaleDateString() }}
							</div>
						</button>
					</div>
				</div>
			</Transition>

			<!-- Messages -->
			<div ref="messagesContainer" class="ai-panel__messages">
				<!-- Welcome message - Show if no user messages yet -->
				<div v-if="!hasUserMessages" class="ai-welcome">
					<div class="ai-welcome__icon">✨</div>
					<p class="ai-welcome__text">
						Hi! I'm Zev. I can help you find products, answer policy questions, and
						assist with automation.
					</p>
					<div class="ai-welcome__actions">
						<button
							v-for="action in quickActions"
							:key="action.label"
							class="ai-quick-btn"
							@click="sendQuickAction(action)"
						>
							{{ action.label }}
						</button>
					</div>
				</div>

				<!-- Chat messages -->
				<AiChatMessage v-for="(msg, i) in messages" :key="i" :message="msg" />

				<!-- Loading indicator -->
				<div v-if="isLoading" class="ai-loading">
					<div class="ai-loading__dots"><span></span><span></span><span></span></div>
					<span>Thinking...</span>
				</div>
			</div>

			<!-- Input -->
			<div class="ai-panel__input">
				<input
					ref="inputEl"
					v-model="inputText"
					class="ai-input"
					placeholder="Ask about products, policies, customers..."
					:disabled="isLoading"
					@keydown.enter="sendMessage"
				/>
				<button
					class="ai-send-btn"
					:disabled="!inputText.trim() || isLoading"
					@click="sendMessage"
				>
					<svg
						width="18"
						height="18"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<line x1="22" y1="2" x2="11" y2="13" />
						<polygon points="22 2 15 22 11 13 2 9 22 2" />
					</svg>
				</button>
			</div>
		</div>
	</Transition>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useAiAssistant } from '@/composables/useAiAssistant.js'
import { useDraggable } from '@/composables/useDraggable.js'
import { usePanelPositioning } from '@/composables/usePanelPositioning.js'
import AiChatMessage from './AiChatMessage.vue'

const {
	inputText,
	isOpen,
	messages,
	history,
	currentChatId,
	isLoading,
	hasMessages,
	sendMessage,
	sendQuickAction,
	togglePanel,
	closePanel,
	newChat,
	greet,
	loadFromHistory,
} = useAiAssistant()

const messagesContainer = ref(null)
const inputEl = ref(null)
const isHistoryOpen = ref(false)

// --- Draggable Logic (FAB) ---
const {
	position: fabPosition,
	isDragging: isFabDragging,
	hasMoved: fabHasMoved,
	startDrag: startFabDrag,
} = useDraggable({
	storageKeyX: 'ai-assistant-pos-x',
	storageKeyY: 'ai-assistant-pos-y',
	initialPos: { x: window.innerWidth - 80, y: window.innerHeight - 80 },
})

// --- Draggable Logic (Panel) ---
const {
	position: panelPosition,
	isDragging: isPanelDragging,
	hasMoved: isPanelMoved,
	startDrag: startPanelDrag,
} = useDraggable({
	initialPos: { x: -1, y: -1 },
	size: 400,
	margin: 16,
})

const hasUserMessages = computed(() => messages.value.some((m) => m.role === 'user'))

// --- Positioning Logic ---
const { panelStyle, initializePosition } = usePanelPositioning(
	panelPosition,
	fabPosition,
	isPanelDragging
)

function handleFabClick() {
	if (!fabHasMoved.value) {
		togglePanel()
	}
}

// Initialize panel position near FAB on first open
watch(isOpen, async (val) => {
	if (val) {
		await nextTick()
		inputEl.value?.focus()

		// Position panel near FAB if not yet positioned
		initializePosition()

		// Add a greeting message if chat is empty
		if (!hasMessages.value) {
			setTimeout(() => {
				if (!hasMessages.value && isOpen.value) {
					greet()
				}
			}, 500)
		}
	}
})

const quickActions = [
	{
		label: 'Find products',
		question: 'Show me trending gold necklaces',
		contextType: 'product',
	},
	{
		label: 'Store policies',
		question: 'What is the layaway cancellation policy?',
		contextType: 'policy',
	},
	{
		label: 'Repair help',
		question: 'What is the standard repair process?',
		contextType: 'repair',
	},
]

// Auto-scroll to bottom when new messages arrive
watch(
	() => messages.value.length,
	async () => {
		await nextTick()
		if (messagesContainer.value) {
			messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
		}
	}
)
</script>

<style scoped>
.ai-fab {
	position: fixed;
	z-index: 1000;
	width: 56px;
	height: 56px;
	border-radius: 50%;
	background: linear-gradient(135deg, #8b5cf6, #6366f1);
	color: white;
	border: none;
	cursor: grab;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
	transition: transform 0.2s, box-shadow 0.2s;
	touch-action: none;
	user-select: none;
}

.ai-fab--dragging {
	cursor: grabbing;
	transform: scale(1.05);
	box-shadow: 0 8px 24px rgba(99, 102, 241, 0.6);
	transition: none;
}

.ai-fab:hover:not(.ai-fab--dragging) {
	transform: scale(1.1);
	box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
}

.ai-fab--pulse {
	animation: pulse 2s infinite;
}

.ai-fab__badge {
	position: absolute;
	top: -4px;
	right: -4px;
	background: #ef4444;
	color: white;
	font-size: 10px;
	font-weight: 700;
	padding: 2px 6px;
	border-radius: 8px;
}

@keyframes pulse {
	0%,
	100% {
		box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
	}
	50% {
		box-shadow: 0 4px 24px rgba(99, 102, 241, 0.6);
	}
}

.ai-panel {
	position: fixed;
	z-index: 1000;
	width: 400px;
	max-height: 600px;
	display: flex;
	flex-direction: column;
	border-radius: 16px;
	background: white;
	box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.06);
	overflow: hidden;
	border: 1px solid #e5e7eb;
}

.dark .ai-panel {
	background: #1f2937;
	border-color: #374151;
}

.ai-panel__header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 14px 16px;
	background: linear-gradient(135deg, #8b5cf6, #6366f1);
	color: white;
	cursor: grab;
	user-select: none;
	touch-action: none;
}

.ai-panel__header--dragging {
	cursor: grabbing;
}

.ai-panel__title {
	display: flex;
	align-items: center;
	gap: 8px;
	font-weight: 600;
	font-size: 15px;
}

.ai-panel__actions {
	display: flex;
	gap: 4px;
}

.ai-btn-icon {
	background: none;
	border: none;
	color: rgba(255, 255, 255, 0.8);
	cursor: pointer;
	padding: 4px;
	border-radius: 6px;
	display: flex;
	align-items: center;
}

.ai-btn-icon:hover,
.ai-btn-icon--active {
	color: white;
	background: rgba(255, 255, 255, 0.15);
}

.ai-history {
	position: absolute;
	top: 48px;
	left: 0;
	right: 0;
	bottom: 0;
	background: white;
	z-index: 10;
	display: flex;
	flex-direction: column;
}

.dark .ai-history {
	background: #1f2937;
}

.ai-history__header {
	padding: 12px 16px;
	border-bottom: 1px solid #e5e7eb;
	font-size: 13px;
	font-weight: 600;
	color: #6b7280;
}

.dark .ai-history__header {
	border-color: #374151;
	color: #9ca3af;
}

.ai-history__list {
	flex: 1;
	overflow-y: auto;
	padding: 8px;
}

.ai-history__item {
	width: 100%;
	text-align: left;
	padding: 10px 12px;
	border-radius: 8px;
	margin-bottom: 4px;
	border: none;
	background: none;
	cursor: pointer;
	transition: background 0.15s;
}

.ai-history__item:hover {
	background: #f3f4f6;
}

.dark .ai-history__item:hover {
	background: #374151;
}

.ai-history__item--active {
	background: #eff6ff;
}

.dark .ai-history__item--active {
	background: #1e3a8a;
}

.ai-history__item-title {
	font-size: 14px;
	font-weight: 500;
	color: #111827;
	margin-bottom: 2px;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.dark .ai-history__item-title {
	color: #f3f4f6;
}

.ai-history__item-date {
	font-size: 11px;
	color: #6b7280;
}

.ai-history__empty {
	text-align: center;
	padding: 40px 20px;
	color: #9ca3af;
	font-size: 14px;
}

.ai-panel__messages {
	flex: 1;
	overflow-y: auto;
	padding: 16px;
	display: flex;
	flex-direction: column;
	gap: 12px;
	min-height: 300px;
	max-height: 440px;
}

.ai-welcome {
	text-align: center;
	padding: 24px 16px;
}

.ai-welcome__icon {
	font-size: 36px;
	margin-bottom: 12px;
}

.ai-welcome__text {
	color: #6b7280;
	font-size: 14px;
	line-height: 1.5;
	margin-bottom: 16px;
}

.dark .ai-welcome__text {
	color: #9ca3af;
}

.ai-welcome__actions {
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
	justify-content: center;
}

.ai-quick-btn {
	padding: 6px 14px;
	border-radius: 20px;
	border: 1px solid #e5e7eb;
	background: white;
	color: #6366f1;
	font-size: 13px;
	cursor: pointer;
	transition: all 0.15s;
}

.dark .ai-quick-btn {
	background: #374151;
	border-color: #4b5563;
	color: #a5b4fc;
}

.ai-quick-btn:hover {
	background: #f3f4f6;
	border-color: #6366f1;
}

.dark .ai-quick-btn:hover {
	background: #4b5563;
}

.ai-loading {
	display: flex;
	align-items: center;
	gap: 8px;
	color: #9ca3af;
	font-size: 13px;
	padding: 4px 0;
}

.ai-loading__dots span {
	display: inline-block;
	width: 6px;
	height: 6px;
	border-radius: 50%;
	background: #9ca3af;
	animation: bounce 1.4s infinite ease-in-out;
}

.ai-loading__dots span:nth-child(1) {
	animation-delay: -0.32s;
}
.ai-loading__dots span:nth-child(2) {
	animation-delay: -0.16s;
}

@keyframes bounce {
	0%,
	80%,
	100% {
		transform: scale(0);
	}
	40% {
		transform: scale(1);
	}
}

.ai-panel__input {
	display: flex;
	gap: 8px;
	padding: 12px 16px;
	border-top: 1px solid #e5e7eb;
	background: #f9fafb;
}

.dark .ai-panel__input {
	border-color: #374151;
	background: #111827;
}

.ai-input {
	flex: 1;
	padding: 10px 14px;
	border-radius: 12px;
	border: 1px solid #e5e7eb;
	font-size: 14px;
	outline: none;
	background: white;
	transition: border-color 0.15s;
}

.dark .ai-input {
	background: #1f2937;
	border-color: #4b5563;
	color: #f3f4f6;
}

.ai-input:focus {
	border-color: #6366f1;
}

.ai-input:disabled {
	opacity: 0.6;
}

.ai-send-btn {
	width: 40px;
	height: 40px;
	border-radius: 12px;
	background: linear-gradient(135deg, #8b5cf6, #6366f1);
	color: white;
	border: none;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: opacity 0.15s;
}

.ai-send-btn:disabled {
	opacity: 0.4;
	cursor: not-allowed;
}

.ai-send-btn:not(:disabled):hover {
	opacity: 0.9;
}

/* Slide transition */
.ai-slide-enter-active,
.ai-slide-leave-active {
	transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.ai-slide-enter-from,
.ai-slide-leave-to {
	transform: translateY(12px) scale(0.98);
	opacity: 0;
}

/* Fade transition */
.ai-fade-enter-active,
.ai-fade-leave-active {
	transition: opacity 0.2s ease;
}

.ai-fade-enter-from,
.ai-fade-leave-to {
	opacity: 0;
}

/* Mobile responsive */
@media (max-width: 480px) {
	.ai-panel {
		width: calc(100vw - 16px);
		right: 8px;
		bottom: 8px;
		max-height: calc(100vh - 80px);
		border-radius: 12px;
	}
}
</style>
