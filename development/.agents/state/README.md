# State Freezing Protocol

Implementation of "State Freezing and Injection" pattern for AI agent accuracy.

Based on: https://medium.com/@tinholt/how-to-make-ai-agents-accurate-stop-treating-memory-like-chat-history-40eb8e0ea437

## The Problem

AI agents degrade over long sessions because:
- Chat history becomes polluted with derivation noise (failed attempts, corrections, stack traces)
- Models prioritize recent tokens (noisy) over earlier instructions (axioms)
- Rules become suggestions, architecture fades, decisions get re-decided

## The Solution

**Stop treating conversation as memory. Treat state as code.**

### Three-Layer Model

```
┌─────────────────────────────────────┐
│  1. CONSTITUTION (Immutable)        │
│     - Axioms, architecture, rules   │
│     - Rarely changes                │
├─────────────────────────────────────┤
│  2. DECISIONS (Append-Only)         │
│     - Decision log with IDs         │
│     - Grows over time               │
├─────────────────────────────────────┤
│  3. CURRENT STATE (Reset Each Time) │
│     - Active goal, plan, risks      │
│     - Changes constantly            │
└─────────────────────────────────────┘
```

## File Structure

```
.agents/state/
├── constitution.md          # Immutable axioms
├── decisions.md             # Append-only decision log
├── current.md               # Active session state
├── README.md                # This file
├── templates/               # Templates for new entries
│   └── session-start.md
└── archived/                # Old decisions/current states
    └── decisions-2026-03-01.md
```

## Quick Start

### Starting a Session

1. Read the three state files:
   ```bash
   cat .agents/state/constitution.md
   cat .agents/state/decisions.md
   cat .agents/state/current.md
   ```

2. Paste into your first message with the task description

3. Tell the agent: "You are operating under STATE FREEZING protocol"

### Ending a Session

1. Update `current.md` - mark tasks complete
2. Add decisions to `decisions.md` if any were made
3. Run: `./.agents/scripts/state-snapshot.sh "What you accomplished"`

## Principles

1. **State as code, not conversation** - Don't rely on chat history
2. **Axioms over preferences** - Constitution rules are absolute
3. **Compiled artifact** - State is prepared, not derived
4. **Reset = Accuracy** - Fresh session + state block = senior engineer
5. **Correctness over creativity** - Agents need constraints, not stories

## Workflows

See `.agents/workflows/`:
- `state-inject.md` - How to start a session
- `state-snapshot.md` - How to end a session

## Key Insight

> "Intelligence is cheap. Coherence is not."

Agents don't hallucinate because they're weak. They hallucinate because we force them to reason over polluted context. State Freezing gives them clean, explicit constraints to operate under.
