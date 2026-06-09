# 📐 Update Changes Template — Authoring Instructions

> **Purpose:** This document defines the **exact format, rules, and conventions** for appending entries to `UPDATE_CHANGES.md`. Any future LLM chat instance or human contributor must follow these instructions to ensure the changelog remains consistent and useful as a review history.

---

## 1. Core Principles

- `UPDATE_CHANGES.md` is **append-only** — never edit or delete existing entries
- New entries are always appended **at the bottom**, immediately before the final `---` line
- Each entry represents a **single work session** (one conversation / one batch of related changes)
- The file serves the same purpose as a Git commit log — reviewers should be able to understand *what changed* and *why* without opening the changed files

---

## 2. Entry Format — Exact Template

Every new entry must follow this exact structure:

```markdown
## [YYYY-MM-DD — HH:MM UTC+<offset>]

**Author:** <author identifier>
**Files changed:**

- `<filename.ext>` — **<Action>**
  - <Change description 1>
  - <Change description 2>
  - <Change description 3>

- `<filename.ext>` — **<Action>**
  - <Change description>

---
```

---

## 3. Field-by-Field Rules

### 3.1 Timestamp Header

```markdown
## [YYYY-MM-DD — HH:MM UTC+<offset>]
```

- Use `##` H2 heading
- Date format: `YYYY-MM-DD` (ISO 8601)
- Time format: `HH:MM` (24-hour)
- Timezone: `UTC+<offset>` matching the user's local timezone (e.g. `UTC+8`, `UTC-5`, `UTC+0`)
- Wrap the full timestamp in square brackets `[ ]`
- Separate date and time with ` — ` (space–em dash–space)

**Example:**
```markdown
## [2026-05-03 — 19:35 UTC+8]
```

### 3.2 Author Line

```markdown
**Author:** <identifier>
```

- For LLM-authored changes: `LLM` (optionally add context like `LLM (initial setup)` or `LLM (bugfix)`)
- For human-authored changes: use the contributor's name or handle
- Bold the label, not the value

### 3.3 Files Changed

```markdown
**Files changed:**
```

- This label appears on its own line, directly after the Author line
- One blank line separates it from the first file entry

### 3.4 File Entries

```markdown
- `<filename.ext>` — **<Action>**
  - <Change description>
```

**Action keywords** (bold, one per file):

| Action | When to use |
|--------|------------|
| **Created** | File did not exist before this session |
| **Updated** | Content was modified within an existing file |
| **Deleted** | File was removed |
| **Renamed** | File was renamed (mention old name in the description) |
| **Moved** | File was relocated to a different directory |

**Rules for file entries:**
- Use backticks around the filename: `` `filename.ext` ``
- Separate filename and action with ` — ` (space–em dash–space)
- List files in the order they were changed during the session

### 3.5 Change Descriptions (bullet points under each file)

Each file entry must have **at least one** indented bullet point describing what changed. Follow these rules:

- Use 2-space indentation for the sub-bullets
- Start each bullet with a **verb in past tense** (Wrote, Added, Updated, Removed, Fixed, Renamed, Refactored, Moved)
- Be **specific** — mention section names, step numbers, parameter names, or line ranges where helpful
- Include **enough detail** that a reviewer can understand the scope without opening the file
- If a file was created, describe its full contents/purpose in the first bullet, then list key sections or components in subsequent bullets
- If a file was updated, describe only what changed — not the entire file contents
- Order bullets from most significant to least significant

**Good examples:**
```markdown
- `tailscale-vpn-setup.md` — **Updated**
  - Added Step 10 covering DNS configuration for split tunnelling
  - Updated Step 4 Breakdown table to clarify `rp_filter` loose mode vs strict mode
  - Fixed broken anchor link in Table of Contents for Step 7

- `nginx-proxy-setup.md` — **Created**
  - Wrote complete Nginx reverse proxy setup guide for Ubuntu 22.04
  - Contains 7 steps: install Nginx, configure server block, enable SSL via Certbot, test config, reload, verify, troubleshoot
  - Includes Quick Reference block and Troubleshooting table with 5 entries
```

**Bad examples (too vague):**
```markdown
- `tailscale-vpn-setup.md` — **Updated**
  - Made some changes
  - Fixed stuff

- `nginx-proxy-setup.md` — **Created**
  - New file
```

---

## 4. Multiple Files in One Entry

When multiple files are changed in the same session, list them all under the same timestamp header:

```markdown
## [2026-06-15 — 10:30 UTC+8]

**Author:** LLM
**Files changed:**

- `docker-compose-setup.md` — **Created**
  - Wrote Docker Compose deployment guide for a multi-container Node.js + PostgreSQL stack
  - Contains 6 steps with full command breakdowns and verification commands

- `UPDATE_CHANGES.md` — **Updated**
  - Appended entry for the creation of `docker-compose-setup.md`

- `misc-setup.md` — **Updated**
  - Added a cross-reference link to the new Docker Compose guide in the "Related Guides" section

---
```

---

## 5. Self-Referencing Rule

Every time you append an entry to `UPDATE_CHANGES.md`, the entry itself must include a bullet for `UPDATE_CHANGES.md`:

```markdown
- `UPDATE_CHANGES.md` — **Updated**
  - Appended changelog entry for <summary of what was done in this session>
```

This ensures the changelog documents its own growth.

---

## 6. Entry Placement

- Open `UPDATE_CHANGES.md`
- Scroll to the **very bottom** of the file
- The last line should be a `---` horizontal rule from the previous entry
- Append the new entry **after** that final `---`
- End the new entry with its own `---`

**Before appending:**
```markdown
  - <last bullet of previous entry>

---
```

**After appending:**
```markdown
  - <last bullet of previous entry>

---

## [2026-06-15 — 10:30 UTC+8]

**Author:** LLM
**Files changed:**

- `<file>` — **<Action>**
  - <description>

---
```

---

## 7. Checklist — Before Appending

- [ ] Timestamp uses the correct format `[YYYY-MM-DD — HH:MM UTC+<offset>]`
- [ ] Author line is present
- [ ] Every changed file is listed with the correct action keyword
- [ ] Every file entry has at least one descriptive bullet point
- [ ] Bullet points use past-tense verbs and are specific
- [ ] `UPDATE_CHANGES.md` itself is listed in the entry
- [ ] The entry is appended at the bottom, after the last `---`
- [ ] The entry ends with its own `---`

---

*Template version: 1.0 — Universal changelog authoring instructions*
