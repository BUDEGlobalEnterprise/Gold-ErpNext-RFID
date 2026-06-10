/**
 * useDrawerStack — Plan §5.4, DEC-REP-V2-004.
 * Right-side drawer queue. Click a metric → open a 50%-width drawer;
 * hub stays mounted behind. Esc closes the top drawer.
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'

export function useDrawerStack() {
	const stack = ref([]) // [{ id, title, component, props }]
	const isOpen = computed(() => stack.value.length > 0)
	const current = computed(() => stack.value[stack.value.length - 1] || null)

	function open(drawer) {
		stack.value.push({ id: Date.now() + Math.random(), ...drawer })
	}
	function close() {
		stack.value.pop()
	}
	function closeAll() {
		stack.value = []
	}

	function handleKey(e) {
		if (e.key === 'Escape' && isOpen.value) {
			e.preventDefault()
			close()
		}
	}

	onMounted(() => window.addEventListener('keydown', handleKey))
	onUnmounted(() => window.removeEventListener('keydown', handleKey))

	return { stack, isOpen, current, open, close, closeAll }
}
