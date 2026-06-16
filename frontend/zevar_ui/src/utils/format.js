/**
 * Shared formatters for the monitor dashboards (Quick-Win Q9).
 *
 * Replaces the 7 duplicate `function fmt()` copies that lived in
 * pages/dashboards/*.vue. Phase 0 will also fold `composables/useFormatters.js`
 * in here so there is a single formatting surface.
 */

const TWO = { minimumFractionDigits: 2, maximumFractionDigits: 2 }

/** Number -> 2-decimal string with thousands separators (the old dashboard `fmt`). */
export function fmt(n) {
	return Number(n || 0).toLocaleString('en-US', TWO)
}

export function fmtCurrency(n, currency = 'USD') {
	if (n == null || n === '') return ''
	return Number(n).toLocaleString('en-US', { ...TWO, style: 'currency', currency })
}

export function fmtPercent(n, digits = 1) {
	if (n == null || n === '') return ''
	return `${Number(n).toFixed(digits)}%`
}

export function fmtCompact(n) {
	if (n == null || n === '') return ''
	return Number(n).toLocaleString('en-US', {
		notation: 'compact',
		maximumFractionDigits: 1,
	})
}

export function fmtNumber(n, digits = 0) {
	if (n == null || n === '') return ''
	return Number(n).toLocaleString('en-US', {
		minimumFractionDigits: digits,
		maximumFractionDigits: digits,
	})
}

export function fmtDate(d) {
	if (!d) return ''
	const dt = new Date(d)
	if (Number.isNaN(dt.getTime())) return String(d)
	return dt.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

export function fmtRelativeTime(d) {
	if (!d) return ''
	const dt = new Date(d)
	if (Number.isNaN(dt.getTime())) return String(d)
	const secs = Math.round((Date.now() - dt.getTime()) / 1000)
	const abs = Math.abs(secs)
	if (abs < 60) return 'just now'
	if (abs < 3600) return `${Math.round(secs / 60)}m ago`
	if (abs < 86400) return `${Math.round(secs / 3600)}h ago`
	return `${Math.round(secs / 86400)}d ago`
}
