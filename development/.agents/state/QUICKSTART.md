---
description: Daily quick reference for State Freezing
---

# State Freezing - Quickstart

## The Problem
AI forgets rules after long chats. This fixes it by giving AI fresh rules each session.

## Files
- **constitution.md** - Rules that never change (security, architecture)
- **decisions.md** - Important choices (DEC-001, DEC-002...)
- **current.md** - What you're working on today

---

## Daily Routine

### Morning (5 min)

1. **Check current.md**
   ```bash
   cat .agents/state/current.md
   ```

2. **New task? Archive old**
   ```bash
   cp .agents/state/current.md .agents/state/archived/current-$(date +%Y%m%d).md
   ```
   Then edit current.md with new goal.

3. **Start AI chat, paste:**
   ```
   [Paste constitution.md]
   [Paste last 2-3 decisions]
   [Paste current.md]
   
   TASK: [what to do today]
   ```

### During Day (2 min each)

Update current.md when:
- Task done → Mark `[x]`
- New file touched → Add to Working Set
- Made decision → Add to decisions.md

Tell AI: "Updated state - X done"

### Evening (2 min)

```bash
./.agents/scripts/state-snapshot.sh "what you did"
```

---

## Real Example (Your POS Project)

### Scenario: Adding barcode search to POS

**current.md before:**
```markdown
Goal: Improve POS search
Plan:
- [x] Add name search
- [ ] Add barcode search  ← Doing this today

Working Set:
- POS.vue
- POSProductModal.vue
```

**You paste to AI:**
```markdown
[constitution pasted here]

[DEC-001, DEC-002 pasted here]

[current.md pasted here]

TASK: Add barcode search to POSProductModal.vue
```

**AI knows:**
- Project uses Vue 3 + Pinia
- API calls go through utilities
- Files are in frontend/zevar_ui/src/
- You're working on POSProductModal.vue

**After 1 hour:**

You edit current.md:
```markdown
Plan:
- [x] Add name search
- [x] Add barcode search
- [ ] Test both modes

Working Set:
- POS.vue
- POSProductModal.vue
- api.py  ← Added this
```

Tell AI: "State updated. Continue with testing."

**End of day:**
```bash
./.agents/scripts/state-snapshot.sh "Added barcode search to POS"
```

---

## Commands

```bash
# View state
cat .agents/state/current.md

# Edit state
vim .agents/state/current.md

# Archive old
mv .agents/state/current.md .agents/state/archived/current-$(date +%Y%m%d).md

# Commit
./.agents/scripts/state-snapshot.sh "description"
```

---

## When to Update What

| File | When | Example |
|------|------|---------|
| constitution.md | Rules change | "We now use TypeScript" |
| decisions.md | Made a choice | "DEC-005: Using Pinia" |
| current.md | Every 30-60 min | Task done, new file touched |

---

## Red Flags

| If AI... | Fix by... |
|----------|-----------|
| Suggests wrong pattern | Check constitution.md is current |
| Contradicts earlier work | Add decision to decisions.md |
| Asks "which file?" | Update Working Set in current.md |

---

## Time Cost
- Setup: 5 min morning
- Updates: 2 min × 3 = 6 min
- Commit: 2 min evening
- **Total: ~13 min/day**
