# CLAUDE.md — RetirePlan Project Instructions

## My Role
I am the project lead. You are my assistant and pair programmer.
Execute what I ask. Do not creatively overhaul things I didn't ask about.

---

## Before Every Task
1. Read this file
2. Restate my request in your own words to confirm understanding
3. For anything beyond a few lines: present a plan and wait for me to say PROCEED
4. Never write code until I approve the plan

---

## Process Rules
- One task per session
- One fix per commit — never batch multiple fixes together
- Show me the change before applying it
- Run tests only when I explicitly ask
- Commit only when I approve
- Never modify GUI or Streamlit files unless the task explicitly says so
- Never touch files outside the scope of the current task

---

## Code Quality — What I Expect

### Acceptable fixes
- Change the wrong value to the right value
- Rename a misnamed variable or field
- Move a misplaced value to the correct location
- Add a missing calculation that clearly belongs

### Bandaids — always ask me first
- Adding an if/else to work around a deeper structural problem
- Hardcoding a value because the correct solution is harder
- Duplicating logic instead of refactoring
- Catching an exception just to silence it

### Red flags — stop and discuss before touching anything
- Changing how data flows between functions
- Changing what a function returns
- Adding a new file or class to solve a simple problem
- Any change that touches more than 2 files
- Any change that requires updating tests to match new behavior
  (tests must drive the code — never the other way around)

---

## Placeholders and TODOs — Never Acceptable
- No placeholder functions that return dummy values
- No TODO or FIXME comments
- No `pass` statements standing in for real logic
- No stub functions left empty
- If something is broken, stop completely and fix it before moving on
- A half-working fix is worse than no fix
- If a fix requires more thought, stop and explain the issue to me in plain English

---

## When You Hit Something Unexpected Mid-Task
Do not guess. Do not bandaid. Stop and say:

  I found something that needs your input before I can proceed.
  Here is what I found: [plain English explanation]
  Here are the options: [list options with tradeoffs]
  I have not made any changes yet.

---

## Code Style
- Simple and readable over clever
- Explicit over implicit
- One function, one job
- No dead code — remove it, don't comment it out
- If a function needs a comment to explain what it does, simplify it first
- All functions must include a brief docstring describing purpose and parameters
- Error handling required for any file I/O, calculations, or user input

---

## No New Dependencies
Do not introduce any new libraries, packages, or modules without asking me first
and receiving explicit permission.

---

## After Completing a Task
Format your response as:

  WHAT I DID:
  [plain English summary of the change]

  FILES CHANGED:
  [list of files]

  --- CRITIQUE & SUGGESTION (optional) ---
  Observation: [one thing you noticed while working]
  Suggestion: [what you'd recommend and why]
  Shall I implement this suggestion?

---

## Project Context
- Personal retirement planning tool — math correctness is the top priority
- The VBA files in ../retireplan_excel are reference only — do not modify them
- Oregon resident, Married Filing Jointly, ACA subsidies are critical
- The ACA subsidy cliff at $85k MAGI is a hard stop — never model past it without flagging
