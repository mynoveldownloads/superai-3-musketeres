# 📐 Template Maker — Meta-Authoring Instructions

> **Purpose:** This document is a **system prompt for an LLM** tasked with creating a new `*_TEMPLATE_INSTRUCTIONS.md` file. It codifies the universal patterns, structure, and formatting conventions that all template instruction files in this repository share. When a user asks you to create a template instruction document for any domain, follow every rule in this file to produce output that is structurally identical to existing template instructions — regardless of subject matter.

---

## 1. What Is a Template Instruction File?

A template instruction file is a **meta-document**. It does not perform a task itself — it tells a future LLM (or human) **exactly how to produce a specific type of `.md` file**. Think of it as a specification sheet: anyone reading it should be able to produce an output file that is structurally indistinguishable from one produced by the original author.

**The chain of abstraction:**

```
TEMPLATE_MAKER_INSTRUCTIONS.md  (you are here — tells you how to write template instructions)
        ↓ produces
*_TEMPLATE_INSTRUCTIONS.md      (tells a future LLM how to write a specific type of .md file)
        ↓ produces
*.md                            (the actual content file — a guide, a log, a report, etc.)
```

---

## 2. Common Structural Pattern

Every template instruction file follows this **exact section order**. Do not skip or reorder sections.

### Section Map

| # | Section | Purpose |
|---|---------|---------|
| — | **Title Block** | H1 title + purpose blockquote |
| 1 | **Foundational Rules** | File naming, core principles, or scope constraints |
| 2 | **Document Structure / Entry Format** | The ordered list of required sections or the exact format template for the target file |
| 3 | **Field-by-Field / Section-by-Section Rules** | Granular rules for every element, each in its own numbered subsection |
| 4 | **Formatting Rules** | Universal typographic and markdown conventions |
| 5 | **Content Voice & Tone** | Writing style, audience assumptions, tense, jargon policy |
| 6 | **Checklist** | Pre-finalisation self-audit items |
| 7 | **Skeleton / Full Example** | A ready-to-copy template with `< >` placeholders |
| — | **Footer** | Template version line |

> **Note:** Not every section applies to every document type. Some target files are simpler (e.g. a changelog has no "Voice & Tone" section because entries are terse). **Include a section only if it adds value.** However, you must always include: Title Block, Document Structure, Field-by-Field Rules, Checklist, and Footer. The others are conditional.

---

## 3. Section-by-Section Authoring Rules

### 3.1 Title Block

```markdown
# 📐 <Document Type> Template — Authoring Instructions

> **Purpose:** This document defines the **exact <structure|format|rules|conventions>** for <what the target file does>. Any future LLM chat instance or human contributor must follow these instructions <to ensure X>.
```

**Rules:**
- Always use the 📐 emoji prefix in the H1 title
- Title format: `<Document Type> Template — Authoring Instructions`
- The purpose blockquote must:
  - Bold the phrase "exact structure" / "exact format" / "exact rules" (whichever fits)
  - Name the target file explicitly (e.g. "for appending entries to `UPDATE_CHANGES.md`")
  - State the consequence of following the instructions (e.g. "to ensure all guides share a uniform format")
- End with a `---` horizontal rule

---

### 3.2 Foundational Rules

This is the first numbered `##` section. Its title and content depend on the target file type:

| Target file type | Section title | Content focus |
|-----------------|---------------|---------------|
| A file created from scratch each time | `File Naming Convention` | Naming pattern, examples, rationale |
| A file that is appended to over time | `Core Principles` | Append-only rule, entry scope, review purpose |
| A file with structural constraints | `Scope & Constraints` | What the file covers and what it does not |

**Rules:**
- Number it `## 1. <Title>`
- Use bullet points for each rule
- Bold the **key constraint** in each bullet
- Keep this section short — 3–6 bullets maximum

---

### 3.3 Document Structure / Entry Format

This is the second numbered `##` section. It presents the **big picture** of what the target file looks like.

**Rules:**
- Title it `## 2. Document Structure — Required Sections (in order)` for files with multiple sections, or `## 2. Entry Format — Exact Template` for files with a repeating entry pattern
- Provide the complete structure in a **fenced markdown code block** so the reader can see the skeleton at a glance
- Below the code block, state explicitly: "Every guide/entry **must** contain the following sections in this exact order. Do not skip or reorder them."
- If the target file has a fixed section order, list them here as a numbered list or table

---

### 3.4 Field-by-Field / Section-by-Section Rules

This is the **largest section** of the template instruction file. It breaks down every element from Section 3.3 into its own numbered subsection with granular rules.

**Rules:**
- Number it `## 3. Field-by-Field Rules` or `## 3. Section-by-Section Rules` (whichever label fits)
- Create a `### 3.N <Element Name>` subsection for every distinct element
- Each subsection must contain:
  1. A **fenced markdown code block** showing the exact syntax/format for that element
  2. A **bullet list of rules** governing that element
  3. At least one **example** (good example, and optionally a bad example for contrast)
- Use tables when comparing options, actions, or keywords (e.g. action keywords like Created/Updated/Deleted)
- Bold the lead keyword in each rule bullet

**Pattern for each subsection:**

```markdown
### 3.N <Element Name>

```markdown
<exact format for this element>
```

- <Rule 1 — bold the key constraint>
- <Rule 2>
- <Rule 3>

**Example:**
```markdown
<concrete filled-in example>
```
```

---

### 3.5 Formatting Rules (conditional)

Include this section when the target file uses diverse markdown features (headings, code blocks, tables, blockquotes, emphasis). Omit it for simple files where formatting is self-evident from the examples.

**Rules:**
- Number it one higher than the previous section (e.g. `## 4. Formatting Rules — Universal` if Field-by-Field was `## 3`)
- Break into subsections by formatting category:
  - `### N.1 Horizontal Rules`
  - `### N.2 Headings`
  - `### N.3 Code Blocks`
  - `### N.4 Emphasis & Formatting`
  - `### N.5 Blockquote Notes`
  - `### N.6 Tables`
  - `### N.7 Line Spacing`
- Only include subsections relevant to the target file
- Each subsection is a short bullet list (2–5 bullets)

---

### 3.6 Content Voice & Tone (conditional)

Include this section when the target file contains prose (e.g. guides, tutorials, documentation). Omit it for structured-data files (e.g. changelogs, config files).

**Rules:**
- Number it sequentially after the previous section
- Cover these dimensions in bullet points:
  - **Voice** — overall register (e.g. academic-practical, conversational, terse)
  - **Tense** — imperative for instructions, present for explanations, past for descriptions
  - **Audience** — what knowledge level to assume
  - **Jargon** — define-on-first-use policy
  - **Ambiguity** — zero-tolerance policy (never "you may want to")

---

### 3.7 Checklist

Every template instruction file **must** include a pre-finalisation checklist.

**Rules:**
- Title: `## N. Checklist — Before Finalising` (or `Before Appending` for append-type files)
- Use markdown checkbox syntax: `- [ ] <item>`
- Each item corresponds to one major rule from the document
- Order from most structural (title, sections) to most granular (formatting, spacing)
- Include **6–16 items** — enough to catch all common mistakes, few enough to actually use

---

### 3.8 Skeleton / Full Example (conditional but strongly recommended)

Include this section when the target file has a complex multi-section structure. It gives the reader a ready-to-fill template.

**Rules:**
- Title: `## N. Full Skeleton — Copy-Paste Starter`
- Wrap the entire skeleton in a **four-backtick fenced block** (` ```` markdown ... ```` `) so that internal code fences render correctly
- Use `< >` angle-bracket placeholders for every variable element
- The skeleton must be **structurally complete** — a reader should be able to copy it, fill in placeholders, and have a valid file

---

### 3.9 Footer

```markdown
---

*Template version: <X.Y> — <one-line scope description>*
```

**Rules:**
- Always present as the last line of the file
- Italicised, preceded by a `---`
- Start at version `1.0`
- Scope description should be generic (e.g. "Universal setup guide authoring instructions", not "Tailscale VPN guide instructions")

---

## 4. Formatting Rules — Universal (apply to the template instruction file itself)

### 4.1 Horizontal Rules
- Place `---` between the title block and Section 1, and between every subsequent `##` section

### 4.2 Headings
- `#` H1 — document title only (exactly one)
- `##` H2 — numbered top-level sections: `## 1. ...`, `## 2. ...`, etc.
- `###` H3 — subsections within a `##` section: `### 3.1 ...`, `### 3.2 ...`, etc.
- `####` H4 — sub-subsections within a `###` (use sparingly, only when a subsection has genuinely distinct sub-parts)

### 4.3 Numbering
- All `##` sections are numbered sequentially starting from `1`
- All `###` subsections use dot notation matching their parent: `3.1`, `3.2`, `3.3`, etc.
- Numbering must be continuous — no gaps

### 4.4 Code Blocks
- Use ` ```markdown ` for showing the format/syntax of the target file
- Use plain ` ``` ` (no language tag) for generic examples
- Use four backticks ` ```` ` for skeletons that contain internal code fences
- Never use ` ```sh ` inside a template instruction file (that is for the target files themselves)

### 4.5 Emphasis
- **Bold** — key constraints, rule keywords, labels in blockquote notes
- *Italics* — light emphasis, definitions
- `Backticks` — filenames, format tokens, field names, markdown syntax elements

### 4.6 Tables
- Use tables for comparing options, listing keywords, or mapping conditions to actions
- Always include header and separator rows
- Keep cell content to one sentence maximum

### 4.7 Blockquote Notes
- Use `>` blockquotes for important caveats or clarifications
- Bold the lead-in: `> **Note:**`, `> **Important:**`, `> **Why?**`
- Maximum one blockquote per section — do not stack them

### 4.8 Line Spacing
- One blank line between every heading and its content
- One blank line between paragraphs and between bullet groups
- No trailing whitespace

---

## 5. Content Voice & Tone (for the template instruction file itself)

- **Voice:** Authoritative and prescriptive — you are writing a specification, not a suggestion
- **Tense:** Imperative for rules ("Use a markdown table", "Include at least 4 items"), present tense for explanations ("This section defines...")
- **Audience:** The reader is an LLM or an experienced technical writer. Assume they understand markdown syntax but not your specific conventions.
- **Precision:** Every rule must be unambiguous. Use "must", "always", "never" — avoid "should", "consider", "you might want to"
- **Domain neutrality:** Never reference a specific tool, OS, service, or project in the rules. Use generic examples or `<placeholders>`.

---

## 6. Process — How to Create a New Template Instruction File

When the user asks you to create a `*_TEMPLATE_INSTRUCTIONS.md` file, follow this workflow:

1. **Identify the target file type.** What kind of `.md` file will the template instruct someone to create? (e.g. a setup guide, a changelog, a runbook, a meeting notes file, a design doc)

2. **Identify or create an exemplar.** Either the user will provide an existing example of the target file, or you must create one first. You cannot write a template instruction file without a concrete example to reverse-engineer.

3. **Analyse the exemplar.** Extract:
   - The ordered list of sections
   - The heading hierarchy
   - Repeating patterns (e.g. every step has the same sub-sections)
   - Formatting conventions (code fences, tables, blockquotes, emphasis)
   - Voice and tone
   - Any constraints (append-only, version numbering, naming conventions)

4. **Map to the Section Map (Section 2 of this document).** Assign each extracted pattern to the appropriate section: Title Block, Foundational Rules, Document Structure, Field-by-Field Rules, Formatting Rules, Voice & Tone, Checklist, Skeleton.

5. **Write the template instruction file** following every rule in this document.

6. **Self-audit** against the checklist in Section 7 below.

7. **Update `UPDATE_CHANGES.md`** per the instructions in `UPDATE_CHANGES_TEMPLATE_INSTRUCTIONS.md`.

---

## 7. Checklist — Before Finalising a Template Instruction File

- [ ] H1 title uses 📐 emoji and follows the `<Type> Template — Authoring Instructions` format
- [ ] Purpose blockquote names the target file and states the consequence of following instructions
- [ ] All `##` sections are numbered sequentially
- [ ] All `###` subsections use dot notation matching their parent
- [ ] Every element of the target file has its own subsection in the Field-by-Field section
- [ ] Every subsection includes: format code block + rule bullets + example
- [ ] Tables are used for comparisons and keyword lists
- [ ] Formatting Rules section covers all markdown features used in the target file
- [ ] Checklist section has 6–16 actionable items
- [ ] Skeleton (if included) is wrapped in four-backtick fences and uses `< >` placeholders
- [ ] No domain-specific references appear in the rules (only in examples)
- [ ] Footer version line is present and uses the correct format
- [ ] `---` horizontal rules separate every `##` section
- [ ] Voice is prescriptive throughout — no "should", "consider", "might"

---

*Template version: 1.0 — Universal meta-instructions for creating template instruction files*
