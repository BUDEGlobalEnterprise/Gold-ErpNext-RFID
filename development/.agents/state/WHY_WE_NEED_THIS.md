---
description: Simple explanation of State Freezing for the team
---

# Why We Need State Freezing (Simple Explanation)

## The Problem (An Analogy)

Imagine you're teaching someone to build a house. You start with clear rules:
- "Use concrete for the foundation"
- "Walls go up after foundation"
- "Never skip the inspection"

But as you work together for hours, the conversation gets messy:
- "Wait, let's try wood for foundation... no, back to concrete"
- "Actually, put walls first, we'll fix it later"
- "Oops that broke, let's try again"
- "Did we say concrete? I meant steel... or maybe concrete"

By hour 5, the person you're teaching is confused. They start:
- Forgetting the foundation rules
- Making up their own (wrong) rules
- Confidently suggesting bad ideas
- Breaking things that worked before

This is what happens to AI agents in long coding sessions.

---

## Why AI Agents "Get Dumber"

### What People Think Happens
"The AI model is getting tired/weak/degraded"

### What Actually Happens
The AI is drowning in **derivation noise**.

Think of an AI like a student with a notebook:
- It can only read the last 50 pages
- New pages are added constantly
- Early pages have the important rules
- Recent pages have corrections, mistakes, "oops", "let me fix that"

After 3 hours:
- Page 1: "Always validate user input" (forgotten)
- Page 47: "Maybe skip validation for now" (remembered)
- Page 48: "Actually validate it" (remembered)
- Page 49: "Oops broke something" (remembered)

The AI follows Page 47-49 because they're recent, even though Page 1 was the real rule.

This is **context pollution** - good signal (rules) drowned by noise (chat history).

---

## The Solution: State Freezing

### Instead of Chat History → Use State Files

**Old Way (Broken):**
```
You → AI: "Build login feature"
AI → You: "Here's code"
You → AI: "Oops, fix that bug"
AI → You: "Fixed"
[Repeat 50 times]

Later...
AI: "I forgot we use JWT"
AI: "I'll use sessions instead"
You: "NO! We decided JWT 2 hours ago!"
AI: "Sorry, I don't remember"
```

**New Way (State Freezing):**
```
You → AI: 
"[Paste rules from constitution.md]
Rules: Always use JWT, never sessions
[Current task: Build login]"

AI: "Using JWT as per rules"

[Session ends, state saved]

New Session:
You → AI:
"[Paste same rules]
Rules: Always use JWT, never sessions  
[Current task: Fix login bug]"

AI: "Still using JWT as per rules"
```

The AI doesn't "remember" - it follows explicit rules every time.

---

## The Three Files Explained

### 1. Constitution (The Rule Book)
**What:** Rules that never change
**Examples:**
- "Always validate user input"
- "Use JWT for auth"
- "Max 50 lines per function"

**Why:** Like a company's employee handbook. Everyone follows it.

### 2. Decisions (The Meeting Minutes)
**What:** Important choices we made
**Examples:**
- "DEC-042: We will use Pinia, not Vuex"
- "DEC-043: API rate limit is 100/minute"

**Why:** Like meeting notes. "Why did we choose this? Check the log."

### 3. Current State (The Whiteboard)
**What:** What we're working on right now
**Examples:**
- "Goal: Fix login bug"
- "Progress: 3 of 5 tasks done"
- "Working on: login.vue, auth.py"

**Why:** Like a whiteboard in an office. Wiped clean each session.

---

## Benefits

| Problem | Solution with State Freezing |
|---------|------------------------------|
| AI forgets rules after 2 hours | Rules are in constitution.md, pasted fresh each session |
| AI contradicts earlier decisions | Decisions are in decisions.md, referenced by ID |
| AI makes up wrong architecture | Constitution has project map and tech stack |
| AI confidence stays high while wrong | Explicit constraints > inferred from messy history |
| Hard to reproduce good sessions | Same state files = same starting point |

### Real Benefits

1. **Accuracy Doesn't Decay**
   - Session 1: AI is sharp
   - Session 10: AI is still sharp (same rules loaded)

2. **New Team Members**
   - Give them constitution.md = they know all the rules
   - No need to dig through 500 Slack messages

3. **Debugging Decisions**
   - "Why did we do this?" → Check decisions.md
   - "Who decided this?" → Check the DEC entry

4. **Consistency**
   - Same rules every session
   - No "I thought we said..." arguments

---

## Issues / Downsides

### 1. Stale State
**Problem:** State files get out of sync with code
**Example:** Constitution says "Use Vuex" but we switched to Pinia last month
**Fix:** 
- Tie state updates to git commits
- Review constitution monthly
- Update timestamp in file when changed

### 2. Over-Constitutionalization
**Problem:** Too many rules, AI loses flexibility
**Example:** 500 rules about every tiny detail
**Fix:**
- Only put axioms in constitution (never violate)
- Keep preferences in current.md (can change)
- Think "constitution, not scripture"

### 3. Extra Work
**Problem:** You have to maintain state files
**Example:** Update current.md, add decisions, commit
**Reality:**
- 5 minutes at end of session
- Saves 30 minutes of "Why did AI do that wrong?"
- Pays for itself quickly

### 4. Discipline Required
**Problem:** You might skip it when busy
**Example:** "I'll update decisions.md later" (never does)
**Fix:**
- Make it habit like git commit
- Script helps: `./state-snapshot.sh "description"`
- Do it before every break

---

## Simple Summary

| | Old Way (Chat) | New Way (State) |
|---|---|---|
| **Memory** | "Remember what I said 3 hours ago" | "Here are the rules, read them now" |
| **Accuracy** | Gets worse over time | Stays consistent |
| **Rules** | Become suggestions | Stay as axioms |
| **Debugging** | Dig through chat history | Check decisions.md |
| **Onboarding** | Explain everything again | Share constitution.md |

**Bottom Line:**
> Don't ask AI to remember. Give it the rules fresh every time.

**The Article's Main Point:**
> "Intelligence is cheap. Coherence is not."

Big AI models are smart. But they get confused when we give them messy chat history. State Freezing gives them clean, organized rules - and smart + organized beats smart + confused every time.
