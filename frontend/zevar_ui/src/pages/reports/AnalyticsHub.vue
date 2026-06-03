<template>
	<AppLayout>
		<div class="hub">
			<header class="hub__header">
				<div class="flex flex-col gap-1 min-w-0 flex-1">
					<h1 class="premium-title !text-2xl">Analytics Hub</h1>
					<p class="text-gray-500 dark:text-gray-400 text-sm mt-1">
						Daily business at a glance
						<span v-if="asOfLabel" class="text-xs text-gray-400 dark:text-gray-500 ml-2">· As of {{ asOfLabel }}</span>
					</p>
				</div>
				<div class="flex items-center gap-2">
					<select v-model="store" class="h-9 px-3 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] text-xs text-gray-700 dark:text-gray-200 focus:ring-2 focus:ring-[#D4AF37] outline-none">
						<option value="">All Stores</option>
						<option v-for="s in stores" :key="s" :value="s">{{ s }}</option>
					</select>
					<button type="button" :disabled="store_loading" @click="refresh(true)" class="h-9 w-9 rounded-lg flex items-center justify-center border border-gray-200 dark:border-warm-border hover:border-[#D4AF37] text-gray-500 hover:text-[#D4AF37] disabled:opacity-50" aria-label="Refresh">
						<span class="material-symbols-outlined" :class="{ 'animate-spin': store_loading }">refresh</span>
					</button>
				</div>
			</header>

			<section class="hub__hero" aria-label="Daily metrics" @touchstart.passive="onHeroTouchStart" @touchend.passive="onHeroTouchEnd">
				<component
					v-for="card in heroCards"
					:key="card.key"
					:is="HERO_COMPONENT_MAP[card.key]"
					:data="heroDataFor(card.key)"
					@open="openCard(card.key)"
				/>
			</section>

			<section v-if="aiBrief" class="hub__ai-brief glass-tier-1" aria-label="AI daily brief">
				<div class="flex items-center gap-2 mb-1">
					<span class="px-1.5 py-0.5 rounded text-[10px] font-black uppercase tracking-wider bg-[color:var(--color-gold)]/15 text-[color:var(--color-gold)]">AI</span>
					<span class="text-[10px] font-mono text-gray-500">Today</span>
				</div>
				<p class="text-sm font-bold text-gray-900 dark:text-white">{{ aiBrief.headline || 'Today at a glance' }}</p>
				<p class="text-xs text-gray-700 dark:text-gray-300 mt-1">{{ aiBrief.body || '' }}</p>
			</section>

			<section v-if="alerts.length" class="hub__alerts" aria-label="Alerts">
				<div v-for="a in alerts" :key="a.key" class="glass-tier-1 hub__alert" @click="openCard(a.card)">
					<span class="material-symbols-outlined hub__alert-icon" :style="{ color: a.color }">{{ a.icon }}</span>
					<div class="flex-1 min-w-0">
						<div class="text-[10px] font-black uppercase tracking-wider text-gray-500">{{ a.label }}</div>
						<div class="text-xs font-bold text-gray-900 dark:text-white truncate">{{ a.detail }}</div>
					</div>
				</div>
			</section>

			<ModuleTabs :tabs="filteredTabs" :active="activeTab" @change="(k) => tabs.setTab(k)" />

			<section class="hub__tab">
				<component :is="currentTabComponent" />
			</section>
		</div>

		<HubDrawer v-if="drawer.isOpen.value" :open="drawer.isOpen.value" :title="drawer.current.value?.title || 'Detail'" @close="drawer.close()">
			<component :is="currentDrawerComponent" :payload="drawer.current.value?.payload" :kind="drawer.current.value?.kind" />
		</HubDrawer>
	</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import RevenueHeroCard from '@/components/analytics/RevenueHeroCard.vue'
import RepairHeroCard from '@/components/analytics/RepairHeroCard.vue'
import LayawayHeroCard from '@/components/analytics/LayawayHeroCard.vue'
import CashVarianceHeroCard from '@/components/analytics/CashVarianceHeroCard.vue'
import LowStockHeroCard from '@/components/analytics/LowStockHeroCard.vue'
import OverduePaymentsHeroCard from '@/components/analytics/OverduePaymentsHeroCard.vue'
import HoldQueueHeroCard from '@/components/analytics/HoldQueueHeroCard.vue'
import ModuleTabs from '@/components/analytics/ModuleTabs.vue'
import HubDrawer from '@/components/analytics/HubDrawer.vue'
import { useAnalyticsHubStore } from '@/stores/analyticsHub'
import { storeToRefs } from 'pinia'
import { useHubAlerts } from '@/composables/analytics/useHubAlerts'
import { useFilteredTabs, TAB_COMPONENT_MAP, DRAWER_COMPONENT_MAP } from '@/composables/analytics/useHubTabs'
import { useRoleAwareHero } from '@/composables/analytics/useRoleAwareHero'

const HERO_COMPONENT_MAP = {
	sales: RevenueHeroCard,
	repair: RepairHeroCard,
	layaway: LayawayHeroCard,
	cash_variance: CashVarianceHeroCard,
	low_stock: LowStockHeroCard,
	overdue_payments: OverduePaymentsHeroCard,
	hold_queue: HoldQueueHeroCard,
}

const hub = useAnalyticsHubStore()
const { tabs, drawer } = hub
const { hero, refreshing, selectedStore, loading, aiBrief, asOf, roleContext } = storeToRefs(hub)

const store = ref(selectedStore.value || '')
const stores = ref([])

const activeTab = computed(() => tabs.activeTab.value)
const store_loading = computed(() => loading.value || refreshing.value)
const asOfLabel = computed(() => {
	if (!asOf.value) return ''
	try { return new Date(asOf.value).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }) }
	catch { return '' }
})

const { cards: heroCards } = useRoleAwareHero(roleContext)
const { HUB_TABS: filteredTabs } = useFilteredTabs(roleContext)

function heroDataFor(key) {
	if (!hero.value) return {}
	if (key === 'low_stock') {
		return {
			total: Number(hero.value.low_stock?.total || 0),
			stockout: Number(hero.value.low_stock?.stockout || 0),
		}
	}
	return hero.value[key] || {}
}

const { alerts } = useHubAlerts(hero)
const currentTabComponent = computed(() => TAB_COMPONENT_MAP[activeTab.value] || TAB_COMPONENT_MAP.revenue)
const currentDrawerComponent = computed(() => DRAWER_COMPONENT_MAP[drawer.current.value?.kind] || null)

function openCard(key) { hub.openCardDrawer(key) }
function refresh(force = false) { hub.refresh(force) }

let touchStartX = 0
function onHeroTouchStart(e) { touchStartX = e.touches[0].clientX }
function onHeroTouchEnd(e) {
	const delta = e.changedTouches[0].clientX - touchStartX
	if (Math.abs(delta) < 50) return
	const el = document.querySelector('.hub__hero')
	if (!el) return
	const scrollAmt = el.clientWidth * 0.7
	el.scrollBy({ left: delta > 0 ? -scrollAmt : scrollAmt, behavior: 'smooth' })
}

watch(store, (v) => { selectedStore.value = v || null; hub.refresh(true) })
onMounted(() => hub.refresh())
</script>

<style scoped>
.hub { display: flex; flex-direction: column; gap: 16px; padding: 0; min-height: 100%; }
.hub__header { display: flex; align-items: center; gap: 12px; justify-content: space-between; }
.hub__hero { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }
@media (max-width: 1024px) { .hub__hero { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) {
	.hub__hero {
		display: flex;
		overflow-x: auto;
		scroll-snap-type: x mandatory;
		scrollbar-width: none;
		gap: 10px;
		padding-bottom: 4px;
	}
	.hub__hero::-webkit-scrollbar { display: none; }
	.hub__hero > * {
		min-width: 75vw;
		flex-shrink: 0;
		scroll-snap-align: center;
	}
}
.hub__ai-brief { padding: 14px 18px; border-radius: var(--radius-lg); }
.hub__alerts { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 8px; }
.hub__alert { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: var(--radius-md); cursor: pointer; transition: background var(--duration-fast) var(--ease-out); }
.hub__alert:hover { background: var(--bg-2); }
.hub__alert-icon { font-size: 20px; }
.hub__tab { padding: 4px 0 24px; }
</style>
