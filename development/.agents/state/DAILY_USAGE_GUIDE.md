---
description: Step-by-step daily usage guide for State Freezing
---

# Daily Usage Guide: State Freezing Step-by-Step

## Overview
This guide shows EXACTLY what to do each day when using State Freezing with AI agents.

---

## PART 1: Starting Your Work Day

### Step 1: Check Current State (2 minutes)

Open `.agents/state/current.md` and see where you left off.

```bash
cat .agents/state/current.md
```

**Look for:**
- What was the goal?
- What tasks were completed?
- What was the working set (files being edited)?

**Example Output:**
```
Current Goal: Implement login feature
Plan:
- [x] Create login API endpoint
- [x] Create login form component  
- [ ] Add validation
- [ ] Test the flow

Working Set:
- api.py
- LoginForm.vue
```

### Step 2: Decide: Continue or New Task?

**Option A: Continue Previous Work**
- Keep current.md as-is
- Proceed to Step 3

**Option B: Start New Task**
- Archive current.md
- Create new current.md

**Commands for Option B:**
```bash
# Archive old current state
cp .agents/state/current.md .agents/state/archived/current-$(date +%Y%m%d).md

# Edit current.md with new goal
# (Use your editor: vim, nano, or VS Code)
```

**New current.md template:**
```markdown
## Session Metadata
- **Session ID**: sess-20260303-002
- **Started**: 2026-03-03 10:00 UTC
- **Branch**: feature/new-feature-name

## Current Goal
Implement [specific feature name]

## Current Plan
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Working Set
- file1.py
- file2.vue

## Known Issues
- None yet
```

### Step 3: Open Your AI Chat

Create a new chat/session with your AI agent.

**Important:** Do NOT continue an old long chat. Start fresh.

### Step 4: Inject State (5 minutes)

**Copy and paste these files into your FIRST message:**

#### 4a. Start with the Directive
```markdown
# STATE INJECTION - NEW SESSION

## SYSTEM DIRECTIVE
You are operating under STATE FREEZING protocol.
- Do NOT treat conversation history as memory
- All ground truth is in the state files below
- Check these files before answering
- Update current.md as we work

---

## 1. CONSTITUTION (Immutable Rules)
```

#### 4b. Paste Constitution
```bash
cat .agents/state/constitution.md
```
Copy everything and paste it after "## 1. CONSTITUTION"

#### 4c. Add Divider + Decisions
```markdown
---

## 2. RECENT DECISIONS
```

```bash
cat .agents/state/decisions.md
```
Copy the last 2-3 decisions and paste them.

#### 4d. Add Divider + Current State
```markdown
---

## 3. CURRENT STATE
```

```bash
cat .agents/state/current.md
```
Copy everything and paste it.

#### 4e. Add Current Task
```markdown
---

## CURRENT TASK
[Describe what you need help with in this session]

Example:
"Continue implementing the login feature. We need to:
1. Add password validation
2. Handle error messages
3. Test the full flow"
```

### Step 5: Send and Start Working

Send the message. The AI now has:
- All the rules (constitution)
- Recent context (decisions)
- Current goal and plan (current state)
- Specific task for today

---

## PART 2: During Your Work Session

### Pattern: Work → Update State → Continue

#### Every 30-60 Minutes:

**1. Check Progress**
Ask yourself:
- Did we complete any tasks?
- Did we make architectural decisions?
- Are there new issues to note?

**2. Update current.md**

Open `.agents/state/current.md` in your editor:

```markdown
## Current Plan
- [x] Add password validation  ← Mark done
- [x] Handle error messages     ← Mark done
- [-] Test the full flow        ← In progress
- [ ] Add to decisions: Using bcrypt for passwords  ← New task
```

**3. If You Made a Decision**

Add to `.agents/state/decisions.md`:

```markdown
### DEC-002: Using bcrypt for password hashing
- **Date**: 2026-03-03
- **Context**: Need to choose password hashing method
- **Decision**: Use bcrypt with 12 rounds
- **Consequences**: All auth code uses bcrypt
- **Commit**: TBD
- **Author**: [Your name]
```

**4. Update Working Set**

If you touched new files, add them:
```markdown
## Working Set
- api.py
- LoginForm.vue
- auth.py              ← New
- test_login.py        ← New
```

**5. Tell the AI**

Send a quick message:
```markdown
State Update:
- Marked tasks X and Y complete
- Added DEC-002 about bcrypt
- Working set updated

Continue with testing the login flow.
```

---

## PART 3: Ending Your Work Day

### Step 1: Final State Update (5 minutes)

**1. Update current.md:**
- Mark all completed tasks `[x]`
- Note any incomplete tasks
- Update working set
- Add any new risks/issues

**Example:**
```markdown
## Current Plan
- [x] Add password validation
- [x] Handle error messages
- [x] Test the full flow
- [ ] Deploy to staging  ← Not done, move to tomorrow

## Known Issues
- Login is slow on mobile (need to investigate)
```

**2. Add Any New Decisions**

If you made architectural choices, add to decisions.md.

### Step 2: Commit State (1 minute)

```bash
./.agents/scripts/state-snapshot.sh "Completed login feature, deployed to dev"
```

Or manually:
```bash
git add .agents/state/
git commit -m "state[sess-20260303-002]: Completed login feature validation and testing"
```

### Step 3: Log Off

Your state is saved. Tomorrow you'll start fresh with all the context loaded.

---

## PART 4: Real Example Walkthrough

### Scenario: Building a POS System

#### Day 1 Morning

**You do:**
```bash
# Check current state (first time, mostly empty)
cat .agents/state/current.md

# It's empty, so create new
cat > .agents/state/current.md << 'CURRENT'
## Session Metadata
- **Session ID**: sess-20260304-001
- **Started**: 2026-03-04 09:00 UTC

## Current Goal
Build POS product search feature

## Current Plan
- [ ] Create product API endpoint
- [ ] Build search component
- [ ] Add filters

## Working Set
- frappe-bench/apps/zevar_core/zevar_core/api.py
- frappe-bench/apps/zevar_core/frontend/zevar_ui/src/components/POSProductSearch.vue
CURRENT
```

**You paste into AI:**
```markdown
[Constitution]
[Decisions - just DEC-001]
[Current State]

## CURRENT TASK
Build a POS product search feature that:
1. Searches products by name/barcode
2. Returns results in under 200ms
3. Shows product image, price, stock
```

**AI helps you code. You work together.**

#### Day 1 Mid-Day

**You update current.md:**
```markdown
- [x] Create product API endpoint
- [-] Build search component  ← In progress
- [ ] Add filters
```

**You tell AI:**
```markdown
State Update:
- API endpoint done
- Working on search component now
- Decided to use debounce (300ms) - adding to decisions
```

**You add to decisions.md:**
```markdown
### DEC-003: POS search uses 300ms debounce
- **Date**: 2026-03-04
- **Context**: Too many API calls while typing
- **Decision**: 300ms debounce on search input
- **Consequences**: POS search component, any future search
```

#### Day 1 End of Day

**You update current.md:**
```markdown
- [x] Create product API endpoint
- [x] Build search component
- [x] Add filters
```

**You commit:**
```bash
./.agents/scripts/state-snapshot.sh "Completed POS product search with debounce"
```

#### Day 2 Morning

**You do:**
```bash
cat .agents/state/current.md
```

**Shows:**
```markdown
All tasks complete. Goal achieved.
```

**You decide:** New task - fix bug from yesterday.

```bash
cp .agents/state/current.md .agents/state/archived/current-20260304.md

# Edit current.md with new goal
```

**You paste into AI:**
```markdown
[Constitution - same]
[Decisions - now includes DEC-003 about debounce]
[Current State - new bug fix goal]

## CURRENT TASK
Fix bug: Search shows out-of-stock items
```

**AI immediately knows:**
- POS search exists (from decisions)
- Uses debounce (from decisions)
- Code location (from working set)
- Doesn't suggest solutions that break existing rules

---

## PART 5: Quick Reference

### Commands Cheat Sheet

```bash
# View state
cat .agents/state/constitution.md
cat .agents/state/decisions.md
cat .agents/state/current.md

# Edit state
vim .agents/state/current.md
# or
code .agents/state/current.md

# Archive old current
mv .agents/state/current.md .agents/state/archived/current-$(date +%Y%m%d).md

# Commit state
./.agents/scripts/state-snapshot.sh "description"
# or
git add .agents/state/ && git commit -m "state[sess-id]: description"
```

### When to Update What

| File | When to Update | How Often |
|------|----------------|-----------|
| **constitution.md** | Rules change | Rarely (monthly) |
| **decisions.md** | Make architectural choice | As needed |
| **current.md** | Task complete/plan changes | Every 30-60 min |

### Red Flags (State Problems)

| Problem | Symptom | Fix |
|---------|---------|-----|
| Stale constitution | AI suggests old patterns | Update constitution.md |
| Missing decisions | AI contradicts earlier work | Add decision to log |
| Outdated current | Working on wrong files | Update working set |
| Long decisions | Too many to read | Archive old ones |

---

## Summary

**Every Day:**
1. Check current.md (2 min)
2. Start fresh AI chat
3. Paste constitution + decisions + current (5 min)
4. Add today's task
5. Work with AI
6. Update current.md every 30-60 min
7. Commit state at end of day (1 min)

**Total overhead: ~10 minutes per day**
**Time saved: ~30-60 minutes of "AI forgot the rules" debugging**
