/**
 * Responsive Design Utilities Composable
 *
 * Provides reactive design detection and grid utilities.
 * Breakpoints match Tailwind defaults:
 *   sm: 640, md: 768, lg: 1024, xl: 1280, 2xl: 1536
 */

import { ref, onMounted, onUnmounted, computed } from 'vue'

const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1280)
const windowHeight = ref(typeof window !== 'undefined' ? window.innerHeight : 800)

// Breakpoint definitions (aligned with Tailwind)
const BREAKPOINTS = {
	sm: 640,
	md: 768,
	lg: 1024,
	xl: 1280,
	'2xl': 1536,
}

function useResponsive() {
	// Reactive device flags
	const isMobile = computed(() => windowWidth.value < BREAKPOINTS.md) // < 768
	const isTablet = computed(() => windowWidth.value >= BREAKPOINTS.md && windowWidth.value < BREAKPOINTS.lg) // 768–1023
	const isMobileOrTablet = computed(() => windowWidth.value < BREAKPOINTS.lg) // < 1024
	const isDesktop = computed(() => windowWidth.value >= BREAKPOINTS.lg) // >= 1024
	const isLargeDesktop = computed(() => windowWidth.value >= BREAKPOINTS.xl) // >= 1280
	const isXLDesktop = computed(() => windowWidth.value >= BREAKPOINTS['2xl']) // >= 1536

	const isTouchDevice = computed(() => {
		if (typeof window === 'undefined') return false
		return 'ontouchstart' in window || navigator.maxTouchPoints > 0
	})

	const orientation = computed(() => {
		if (typeof window === 'undefined') return 'portrait'
		return windowWidth.value > windowHeight.value ? 'landscape' : 'portrait'
	})

	// Grid columns based on device
	const gridColumns = computed(() => {
		if (isMobile.value) return 1
		if (isTablet.value) return 2
		if (isDesktop.value && !isLargeDesktop.value) return 3
		return 4
	})

	// Safe area insets (for notched devices)
	const safeAreaInsets = computed(() => {
		if (typeof document === 'undefined') return { top: 0, bottom: 0, left: 0, right: 0 }
		const style = getComputedStyle(document.documentElement)
		return {
			top: parseInt(style.getPropertyValue('--safe-area-inset-top') || '0'),
			bottom: parseInt(style.getPropertyValue('--safe-area-inset-bottom') || '0'),
			left: parseInt(style.getPropertyValue('--safe-area-inset-left') || '0'),
			right: parseInt(style.getPropertyValue('--safe-area-inset-right') || '0'),
		}
	})

	// Update dimensions on resize
	function updateDimensions() {
		windowWidth.value = window.innerWidth
		windowHeight.value = window.innerHeight
	}

	onMounted(() => {
		updateDimensions()
		window.addEventListener('resize', updateDimensions)
		window.addEventListener('orientationchange', updateDimensions)
	})

	onUnmounted(() => {
		window.removeEventListener('resize', updateDimensions)
		window.removeEventListener('orientationchange', updateDimensions)
	})

	return {
		// Dimensions
		windowWidth,
		windowHeight,
		// Device flags
		isMobile,
		isTablet,
		isMobileOrTablet,
		isDesktop,
		isLargeDesktop,
		isXLDesktop,
		// Computed
		orientation,
		gridColumns,
		isTouchDevice,
		safeAreaInsets,
		// Constants
		BREAKPOINTS,
	}
}

// CSS class helpers for responsive design
export const responsiveClasses = computed(() => ({
	mobile: windowWidth.value < BREAKPOINTS.md,
	tablet: windowWidth.value >= BREAKPOINTS.md && windowWidth.value < BREAKPOINTS.lg,
	desktop: windowWidth.value >= BREAKPOINTS.lg,
	largeDesktop: windowWidth.value >= BREAKPOINTS.xl,
	touch: typeof window !== 'undefined' && ('ontouchstart' in window || navigator.maxTouchPoints > 0),
	portrait: windowWidth.value <= windowHeight.value,
	landscape: windowWidth.value > windowHeight.value,
}))

export default useResponsive
