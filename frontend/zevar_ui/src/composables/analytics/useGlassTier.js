/**
 * useGlassTier — resolves the appropriate glass tier (Plan §11.2)
 * based on the component's z-layer. 3 tiers: low, mid, high.
 */
import { computed, unref } from 'vue'

const TIER_CLASS = {
	low: 'glass-tier-1',
	mid: 'glass-tier-2',
	high: 'glass-tier-3',
}

export function useGlassTier(layer = 'low') {
	const tier = computed(() => TIER_CLASS[unref(layer)] || TIER_CLASS.low)
	const blurPx = computed(() => {
		const map = { low: 8, mid: 16, high: 24 }
		return map[unref(layer)] ?? 8
	})
	return { tier, blurPx }
}
