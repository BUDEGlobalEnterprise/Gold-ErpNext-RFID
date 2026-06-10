<template>
	<span ref="el" class="font-bold tabular-nums">{{ display }}</span>
</template>

<script setup>
/**
 * AnimatedNumber — Plan §7.6, 50 LOC budget.
 * Count-up animation, 1.2s on first appearance, then static (Pixel Show §11.6).
 */
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
	value: { type: Number, default: 0 },
	duration: { type: Number, default: 1200 },
	decimals: { type: Number, default: 0 },
	prefix: { type: String, default: '' },
	suffix: { type: String, default: '' },
})

const display = ref(format(0))
const el = ref(null)
let started = false

function format(v) {
	return `${props.prefix}${v.toFixed(props.decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}${
		props.suffix
	}`
}

function run() {
	if (started) return
	started = true
	const start = performance.now()
	const from = 0
	const to = Number(props.value) || 0
	function tick(now) {
		const t = Math.min(1, (now - start) / props.duration)
		// ease-out cubic
		const eased = 1 - Math.pow(1 - t, 3)
		display.value = format(from + (to - from) * eased)
		if (t < 1) requestAnimationFrame(tick)
	}
	requestAnimationFrame(tick)
}

onMounted(() => {
	if (typeof IntersectionObserver === 'undefined') {
		run()
		return
	}
	const io = new IntersectionObserver(
		(entries) => {
			if (entries[0]?.isIntersecting) {
				run()
				io.disconnect()
			}
		},
		{ threshold: 0.1 }
	)
	if (el.value) io.observe(el.value)
})

watch(
	() => props.value,
	() => {
		display.value = format(props.value)
	}
)
</script>
