# 📐 Setup Guide Template — Authoring Instructions

> **Purpose:** This document defines the **exact structure, formatting rules, and conventions** for writing step-by-step practical setup/installation guides within this repository. Any future LLM chat instance or human contributor must follow these instructions verbatim to ensure all guides share a uniform, professional, academic-practical format.

---

## 1. File Naming Convention

- Use **lowercase kebab-case** with a descriptive name: `<topic>-setup.md`
- Examples: `tailscale-vpn-setup.md`, `nginx-reverse-proxy-setup.md`, `docker-compose-setup.md`
- The filename must clearly indicate the subject of the guide at a glance

---

## 2. Document Structure — Required Sections (in order)

Every guide **must** contain the following sections in this exact order. Do not skip or reorder them.

### 2.1 Title Block

```markdown
# <Descriptive Title of What Is Being Set Up>
### Module: <Parent Module Name> — Practical Guide

> **Objective:** <One-sentence summary of what the reader will achieve by the end of this guide. Be specific — mention the end-state, not just the tool name.>
```

**Rules:**
- The `#` H1 heading is the guide title — clear, specific, includes the platform/OS if relevant
- The `###` H3 subtitle names the module this guide belongs to (e.g. "VPS Management", "Network Security")
- The blockquote `Objective` is mandatory and must describe the **outcome**, not the process
  - ✅ Good: *"Configure an Nginx reverse proxy serving HTTPS traffic for a Node.js application on Ubuntu 22.04"*
  - ❌ Bad: *"Set up Nginx"*

---

### 2.2 Table of Contents

```markdown
---

## 📋 Table of Contents

| Step | Title | Description |
|------|-------|-------------|
| [Step 1](#step-1--<anchor>) | <Step Title> | <One-line description> |
| [Step 2](#step-2--<anchor>) | <Step Title> | <One-line description> |
| ... | ... | ... |
```

**Rules:**
- Use a **markdown table** with exactly three columns: `Step`, `Title`, `Description`
- The `Step` column must contain an **anchor link** in the format `[Step N](#step-n--<kebab-case-title>)`
  - Anchor format: lowercase, spaces → hyphens, special characters (e.g. `&`) → double hyphens `--`
  - Example: `## Step 5 — Fix UDP GRO & Persist It` → anchor is `#step-5--fix-udp-gro--persist-it`
- The `Description` column is a **one-line plain-English summary** (no jargon, no commands)
- Every step in the guide body must appear in this table — no exceptions
- Place a horizontal rule (`---`) before and after this section

---

### 2.3 Prerequisites

```markdown
## Prerequisites

Before you begin, ensure the following:

- ✅ <Prerequisite 1>
- ✅ <Prerequisite 2>
- ✅ <Prerequisite 3>

> **Note on <topic>:** <Any universal caveat, e.g. privilege requirements, network access, account signups.>
```

**Rules:**
- Use the ✅ emoji prefix for every checklist item
- Bold the **key noun** in each item (e.g. "You have **root SSH access**")
- Include a blockquote note if there is a universal caveat (e.g. "run as root", "requires internet access")
- If a prerequisite requires signing up for a service, include a hyperlink to the signup page
- End with a horizontal rule (`---`)

---

### 2.4 Step Sections (repeat for each step)

Each step is a `## Step N — <Title>` heading containing a fixed set of sub-sections. There are **two step types**: Command Steps and GUI/Manual Steps. Use the appropriate template.

#### 2.4.1 Command Step Template (for steps involving terminal commands)

```markdown
---

## Step N — <Step Title>

### What this does
<1–3 paragraphs explaining WHY this step is necessary and WHAT it accomplishes at a conceptual level. Write for someone who has never seen these commands before. Mention relevant background concepts (e.g. what IP forwarding is, what a swap file does). Bold key terms on first mention.>

> **<Optional contextual note>:** <edge cases, "who needs this?", version-specific caveats>

### Command(s)
```sh
<exact command(s) to run, one per line or logically grouped>
```

### Breakdown

| <Column 1 Header> | <Column 2 Header> | ... |
|--------------------|-------------------|-----|
| `<command or parameter>` | <explanation> | ... |

### Verify
```sh
<verification command>
```
<1–2 lines describing expected output, optionally with an example output block:>
```
<expected output>
```
```

**Rules for "What this does":**
- This is the **most important section** — it must fully explain the *why*
- Do not just paraphrase the command; explain the **underlying concept**
- Bold key technical terms on first mention (e.g. **swap file**, **IP forwarding**)
- If a step is optional or conditional, add a blockquote note (e.g. `> **Who needs this?** ...`)

**Rules for "Command(s)":**
- Use the heading `### Command` (singular) if there is exactly one command
- Use `### Commands` (plural) if there are multiple commands
- Always use ` ```sh ` as the code fence language
- If multiple commands are logically grouped (e.g. create + permission + activate), keep them in one fenced block
- If a step contains conceptually distinct groups, you may use inline `# comments` inside the code fence to separate them
- Reproduce commands **exactly** as they should be typed — no placeholders like `<your-username>` unless the user truly must substitute a value, in which case wrap placeholders in `< >` angle brackets and explain them in the Breakdown table

**Rules for "Breakdown":**
- Use a **markdown table** — every distinct command, flag, parameter, or non-obvious value gets its own row
- The first column header should be contextually appropriate:
  - `Command` / `Explanation` — when each row is a full command
  - `Part` / `Explanation` — when dissecting one compound command
  - `Parameter` / `Value` / `Explanation` — when explaining configuration parameters
  - `Command / Parameter` / `Explanation` — when mixing commands and flags
- Wrap commands and flags in backticks in the first column
- Explanations must be self-contained sentences — a reader should understand the row without reading the others
- If a command or parameter has a non-obvious default or alternative, mention it (e.g. "Strict mode (`1`) would drop packets; `2` allows them")
- Add a blockquote note below the table for deeper context if warranted (e.g. `> **Why this path?** ...`)

**Rules for "Verify":**
- Include a verification step **whenever the step produces a checkable result**
- Show the **exact command** to run in a ` ```sh ` block
- Below it, describe what the output should look like in 1–2 lines
- If the expected output is multi-line, include it in a plain ` ``` ` code block (no language tag)
- If a step has no verifiable output (e.g. "open a URL"), omit this section entirely — do not write "N/A"

---

#### 2.4.2 GUI / Manual Step Template (for steps involving a web UI, app, or physical action)

```markdown
---

## Step N — <Step Title>

### What this does
<1–3 paragraphs explaining WHY this step is necessary and what the user is accomplishing. Same depth as command steps.>

### Steps

1. **<Action verb>** <target> (include URLs as hyperlinks if applicable)

2. **<Action verb>** <what to click/select/toggle>

3. **<Action verb>** <what to click/select/toggle>

4. **<Action verb>** <final action>

### <Success Indicator / Visual Confirmation>
<Describe what the user should see to confirm the step worked — a badge, a colour change, a status message, etc.>
- <Indicator 1>
- <Indicator 2> (optional)
```

**Rules:**
- Each numbered item begins with a **bold action verb** (Navigate, Click, Select, Toggle, Tap, Open, etc.)
- Include **parenthetical platform hints** if the UI differs across platforms (e.g. "on iOS: ... ; on Android: ...")
- If a URL is involved, make it a clickable markdown hyperlink
- End with a "Success Indicator" or "Visual Confirmation" sub-section — the user must know what success looks like

---

### 2.5 Quick Reference — Full Command Sequence

```markdown
---

## 🔁 Quick Reference — Full Command Sequence

For future reference, here is the complete ordered command sequence (<brief context on how to use it>):

```sh
# 1. <Step 1 title>
<command(s)>

# 2. <Step 2 title>
<command(s)>

# ...

# N. <Step N title>
<command(s)>
# → <any manual follow-up actions as comments>
```
```

**Rules:**
- This section is a **single continuous ` ```sh ` code block** containing every command from the guide, in order
- Each step is separated by a blank line and prefixed with a `# N. <step title>` comment
- GUI-only steps (no commands) are represented by a comment line: `# N. <title> → <brief instruction>`
- This section is for copy-paste convenience — it must be functionally complete (a reader should be able to SSH in and paste the whole block)

---

### 2.6 Troubleshooting

```markdown
---

## 🛠️ Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| <What the user observes> | <Root cause> | <Actionable fix — reference a specific Step if applicable> |
| ... | ... | ... |
```

**Rules:**
- Use a **three-column table**: `Symptom`, `Likely Cause`, `Fix`
- Include **at least 4–6 rows** covering the most common failure modes
- `Symptom` should describe what the user **sees or experiences** (error messages in backticks)
- `Fix` must be **actionable** — name the exact command or step number to re-run
- Place after the Quick Reference section

---

### 2.7 Footer

```markdown
---

*Guide version: <X.Y> — <short description of scope>*
```

- Start at version `1.0` for new guides
- Increment the minor version (`1.1`, `1.2`) for content updates; increment the major version (`2.0`) for restructures
- The short description is a plain-English scope reminder (e.g. "Alpine Linux / OpenRC / Tailscale exit node setup")

---

## 3. Formatting Rules — Universal

These rules apply to every section of every guide.

### 3.1 Horizontal Rules
- Place a `---` horizontal rule **between every major section** (between the ToC and Prerequisites, between Prerequisites and Step 1, between each Step, before Quick Reference, before Troubleshooting, before the Footer)

### 3.2 Headings
- `#` H1 — Document title only (exactly one per document)
- `##` H2 — Major sections: Table of Contents, Prerequisites, each Step, Quick Reference, Troubleshooting
- `###` H3 — Sub-sections within a step: "What this does", "Command(s)", "Breakdown", "Verify", "Steps", "Success Indicator"
- Never skip heading levels (e.g. no `##` → `####`)

### 3.3 Code Blocks
- All terminal commands use ` ```sh ` (not `bash`, not `shell`, not `text`)
- Expected output / non-executable text uses plain ` ``` ` (no language tag)
- Inline references to commands, flags, filenames, or values use single backticks: `` `command` ``

### 3.4 Emphasis & Formatting
- **Bold** — key terms on first mention, action verbs in GUI steps, emphasis on critical concepts
- *Italics* — technical term definitions, light emphasis
- `Backticks` — commands, flags, filenames, config values, parameter names
- ✅ emoji — prerequisites checklist only
- 📋 🔁 🛠️ emojis — section header accents (Table of Contents, Quick Reference, Troubleshooting respectively)

### 3.5 Blockquote Notes
- Use `>` blockquote for contextual notes, caveats, and tips
- Always bold the lead-in label: `> **Note:**`, `> **Important:**`, `> **Who needs this?**`, `> **Why <topic>?**`
- Do not stack multiple blockquotes consecutively — separate with body text

### 3.6 Tables
- Always include a header row and a separator row (`|---|`)
- Wrap commands/code in backticks within table cells
- Keep cell content concise — one sentence max per cell where possible

### 3.7 Line Spacing
- One blank line between every heading and its content
- One blank line between paragraphs
- No trailing whitespace on any line

---

## 4. Content Voice & Tone

- **Voice:** Academic-practical — instructional, precise, and thorough, but not dry. Write as if delivering a hands-on lab session.
- **Tense:** Use imperative mood for instructions ("Run the following command"), present tense for explanations ("This creates a swap file")
- **Audience:** Assume the reader can open a terminal and type commands, but do **not** assume they understand what the commands do. Every command must be explained.
- **Jargon:** Define technical terms on first use, either inline or in the Breakdown table. Never assume the reader knows an acronym.
- **No ambiguity:** Never write "you may want to" or "consider doing" — either include the step or don't. The guide must leave **zero room for interpretation**.

---

## 5. Checklist — Before Finalising a Guide

Use this checklist to self-audit before considering the guide complete:

- [ ] H1 title is specific and includes platform/OS
- [ ] Objective blockquote describes the end-state, not just the tool
- [ ] Table of Contents lists every step with working anchor links
- [ ] Prerequisites use ✅ bullets and bold key nouns
- [ ] Every command step has: What this does → Command(s) → Breakdown → Verify
- [ ] Every GUI step has: What this does → Steps (numbered, bold verbs) → Success Indicator
- [ ] Breakdown tables explain every command, flag, and non-obvious value
- [ ] "What this does" sections explain the *why*, not just the *what*
- [ ] Quick Reference contains all commands in a single copyable block
- [ ] Troubleshooting table has ≥ 4 rows with actionable fixes
- [ ] Horizontal rules separate every major section
- [ ] Code fences use ` ```sh ` for commands, plain ` ``` ` for output
- [ ] No placeholders without angle brackets and an explanation
- [ ] Footer version line is present

---

## 6. Full Skeleton — Copy-Paste Starter

Below is a blank skeleton that follows every rule above. Copy this into a new `.md` file and fill in the `< >` placeholders.

````markdown
# <Title Including Platform/OS>
### Module: <Module Name> — Practical Guide

> **Objective:** <One-sentence end-state description.>

---

## 📋 Table of Contents

| Step | Title | Description |
|------|-------|-------------|
| [Step 1](#step-1--<anchor>) | <Title> | <Description> |
| [Step 2](#step-2--<anchor>) | <Title> | <Description> |

---

## Prerequisites

Before you begin, ensure the following:

- ✅ <Prerequisite with **bold key noun**>
- ✅ <Prerequisite with **bold key noun**>

> **Note on <topic>:** <Universal caveat.>

---

## Step 1 — <Step Title>

### What this does
<Conceptual explanation.>

### Command(s)
```sh
<command>
```

### Breakdown

| Command | Explanation |
|---------|-------------|
| `<cmd>` | <explanation> |

### Verify
```sh
<verification command>
```
Expected output:
```
<output>
```

---

## Step 2 — <GUI Step Title>

### What this does
<Conceptual explanation.>

### Steps

1. **Navigate** to <URL or location>

2. **Click** <element>

3. **Select** <option>

### Success Indicator
- <What the user should see>

---

## 🔁 Quick Reference — Full Command Sequence

```sh
# 1. <Step 1>
<commands>

# 2. <Step 2>
# → <manual action>
```

---

## 🛠️ Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| <symptom> | <cause> | <fix> |

---

*Guide version: 1.0 — <scope description>*
````

---

*Template version: 1.0 — Universal setup guide authoring instructions*
