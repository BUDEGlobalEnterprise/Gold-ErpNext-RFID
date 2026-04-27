/**
 * Date Formatting Utility
 *
 * Centralized date formatting to ensure consistent US date format (MM/DD/YYYY)
 * regardless of browser locale settings.
 */

const MONTH_NAMES = [
	'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
	'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
]

/**
 * Format date to US format with abbreviated month (e.g., "Apr 26, 2025")
 * @param {string|Date} dateStr - Date string or Date object
 * @returns {string} Formatted date
 */
export function formatDate(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	if (isNaN(date.getTime())) return ''

	const month = MONTH_NAMES[date.getMonth()]
	const day = date.getDate()
	const year = date.getFullYear()

	return `${month} ${day}, ${year}`
}

/**
 * Format date to US format with abbreviated month and day only (e.g., "Apr 26")
 * @param {string|Date} dateStr - Date string or Date object
 * @returns {string} Formatted date
 */
export function formatDateShort(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	if (isNaN(date.getTime())) return ''

	const month = MONTH_NAMES[date.getMonth()]
	const day = date.getDate()

	return `${month} ${day}`
}

/**
 * Format date and time to US format (e.g., "Apr 26, 2025, 2:30 PM")
 * @param {string|Date} dateStr - Date string or Date object
 * @returns {string} Formatted date and time
 */
export function formatDateTime(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	if (isNaN(date.getTime())) return ''

	const month = MONTH_NAMES[date.getMonth()]
	const day = date.getDate()
	const year = date.getFullYear()
	let hours = date.getHours()
	const minutes = date.getMinutes().toString().padStart(2, '0')
	const ampm = hours >= 12 ? 'PM' : 'AM'

	hours = hours % 12
	hours = hours ? hours : 12 // Convert 0 to 12

	return `${month} ${day}, ${year}, ${hours}:${minutes} ${ampm}`
}

/**
 * Format date to numeric US format (e.g., "04/26/2025")
 * @param {string|Date} dateStr - Date string or Date object
 * @returns {string} Formatted date
 */
export function formatDateNumeric(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	if (isNaN(date.getTime())) return ''

	const month = (date.getMonth() + 1).toString().padStart(2, '0')
	const day = date.getDate().toString().padStart(2, '0')
	const year = date.getFullYear()

	return `${month}/${day}/${year}`
}
