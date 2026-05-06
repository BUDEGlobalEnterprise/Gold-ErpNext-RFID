<template>
	<div class="ai-product" @click="$emit('click', product)">
		<div class="ai-product__image">
			<img v-if="product.image" :src="product.image" :alt="product.item_name" />
			<div v-else class="ai-product__placeholder">
				<svg
					width="24"
					height="24"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="1.5"
				>
					<rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
					<circle cx="8.5" cy="8.5" r="1.5" />
					<polyline points="21 15 16 10 5 21" />
				</svg>
			</div>
		</div>
		<div class="ai-product__info">
			<h4 class="ai-product__name">{{ product.item_name }}</h4>
			<div class="ai-product__tags">
				<span v-if="product.metal" class="ai-tag">{{ product.metal }}</span>
				<span v-if="product.purity" class="ai-tag">{{ product.purity }}</span>
				<span v-if="product.jewelry_type" class="ai-tag ai-tag--primary">{{
					product.jewelry_type
				}}</span>
			</div>
			<div class="ai-product__footer">
				<span v-if="product.msrp" class="ai-product__price"
					>${{ product.msrp.toLocaleString() }}</span
				>
				<span
					class="ai-product__stock"
					:class="{ 'ai-product__stock--low': product.stock_qty <= 2 }"
				>
					{{ product.stock_qty > 0 ? `${product.stock_qty} in stock` : 'Out of stock' }}
				</span>
			</div>
			<div class="ai-product__match">{{ (product.similarity * 100).toFixed(0) }}% match</div>
		</div>
	</div>
</template>

<script setup>
defineProps({
	product: {
		type: Object,
		required: true,
	},
})

defineEmits(['click'])
</script>

<style scoped>
.ai-product {
	display: flex;
	gap: 12px;
	padding: 10px;
	border-radius: 10px;
	cursor: pointer;
	transition: background 0.1s;
}

.ai-product:hover {
	background: #f3f4f6;
}

.dark .ai-product:hover {
	background: #374151;
}

.ai-product__image {
	width: 56px;
	height: 56px;
	border-radius: 8px;
	overflow: hidden;
	flex-shrink: 0;
}

.ai-product__image img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.ai-product__placeholder {
	width: 100%;
	height: 100%;
	display: flex;
	align-items: center;
	justify-content: center;
	background: #f3f4f6;
	color: #9ca3af;
	border-radius: 8px;
}

.ai-product__info {
	flex: 1;
	min-width: 0;
}

.ai-product__name {
	font-size: 13px;
	font-weight: 500;
	margin: 0 0 4px;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.ai-product__tags {
	display: flex;
	gap: 4px;
	flex-wrap: wrap;
	margin-bottom: 6px;
}

.ai-tag {
	padding: 1px 6px;
	border-radius: 4px;
	font-size: 10px;
	background: #f3f4f6;
	color: #4b5563;
}

.dark .ai-tag {
	background: #374151;
	color: #d1d5db;
}

.ai-tag--primary {
	background: #e0e7ff;
	color: #4338ca;
}

.dark .ai-tag--primary {
	background: #312e81;
	color: #a5b4fc;
}

.ai-product__footer {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.ai-product__price {
	font-size: 13px;
	font-weight: 600;
	color: #059669;
}

.ai-product__stock {
	font-size: 11px;
	color: #6b7280;
}

.ai-product__stock--low {
	color: #d97706;
}

.ai-product__match {
	font-size: 10px;
	color: #6366f1;
	margin-top: 2px;
}
</style>
