/**
 * Theme Composable
 *
 * Shared theme management — syncs with the UI store's 'theme' key
 * so Dashboard and Terminal/AppLayout share a single toggle.
 */
import { ref, onMounted } from 'vue'

const THEME_KEY = 'theme'

export function useTheme() {
	const isDark = ref(false)
	const themeKey = ref(0)

	const loadTheme = () => {
		const stored = localStorage.getItem(THEME_KEY)
		// Default to dark only on first visit (no stored preference)
		if (stored === null) {
			isDark.value = true
			localStorage.setItem(THEME_KEY, 'dark')
		} else {
			isDark.value = stored === 'dark'
		}
		updateDocumentClass()
	}

	const toggleTheme = () => {
		isDark.value = !isDark.value
		localStorage.setItem(THEME_KEY, isDark.value ? 'dark' : 'light')
		updateDocumentClass()
		themeKey.value++
	}

	const updateDocumentClass = () => {
		document.documentElement.classList.toggle('dark', isDark.value)
		document.body.style.backgroundColor = isDark.value ? '#08080a' : '#ffffff'
	}

	onMounted(() => {
		loadTheme()
	})

	return {
		isDark,
		themeKey,
		toggleTheme,
		loadTheme,
	}
}
