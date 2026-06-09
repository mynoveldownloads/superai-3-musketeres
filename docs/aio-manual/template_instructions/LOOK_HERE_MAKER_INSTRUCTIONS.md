# LOOK_HERE Maker — Authoring Instructions

> **Purpose:** This document is a system prompt for an LLM tasked with creating a `LOOK_HERE.md` file for a **new project or domain**. It codifies the exact structure, formatting patterns, and conventions used in `LOOK_HERE.md` files so that the output is structurally identical regardless of subject matter.

---

## 1. What Is a LOOK_HERE.md File?

A `LOOK_HERE.md` file is the **entry point** for any LLM (or human) entering a project workspace for the first time. It answers three questions:

1. **What is this project?** — Brief context and objective.
2. **What am I responsible for?** — Explicit enumeration of duties.
3. **What do I read, and in what order?** — A step-by-step workflow pipeline pointing to the right files.

It is **not** a template instruction file (those define formats). It is **not** a guide (those teach a reader to do something). It is an **onboarding briefing** — concise, directive, and unambiguous.

---

## 2. Document Structure — Required Sections (in order)

Every `LOOK_HERE.md` file must contain the following sections in this exact order:

| # | Section | Purpose |
|---|---------|---------|
| — | Title | H1: always `# LOOK HERE FIRST` |
| — | Opening line | One plaintext sentence telling the reader to read the entire file before doing anything |
| — | `---` | Horizontal rule |
| 1 | Context | Brief description of the project: what the directory contains, what the files are for, what conventions exist |
| 2 | Your Responsibilities | Numbered list of the LLM's duties in this workspace |
| 3 | Workflow | A visual step-by-step pipeline (ASCII box diagram) defining the exact order of operations for every task |
| 4 | File Reference | A table mapping every file in the directory to its purpose and when to read it |
| 5 | Strict Rules | A bullet list of non-negotiable constraints |
| — | Footer | Version line |

---

## 3. Section-by-Section Rules

### 3.1 Title and Opening Line

```markdown
# LOOK HERE FIRST

You are an LLM assistant entering a project workspace. Before doing anything, read this file completely. It tells you what this project is, what your responsibilities are, and exactly which files to consult before producing any output.
```

**Rules:**
- The H1 title is always `LOOK HERE FIRST` — do not customise it per project
- The opening line is a single plaintext paragraph (no formatting, no bullets) addressed directly to the LLM in second person
- It must tell the reader to read the entire file before acting
- Follow with a `---` horizontal rule

---

### 3.2 Context

```markdown
## Context

<2–4 paragraphs describing:>
<1. What this directory contains (types of files, their purpose)>
<2. What conventions/systems are in place (templates, changelogs, naming patterns)>
<3. Why those systems exist (consistency, reproducibility, auditability)>
```

**Rules:**
- Title: `## Context` (no emoji, no numbering)
- Keep it to **2–4 short paragraphs** — this is a briefing, not documentation
- Write in **present tense, third person** ("This directory contains...", "Each guide walks a reader through...")
- Mention every category of file that exists (guides, templates, changelogs, configs, etc.) but do not list individual filenames here — that is for the File Reference table
- Do not explain how to use the files — that is for the Workflow section
- End with a `---` horizontal rule

---

### 3.3 Your Responsibilities

```markdown
## Your Responsibilities

You have <N> responsibilities in this workspace. They apply to every task the user gives you, no matter the subject.

1. **<Responsibility 1>** <one-sentence explanation of when/how it applies>
2. **<Responsibility 2>** <one-sentence explanation>
3. **<Responsibility 3>** <one-sentence explanation>
```

**Rules:**
- Title: `## Your Responsibilities`
- Open with a one-line sentence stating how many responsibilities there are and that they are universal
- Use a **numbered list** (not bullets) — the order implies priority
- Bold the **responsibility name** at the start of each item, followed by a plain-text elaboration
- Keep to **2–5 items** — more than 5 dilutes focus
- Responsibilities must be **action-oriented** (generate, follow, document, validate) not passive (be aware of, understand)
- End with a `---` horizontal rule

---

### 3.4 Workflow

This is the **core section** of the file. It provides a visual, sequential pipeline that the LLM must follow for every task.

```markdown
## Workflow — Follow These Steps in Order

Every time the user gives you a task, execute the following pipeline from top to bottom. Do not skip steps.
```

Followed by an **ASCII box-and-arrow diagram** using this exact visual format:

```
START
  │
  ▼
┌─────────────────────────────────────────────────────┐
│  Step N — <Step title>                              │
│  <Line 1: what to do>                               │
│  <Line 2: additional detail or conditional logic>   │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  Step N+1 — <Step title>                            │
│  ...                                                │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
                      END
```

**Rules for the workflow diagram:**
- Wrap the entire diagram in a plain ` ``` ` code fence (no language tag)
- Start with `START` and end with `END`
- Each step is a **box** drawn with `┌─┐`, `│ │`, `└─┘` Unicode box-drawing characters
- Boxes are connected by `│` and `▼` characters
- Each box contains:
  - Line 1: `Step N — <Title>` (bold is not rendered in code blocks, so just use plain text)
  - Lines 2+: concise instructions, one per line, left-aligned inside the box
- Use `•` bullets inside boxes when listing conditional branches (e.g. "Creating a guide? → Read file X")
- Use `⚠` for critical warnings inside boxes (e.g. "THIS STEP IS NOT OPTIONAL")
- Keep box width consistent (approximately 55 characters of content)
- **Typical steps** (adapt to the project):
  1. Orient — list directory, read LOOK_HERE
  2. Understand — parse the user's request, determine task type
  3. Read templates — consult the relevant template instruction files
  4. Read examples — open an existing file to see the pattern in practice
  5. Execute — create or modify files
  6. Document — update the changelog (always the final step, always mandatory)

---

### 3.5 File Reference

```markdown
## File Reference

| File | What it is | When to read it |
|------|-----------|-----------------|
| `<filename>` | <one-line description> | <trigger condition> |
| ... | ... | ... |
```

**Rules:**
- Title: `## File Reference`
- Use a **three-column table**: `File`, `What it is`, `When to read it`
- List **every file** in the directory (or every file the LLM might interact with)
- Filenames in backticks
- "When to read it" must be a concrete trigger: "Before creating any guide", "After every session", "Always read first" — not vague phrases like "when needed"
- Order files by importance: LOOK_HERE first, then templates, then changelog, then content files
- End with a `---` horizontal rule

---

### 3.6 Strict Rules

```markdown
## Strict Rules

- **Never <prohibited action>.** <Consequence or rationale.>
- **Never <prohibited action>.** <Consequence or rationale.>
- **Never <prohibited action> without <required precondition>.** <Rationale.>
- **Always <required action>.** <Rationale.>
```

**Rules:**
- Title: `## Strict Rules`
- Use a **bullet list** (not numbered — these are constraints, not a sequence)
- Each bullet starts with **bold "Never"** or **bold "Always"**
- Follow the constraint with a period, then a consequence or rationale in a second sentence
- Include **4–7 items** covering:
  - File creation without reading the template first
  - Finishing a session without updating the changelog
  - Inventing new structures without a template
  - Modifying append-only files
  - Skipping explanatory sections in guides
- These rules are the "hard guardrails" — they must be absolute, not suggestions
- End with a `---` horizontal rule

---

### 3.7 Footer

```markdown
---

*LOOK_HERE version: <X.Y> — <project name> project onboarding*
```

**Rules:**
- Italicised version line
- Format: `LOOK_HERE version: <X.Y> — <project name> project onboarding`
- Start at `1.0` for new files

---

## 4. Formatting Rules — Universal

### 4.1 Horizontal Rules
- Place `---` after the opening line, and between every `##` section

### 4.2 Headings
- `#` H1 — title only (`LOOK HERE FIRST`), exactly one
- `##` H2 — all major sections (Context, Your Responsibilities, Workflow, File Reference, Strict Rules)
- No `###` H3 headings — the file should be flat; depth lives in the template instruction files, not here

### 4.3 Code Blocks
- Use plain ` ``` ` (no language tag) for the workflow diagram
- Do not use code blocks anywhere else in the file — this is a plaintext-forward document

### 4.4 Emphasis
- **Bold** — responsibility names, "Never"/"Always" in strict rules, file references in prose
- `Backticks` — filenames only
- No italics in the body (reserved for the footer)
- No emojis except `⚠` inside workflow boxes

### 4.5 Tables
- One table only: the File Reference table
- Three columns: `File`, `What it is`, `When to read it`

### 4.6 Tone
- **Direct and commanding** — second person ("You are an LLM assistant", "Read this file", "Do not skip steps")
- **Concise** — every sentence earns its place; no filler, no background essays
- **Unambiguous** — no "should", "consider", "you might want to"; only "must", "always", "never", "do not"

---

## 5. Process — How to Create a LOOK_HERE.md for a New Project

1. **Survey the directory.** List all files. Categorise them: content files, template instructions, changelogs, configs, other.

2. **Identify the project's purpose.** What does this directory help someone do? Write 1–2 sentences capturing the objective.

3. **Identify the LLM's responsibilities.** Based on the types of files present, what will the LLM be asked to do? (Create guides? Append logs? Generate reports? Update configs?)

4. **Map the workflow.** For a typical task, what files must be read and in what order? What is the final mandatory step? Build the pipeline as a sequence of boxes.

5. **Catalogue all files.** Fill in the File Reference table — every file, its role, and its read trigger.

6. **Extract the hard rules.** What must never happen? What must always happen? Write 4–7 absolute constraints.

7. **Assemble the file** following the section order in Section 2 of this document.

8. **Self-audit** against the checklist in Section 6 below.

---

## 6. Checklist — Before Finalising a LOOK_HERE.md

- [ ] H1 title is `LOOK HERE FIRST`
- [ ] Opening line tells the reader to read the entire file before acting
- [ ] Context section is 2–4 paragraphs and covers all file categories
- [ ] Responsibilities section uses a numbered list with bold action-oriented names
- [ ] Workflow diagram uses ASCII box-drawing characters inside a plain code fence
- [ ] Workflow starts with `START` and ends with `END`
- [ ] Every workflow step has a title and at least one instruction line
- [ ] The final workflow step is always "update the changelog" and is marked as mandatory
- [ ] File Reference table lists every file with a concrete read trigger
- [ ] Strict Rules section has 4–7 bullets starting with bold "Never" or "Always"
- [ ] No `###` headings are used — the file is flat
- [ ] No emojis appear except `⚠` inside workflow boxes
- [ ] Footer version line is present
- [ ] `---` horizontal rules separate every section

---

*Template version: 1.0 — Universal LOOK_HERE.md authoring instructions*
