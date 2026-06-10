<template>
	<div
		class="mb-6 p-4 bg-white dark:bg-warm-dark-900 rounded-lg border border-gray-200 dark:border-warm-border"
	>
		<h3 class="font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
			<span class="material-symbols-outlined !text-lg text-[#D4AF37]">star</span>
			Rate Your Experience
		</h3>

		<div v-if="submitted" class="text-center p-6 bg-green-50 dark:bg-green-900/20 rounded-lg">
			<div
				class="w-12 h-12 bg-green-100 dark:bg-green-800 rounded-full flex items-center justify-center mx-auto mb-3 text-green-600 dark:text-green-400"
			>
				<span class="material-symbols-outlined !text-2xl">thumb_up</span>
			</div>
			<p class="font-bold text-green-700 dark:text-green-300">
				Thank you for your feedback!
			</p>
			<p class="text-sm text-green-600 dark:text-green-400 mt-1">
				We appreciate you choosing Zevar Jewelers.
			</p>
		</div>

		<form v-else @submit.prevent="submitReview" class="space-y-4">
			<div class="flex flex-col items-center py-4">
				<p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
					How would you rate your repair?
				</p>
				<div class="flex gap-2">
					<button
						v-for="star in 5"
						:key="star"
						type="button"
						@click="rating = star"
						@mouseenter="hoverRating = star"
						@mouseleave="hoverRating = 0"
						class="p-1 transition focus:outline-none"
					>
						<span
							class="material-symbols-outlined !text-3xl transition-colors"
							:class="
								(hoverRating ? star <= hoverRating : star <= rating)
									? 'text-[#D4AF37]'
									: 'text-gray-300 dark:text-gray-600'
							"
						>
							star
						</span>
					</button>
				</div>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
					>Any comments or feedback?</label
				>
				<textarea
					v-model="comments"
					rows="3"
					placeholder="Tell us what you loved or how we can improve..."
					class="w-full px-4 py-2 border border-gray-200 dark:border-warm-border rounded-lg bg-gray-50 dark:bg-[#1C1F26] focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent transition"
				></textarea>
			</div>

			<div
				v-if="error"
				class="p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded-lg text-sm"
			>
				{{ error }}
			</div>

			<button
				type="submit"
				:disabled="loading || rating === 0"
				class="w-full py-3 bg-[#D4AF37] text-black rounded-lg font-bold hover:bg-[#c9a432] disabled:opacity-50 transition flex items-center justify-center gap-2"
			>
				<span v-if="loading" class="material-symbols-outlined animate-spin">refresh</span>
				{{ loading ? 'Submitting...' : 'Submit Feedback' }}
			</button>
		</form>
	</div>
</template>

<script setup>
import { ref } from 'vue'
import { call } from 'frappe-ui'

const props = defineProps({
	repair: {
		type: Object,
		required: true,
	},
	authToken: {
		type: String,
		required: true,
	},
})

const rating = ref(0)
const hoverRating = ref(0)
const comments = ref('')
const loading = ref(false)
const error = ref(null)
const submitted = ref(props.repair.review_rating > 0)

async function submitReview() {
	if (rating.value === 0) return

	loading.value = true
	error.value = null

	try {
		const res = await call('zevar_core.api.repair_customer_portal.submit_repair_review', {
			auth_token: props.authToken,
			repair_order: props.repair.name,
			rating: rating.value,
			comments: comments.value,
		})

		if (res.success) {
			submitted.value = true
		} else {
			error.value = res.message || 'Failed to submit review'
		}
	} catch (e) {
		console.error('Review error:', e)
		error.value = e.message || 'An error occurred while submitting review'
	} finally {
		loading.value = false
	}
}
</script>
