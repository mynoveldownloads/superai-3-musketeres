# 📐 User Prompt Template — Authoring & Onboarding Guide

> **Purpose:** This document is an **onboarding guide for human users** on how to construct highly effective, structured, and repeatable prompts for LLM agents working in this repository. It deconstructs an unstructured task request into a modular, reliable framework using `USER_PROMPT.md`.

---

## 1. Introduction: Why Structure Matters

When you tell an LLM agent to do a complex task (like setting up a new module, writing a guide, creating an onboarding file, and updating a changelog), the agent needs explicit sequencing.

**Your original prompt structure was:**
> *inside "Template instructions" folder, read all \*_TEMPLATE... create git-version-control.md... read UPDATE_CHANGES... create LOOK_HERE... update changes made into UPDATE_CHANGES.md*

While effective, this was a "stream of consciousness." To make this repeatable for *any* future project (like Docker setup, Nginx config, etc.), we break it down into a structured pipeline. This ensures the agent never skips a step, applies templates perfectly, and documents its own work.

---

## 2. The Four Pillars of a Perfect Module Initialization Prompt

Every prompt to initialize a new module must contain four distinct phases. This is the pattern codified in `USER_PROMPT.md`.

### Phase 1: Context Loading
Before writing any code or markdown, the agent must load the rules of the repository into its active memory. By telling it to read the `*_TEMPLATE_INSTRUCTIONS.md` files, you guarantee the output will match the repository's strict aesthetic and structural standards.

### Phase 2: Primary Task Definition
This is where you define the unique work. You must provide:
- The target directory name.
- The desired filename.
- The core objective (what the file should accomplish).
- Specific technical constraints (e.g., "must use a GitHub access token", "default branch must be main").

### Phase 3: Infrastructure Generation
Every module in this repository requires standard infrastructure:
- An `UPDATE_CHANGES.md` file (the local changelog).
- A `LOOK_HERE.md` file (the onboarding briefing).
By explicitly telling the agent to read the maker instructions for these files, you ensure the new directory is immediately integrated into the repository's ecosystem.

### Phase 4: Self-Documentation
The final step is always documentation. The agent must append a record of all files it created during the session into the newly generated `UPDATE_CHANGES.md`.

---

## 3. How to Use the `USER_PROMPT.md` Template

As a user, you do not need to memorize the four pillars or write a massive paragraph from scratch every time. Instead, follow this standard operating procedure:

1. **Locate the Template:** Go to the `Template instructions` folder and find the `USER_PROMPT.md` file.
2. **Copy the Template:** Copy the `USER_PROMPT.md` file into the new target directory you want the agent to work on.
3. **Fill the Placeholders:** Open the copied file and replace the `<angle bracket>` placeholders with your specific requirements.
   - Example: Change `<Target Directory Name>` to `Docker Deployment`.
   - Example: Change `<main-file-name>.md` to `docker-compose-setup.md`.
4. **Trigger the Agent:** Copy the entirely filled-out text and paste it into the LLM chat interface.

---

## 4. Strict Rules for the User

To ensure the LLM agent behaves predictably, you (the human) must adhere to these rules when writing prompts:

- **Never ask the agent to invent structures.** Always reference existing template instructions.
- **Always enforce documentation.** Never remove the final instruction to update `UPDATE_CHANGES.md`.
- **Be explicit with constraints.** If you want a specific command or tool used, write it directly in the Primary Task Definition bullet points.
- **Do not group multiple primary tasks.** One prompt = one module initialization. Do not ask the agent to set up Git version control *and* Nginx in the same prompt.

---

## 5. Next Steps

If you are ready to start a new project:
1. Open `USER_PROMPT.md`.
2. Copy its contents.
3. Replace the placeholders for your new topic.
4. Send it to the agent.

---

*Template version: 1.0 — Human onboarding and prompt authoring instructions*
