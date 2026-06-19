---
name: flawless-theme-matching
description: Extract exact Tailwind CSS conventions from existing AppShell.vue before building new Vue components to ensure pixel-perfect theme match
source: auto-skill
extracted_at: '2026-06-19T06:21:50.895Z'
---

## Purpose

When building new Vue 3 + Pinia + Tailwind components for Zevar POS, you must first read the existing AppShell.vue and store files to extract the exact Tailwind CSS conventions used throughout the app. Never guess — always verify against real code.

## Procedure

### Step 1: Read AppShell.vue (CRITICAL FIRST STEP)

Before writing any component, read `frontend/zevar_ui/src/components/AppShell.vue` to extract:

- **Panel backgrounds**: `bg-white/70 dark:bg-warm-dark-950/80 backdrop-blur-md`
- **Header backgrounds**: `bg-white/70 dark:bg-warm-dark-950/80 backdrop-blur-md`
- **Primary accent (Gold)**: `#D4AF37` — used for buttons, active states, ring focus, highlights
- **Typography**: `.premium-title` class + `tracking-tighter` for titles; `text-[10px] font-black uppercase tracking-widest text-gray-500` for labels
- **Borders**: `border-gray-200 dark:border-warm-border/50`
- **Inputs**: `bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]`
- **Dark card backgrounds**: `#1E2022` for Kanban cards
- **Sidebar**: `bg-[#1E2022] dark:bg-warm-dark-950`
- **Dividers**: `border-gray-200 dark:border-warm-border/30`

### Step 2: Read Existing Stores

Read 1-2 existing store files to match patterns:
- `frontend/zevar_ui/src/stores/cart.js` — complex state management, localStorage persistence, frappe-ui `createResource`
- `frontend/zevar_ui/src/stores/quotes.js` — simpler store pattern with `createResource` for API calls
- `frontend/zevar_ui/src/stores/time.js` — reactive state with computed getters

**Key patterns to match**:
- Stores use `defineStore` from pinia with the options API (not setup)
- API calls use `createResource({ url: 'zevar_core.api.xxx.method', ... })` from frappe-ui
- Resources exposed via `.fetch()` for reads, `.submit()` for writes
- Computed values used for derived state (totals, summaries)

### Step 3: Read index.css for Global Styles

Read `frontend/zevar_ui/src/index.css` for:
- CSS custom properties (`--color-gold`, `--color-dark`, font families)
- Global classes (`.premium-card`, `.premium-title`, `.status-label`)
- Body/dark body gradients

### Step 4: Match Router Conventions

Read `frontend/zevar_ui/src/router.js` to understand:
- Route meta patterns (`requiresAuth: true`)
- Existing special-orders route exists at `/special-orders` pointing to `SpecialOrders.vue`

### Step 5: Build Components

Follow these conventions for every new component:

1. **File location**: `frontend/zevar_ui/src/components/<area>/` (create directory if needed)
2. **Template structure**: Wrap panels in the exact background pattern from Step 1
3. **Gold accent**: Only use `#D4AF37` (not `#CBA358` or others) for primary actions, focus rings, active states
4. **Typography hierarchy**: 
   - Page titles: `premium-title tracking-tighter text-2xl`
   - Section headers: `text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400`
   - Body labels: `text-xs font-medium`
5. **Inputs**: Always `bg-gray-50/50 dark:bg-warm-dark-900/50` with `focus:ring-2 focus:ring-[#D4AF37]`
6. **Dark mode**: Use Tailwind `dark:` variant for every color class — never assume light-only

## What NOT to Do

- Do not use system colors (`blue-500`, `green-500`, etc.) for primary actions — always use `#D4AF37` gold
- Do not use `border-gray-300` — use `border-gray-200 dark:border-warm-border/50`
- Do not guess API endpoints — grep existing stores for the `zevar_core.api` namespace pattern
- Do not create stores using Composition API (`setup()` style) — this project uses Options API with `defineStore`
- Do not add new CSS classes for theming — use only the established patterns from AppShell.vue
- Do not forget dark mode variants on any color-sensitive element
