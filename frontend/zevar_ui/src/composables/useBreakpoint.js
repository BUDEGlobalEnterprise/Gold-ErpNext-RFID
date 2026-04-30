import { ref, computed, onMounted, onUnmounted, readonly } from 'vue'

/**
 * useBreakpoint — Mobile-first responsive breakpoint composable
 *
 * Breakpoint bands (aligned with Tailwind):
 *   xs:  < 640px   (phone portrait)
 *   sm:  640–767   (large phone / phone landscape)
 *   md:  768–1023  (tablet portrait / POS 10")
 *   lg:  1024–1279 (tablet landscape / laptop)
 *   xl:  1280–1535 (desktop)
 *   2xl: ≥ 1536    (wide monitor)
 *
 * Semantic helpers:
 *   isMobile      < md  (phone)
 *   isTablet      md–lg (tablet)
 *   isDesktop     ≥ lg
 *   isLargeDesktop ≥ xl
 */

const BREAKPOINTS = {
	xs: 0,
	sm: 640,
	md: 768,
	lg: 1024,
	xl: 1280,
	'2xl': 1536,
}

// Singleton shared state — one listener for all consumers
const width = ref(typeof window !== 'undefined' ? window.innerWidth : 1280)
const height = ref(typeof window !== 'undefined' ? window.innerHeight : 800)
const dpr = ref(typeof window !== 'undefined' ? window.devicePixelRatio : 1)
const reducedMotion = ref(false)

let listenerCount = 0
let mqlList = []

function updateFromWindow() {
	width.value = window.innerWidth
	height.value = window.innerHeight
	dpr.value = window.devicePixelRatio
}

function initListeners() {
	// Use matchMedia for efficient breakpoint listening
	updateFromWindow()

	// Listen for resize via matchMedia on common boundaries
	const queries = [
		window.matchMedia('(max-width: 639px)'),
		window.matchMedia('(min-width: 640px)'),
		window.matchMedia('(min-width: 768px)'),
		window.matchMedia('(min-width: 1024px)'),
		window.matchMedia('(min-width: 1280px)'),
		window.matchMedia('(min-width: 1536px)'),
	]

	const handler = () => updateFromWindow()
	for (const mql of queries) {
		mql.addEventListener('change', handler)
	}
	mqlList = queries

	// Detect prefers-reduced-motion
	const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
	reducedMotion.value = motionQuery.matches
	motionQuery.addEventListener('change', (e) => {
		reducedMotion.value = e.matches
	})
	mqlList.push(motionQuery)

	// Fallback: also listen to resize for edge cases
	window.addEventListener('resize', updateFromWindow, { passive: true })
}

function destroyListeners() {
	for (const mql of mqlList) {
		mql.removeEventListener('change', updateFromWindow)
	}
	mqlList = []
	window.removeEventListener('resize', updateFromWindow)
}

export function useBreakpoint() {
	// Individual breakpoint bands
	const xs = computed(() => width.value < BREAKPOINTS.sm)
	const sm = computed(() => width.value >= BREAKPOINTS.sm && width.value < BREAKPOINTS.md)
	const md = computed(() => width.value >= BREAKPOINTS.md && width.value < BREAKPOINTS.lg)
	const lg = computed(() => width.value >= BREAKPOINTS.lg && width.value < BREAKPOINTS.xl)
	const xl = computed(() => width.value >= BREAKPOINTS.xl && width.value < BREAKPOINTS['2xl'])
	const xxl = computed(() => width.value >= BREAKPOINTS['2xl'])

	// Semantic device flags
	const isMobile = computed(() => width.value < BREAKPOINTS.md)
	const isTablet = computed(() => width.value >= BREAKPOINTS.md && width.value < BREAKPOINTS.lg)
	const isDesktop = computed(() => width.value >= BREAKPOINTS.lg)
	const isLargeDesktop = computed(() => width.value >= BREAKPOINTS.xl)

	const isTouchDevice = computed(() => {
		if (typeof window === 'undefined') return false
		return 'ontouchstart' in window || navigator.maxTouchPoints > 0
	})

	const orientation = computed(() =>
		width.value > height.value ? 'landscape' : 'portrait'
	)

	// Grid column presets for responsive grids
	const gridCols = computed(() => {
		if (isMobile.value) return 1
		if (isTablet.value) return 2
		if (lg.value) return 3
		return 4
	})

	// Product grid columns (higher density)
	const productGridCols = computed(() => {
		if (xs.value) return 2
		if (sm.value) return 3
		if (md.value) return 4
		if (lg.value) return 5
		return 6
	})

	// Safe area insets for notched devices
	const safeAreaInsets = computed(() => {
		if (typeof document === 'undefined') return { top: 0, bottom: 0, left: 0, right: 0 }
		const s = getComputedStyle(document.documentElement)
		return {
			top: parseInt(s.getPropertyValue('--safe-area-inset-top') || '0'),
			bottom: parseInt(s.getPropertyValue('--safe-area-inset-bottom') || '0'),
			left: parseInt(s.getPropertyValue('--safe-area-inset-left') || '0'),
			right: parseInt(s.getPropertyValue('--safe-area-inset-right') || '0'),
		}
	})

	// Layout mode for AppShell
	const layoutMode = computed(() => {
		if (isMobile.value) return 'mobile'
		if (isTablet.value) return 'tablet'
		return 'desktop'
	})

	// Touch target size recommendation
	const touchTarget = computed(() => isMobile.value ? 44 : 36)

	onMounted(() => {
		listenerCount++
		if (listenerCount === 1) initListeners()
	})

	onUnmounted(() => {
		listenerCount--
		if (listenerCount <= 0) {
			listenerCount = 0
			destroyListeners()
		}
	})

	return {
		// Dimensions
		width: readonly(width),
		height: readonly(height),
		dpr: readonly(dpr),
		// Individual breakpoints
		xs, sm, md, lg, xl, xxl,
		// Semantic flags
		isMobile,
		isTablet,
		isDesktop,
		isLargeDesktop,
		isTouchDevice,
		// Computed helpers
		orientation,
		gridCols,
		productGridCols,
		safeAreaInsets,
		layoutMode,
		touchTarget,
		reducedMotion: readonly(reducedMotion),
		// Constants
		BREAKPOINTS,
	}
}

export { BREAKPOINTS }
export default useBreakpoint
