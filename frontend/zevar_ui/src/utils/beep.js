/**
 * Audio beep synthesizer using the Web Audio API.
 *
 * Generates a short, pleasant "scan success" tone with zero latency
 * and no external audio file dependency.
 */

let audioCtx = null

function getAudioContext() {
	if (!audioCtx) {
		audioCtx = new (window.AudioContext || window.webkitAudioContext)()
	}
	return audioCtx
}

export function playBeep(frequency = 1200, duration = 120, volume = 0.3) {
	try {
		const ctx = getAudioContext()
		if (ctx.state === 'suspended') {
			ctx.resume()
		}

		const oscillator = ctx.createOscillator()
		const gainNode = ctx.createGain()

		oscillator.connect(gainNode)
		gainNode.connect(ctx.destination)

		oscillator.type = 'sine'
		oscillator.frequency.setValueAtTime(frequency, ctx.currentTime)

		// Quick fade-in / fade-out to avoid clicks
		gainNode.gain.setValueAtTime(0, ctx.currentTime)
		gainNode.gain.linearRampToValueAtTime(volume, ctx.currentTime + 0.01)
		gainNode.gain.linearRampToValueAtTime(0, ctx.currentTime + duration / 1000)

		oscillator.start(ctx.currentTime)
		oscillator.stop(ctx.currentTime + duration / 1000)
	} catch {
		// Audio not available — silent fallback
	}
}
