# Quick Actions Sidebar Implementation Plan
## For Employee & ESS (Employee Self Service) Roles

**Date:** 2026-05-04  
**Target Layout:** `tile-row-4` (4-button sidebar rhythm matching Dashboard.vue)

---

## 1. Feature Overview

Add a "Quick Actions" sidebar section (4 buttons in `tile-row-4` layout) for **Employee** and **Employee Self Service (ESS)** roles that provides fast access to key POS and customer operations. This appears in the left sidebar (AppShell.vue) for quick transactional access.

### Requested Buttons:
1. **Quick Sale** → `/pos` — "New transaction"
2. **Lookup Customer** → `/customers` — "Search or add"
3. **Clock In/Out** → `/employee-portal/#/attendance` — "Track shift"
4. **Create Quote** → `/quotes` — "New estimate"

---

## 2. Target Location

**File:** `frontend/zevar_ui/src/components/AppShell.vue`  
**Section:** Sidebar (left nav), after the main navigation sections, before Market Prices

Current sidebar structure in AppShell.vue:
- Operations section (Dashboard, POS Terminal, Inventory, Audit, Customers)
- Sales section (Sales History, Catalogues, Layaway)
- Services section (Repairs, Trade-Ins, Appraisals)
- Management section (Reports, Contacts, Support)

**New section to add:** "Quick Actions" — visible only for Employee & ESS roles.

---

## 3. Current Limitations & Gaps

### 3.1 Route / Path Issues
- **`/pos`** — Does NOT exist. Current POS route is `/terminal` (see Dashboard.vue line 54, AppShell.vue line 796).  
  **Action:** Either alias `/pos` → `/terminal` or use `/terminal` as the route.

- **`/quotes`** — Does NOT exist as a route in current app. Button in Dashboard.vue line 361 is `<router-link to="#">` (disabled). No quote creation functionality implemented.  
  **Action:** Need to create quotes module or use existing alternative (POS/Transactions may have quote capability).

- **`/employee-portal/#/attendance`** — External Frappe HR route (not within Zevar SPA). This links out of the Vue app to the Frappe employee portal.  
  **Action:** Keep as external link or create internal attendance tracking. Current app has `/employee-portal` links (AppShell.vue lines 365, 962) that open external.

- **`/customers`** — EXISTS ✅ (router-link in Dashboard.vue line 198, AppShell.vue line 811, Sidebar line 673).

### 3.2 Role-Based Visibility
- Current AppShell sidebar uses `canAccessReports()` for Reports visibility but has NO role checks for Employee/ESS specific sections.
- Dashboard.vue has Employee Portal section visible for: `['Employee', 'Employee Self Service', 'Sales Associate']` (lines 78-86).
- **Need:** Role check utility to show Quick Actions only for Employee & ESS roles.

### 3.3 UI/UX Consistency
- Sidebar currently uses simple icon+text links (`tile-secondary` style not used).
- Dashboard uses `tile-row-4` with `tile-secondary` class (styled boxes).
- **Decision:** Use compact sidebar style (existing pattern) OR adopt `tile-secondary` box style (new for sidebar).

---

## 4. What Needs to Be Built

### 4.1 Core Implementation (AppShell.vue)

**A. Add Role Check Utility** (`utils/permissions.js` or new file)
```javascript
export function hasEmployeeRole() {
  const session = useSessionStore()
  return session.hasAnyRole(['Employee', 'Employee Self Service'])
}
```

**B. Add Quick Actions Section to Sidebar** (in `sidebarSections` computed)
```javascript
{
  label: 'Quick Actions',
  showForRoles: ['Employee', 'Employee Self Service'],
  items: [
    { to: '/terminal', label: 'Quick Sale', subtitle: 'New transaction', icon: '...' },
    { to: '/customers', label: 'Lookup Customer', subtitle: 'Search or add', icon: '...' },
    { to: '/employee-portal/#/attendance', label: 'Clock In/Out', subtitle: 'Track shift', icon: '...', external: true },
    { to: '/quotes', label: 'Create Quote', subtitle: 'New estimate', icon: '...', disabled: true }
  ]
}
```

**C. Filter Sections by Role** in computed property:
```javascript
const sidebarSections = computed(() => {
  const sections = [ /* ... existing sections ... */ ]
  
  // Add Quick Actions for Employee/ESS
  if (session.hasAnyRole(['Employee', 'Employee Self Service'])) {
    sections.unshift({ // Add to top
      label: 'Quick Actions',
      items: [ /* 4 items */ ]
    })
  }
  
  // ... rest of sections
})
```

**D. Styling for Enhanced Sidebar Items**
Option 1: Use existing simple link style (fastest)
Option 2: Add `tile-secondary` box style to sidebar items (requires CSS)

### 4.2 Backend/API Requirements

**A. Quotes Module**
- No `/quotes` route exists
- Need to check if Frappe Quotes doctype is available
- May need custom "Estimate" doctype for jewelry business
- **Workaround:** Link to POS with "Create Quote" mode, or disable button until implemented

**B. POS Terminal Enhancement**
- Current `/terminal` route exists (Dashboard → POS tile goes here)
- Consider adding route alias `/pos` → `/terminal` in router config

### 4.3 Frontend Components

**A. Sidebar Item Component Enhancement**
Current sidebar uses simple `<router-link>` with icon. Could enhance to show:
- Subtitle text (smaller, below label)
- Badge for "New" or status
- Disabled state for unimplemented features

**B. Role-Based Rendering**
Use session store to check roles:
```javascript
const session = useSessionStore()
const isEmployeeOrESS = computed(() => 
  session.hasAnyRole(['Employee', 'Employee Self Service'])
)
```

---

## 5. Implementation Priority

### Phase 1: Minimal Viable (1-2 days)
- [ ] Add Quick Actions section to AppShell.vue sidebar
- [ ] Use existing routes (`/terminal`, `/customers`, `/employee-portal`)
- [ ] Role-based visibility (Employee, ESS)
- [ ] Simple icon+text links (match existing sidebar style)
- [ ] Add `/pos` router alias to `/terminal`
- [ ] Create placeholder for `/quotes` (disabled with tooltip "Coming soon")

### Phase 2: Enhanced UI (2-3 days)
- [ ] Style sidebar items with `tile-secondary` box design
- [ ] Show subtitle text on hover or always
- [ ] Add badges (e.g., "New" for customers if recent)
- [ ] Smooth animations/transitions

### Phase 3: Full Functionality (3-5 days)
- [ ] Implement Quotes module (Estimate doctype)
- [ ] Create `/quotes` route and component
- [ ] Add "Create Estimate" from POS flow
- [ ] Internal attendance tracking (optional, instead of external portal)
- [ ] Add keyboard shortcuts (e.g., Alt+1 for Quick Sale)

### Phase 4: Polish (1-2 days)
- [ ] Mobile responsive (show in bottom nav or drawer)
- [ ] Tooltips on hover
- [ ] User customization (drag to reorder)
- [ ] Analytics tracking (which buttons used most)

---

## 6. Exact Changes Required

### File: `frontend/zevar_ui/src/components/AppShell.vue`

**Location 1:** Add role check after line 722 (script setup)
```javascript
import { useSessionStore } from '@/stores/session.js'
const session = useSessionStore()
const isQuickActionsVisible = computed(() => 
  session.hasAnyRole(['Employee', 'Employee Self Service'])
)
```

**Location 2:** Modify `sidebarSections` computed (around line 785)
```javascript
const sidebarSections = computed(() => {
  const sections = []
  
  // Quick Actions for Employee/ESS
  if (isQuickActionsVisible.value) {
    sections.push({
      label: 'Quick Actions',
      items: [
        {
          to: '/terminal',
          label: 'Quick Sale',
          subtitle: 'New transaction',
          icon: 'M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z'
        },
        {
          to: '/customers',
          label: 'Lookup Customer',
          subtitle: 'Search or add',
          icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z'
        },
        {
          to: '/employee-portal/#/attendance',
          label: 'Clock In/Out',
          subtitle: 'Track shift',
          icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
          external: true
        },
        {
          to: '/quotes',
          label: 'Create Quote',
          subtitle: 'New estimate',
          icon: 'M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z',
          disabled: true // Not implemented yet
        }
      ]
    })
  }
  
  // ... rest of existing sections
  sections.push(...existingSections)
  
  return sections
})
```

**Location 3:** Update template to show subtitle and handle external/disabled states (around line 80-120)
```vue
<router-link
  v-for="item in section.items"
  :key="item.to"
  :to="item.disabled ? '#' : item.to"
  :target="item.external ? '_blank' : null"
  :class="{
    'pointer-events-none opacity-50': item.disabled
  }"
  class="flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-300 group relative overflow-hidden"
  :class="isNavActive(item.to) && !item.disabled
    ? 'bg-gradient-to-r from-[#D4AF37]/20 to-transparent text-[#D4AF37]'
    : 'text-gray-600 dark:text-gray-400 hover:text-[#D4AF37] hover:bg-gradient-to-r hover:from-[#D4AF37]/10 hover:to-transparent'"
>
  <div class="relative z-10 flex items-center gap-4 w-full" :class="{ 'justify-center': isSidebarCollapsed }">
    <svg class="w-5 h-5 transition-colors shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon"/>
    </svg>
    <div v-if="!isSidebarCollapsed" class="flex-1 min-w-0">
      <span class="font-medium tracking-wide text-sm whitespace-nowrap block">{{ item.label }}</span>
      <span v-if="item.subtitle" class="text-[10px] text-gray-400 block truncate">{{ item.subtitle }}</span>
    </div>
    <div v-if="isSidebarCollapsed" class="absolute left-14 px-3 py-1 bg-gray-900 text-white text-[10px] font-bold rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 shadow-xl">
      {{ item.label }}<br><span class="text-[9px] opacity-75">{{ item.subtitle }}</span>
    </div>
    <span v-if="item.disabled" class="text-[9px] bg-gray-200 dark:bg-gray-700 px-1.5 rounded">Soon</span>
  </div>
</router-link>
```

### File: `frontend/zevar_ui/src/router/index.js` (or wherever routes are defined)

**Add alias for Quick Sale:**
```javascript
{
  path: '/pos',
  redirect: '/terminal'
}
```

### File: `frontend/zevar_ui/src/stores/session.js`

**Ensure `hasAnyRole` method exists:**
```javascript
hasAnyRole(roles) {
  if (!this.user?.roles) return false
  return roles.some(role => this.user.roles.includes(role))
}
```

### File: `frontend/zevar_ui/src/utils/permissions.js`

**Add export:**
```javascript
export function canAccessQuickActions(session) {
  return session.hasAnyRole(['Employee', 'Employee Self Service'])
}
```

---

## 7. Testing Plan

### Test Cases:

1. **Role Visibility**
   - Login as Employee → Quick Actions visible ✅
   - Login as ESS → Quick Actions visible ✅
   - Login as Admin → Quick Actions NOT visible ✅
   - Login as Sales Associate → Quick Actions NOT visible ✅

2. **Button Links**
   - Quick Sale → Opens `/terminal` ✅
   - Lookup Customer → Opens `/customers` ✅
   - Clock In/Out → Opens external HR portal ✅
   - Create Quote → Shows "Coming soon" disabled state ✅

3. **Responsive**
   - Desktop sidebar shows all 4 buttons ✅
   - Mobile drawer shows all 4 buttons ✅
   - Collapsed sidebar shows tooltips ✅

4. **UI Consistency**
   - Matches Dashboard tile-row-4 rhythm ✅
   - Hover states work ✅
   - Active state highlighting works ✅

---

## 8. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| `/quotes` route doesn't exist | High - feature incomplete | Disable button with "Coming soon" label |
| External HR portal breaks link | Medium | Add rel="noopener" and error handling |
| Role check fails silently | Medium | Add fallback visibility + console warning |
| Sidebar too crowded | Low | Use collapsible section or "More" dropdown |

---

## 9. Report Summary

### Current State:
- ✅ **`/customers`** route exists
- ✅ **`/terminal`** route exists (POS)
- ⚠️ **`/pos`** route does NOT exist (needs alias)
- ❌ **`/quotes`** route does NOT exist (needs implementation)
- ✅ **`/employee-portal`** links exist (external Frappe HR)

### Needed for Phase 1:
1. Router alias: `/pos` → `/terminal`
2. Quick Actions section in AppShell.vue sidebar
3. Role-based visibility (Employee, ESS only)
4. Disabled state for Create Quote with tooltip
5. Subtitle labels on sidebar items

### Effort Estimate:
- **Phase 1 (MVP):** 2-3 hours
- **Phase 2 (Enhanced UI):** 4-6 hours
- **Phase 3 (Full functionality):** 2-3 days
- **Phase 4 (Polish):** 1 day

### Dependencies:
- None (self-contained in frontend)
- Quotes module requires backend doctype creation (separate task)

---

## 10. Recommendations

1. **Start with Phase 1** — Provides immediate value with existing routes
2. **Use `/terminal` alias for Quick Sale** — Consistent with current codebase
3. **Add Create Quote to roadmap** — Essential for full jewelry business flow
4. **Consider internal attendance** — Reduce dependency on external Frappe HR portal
5. **A/B test placement** — Sidebar vs Dashboard tiles for employee roles

---

**Prepared by:** Kilo (AI Software Engineer)  
**Status:** Ready for implementation review