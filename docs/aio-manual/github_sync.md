# Git Workflow Documentation
**Project:** superai-3-musketeres
**Branch:** `backend-development` → `main` → `agent-integration`
**Date:** 09 June 2026
**Author:** Caden Tang

***

## Overview

This documents the Git workflow used to:
1. Push backend work to `backend-development`
2. Sync local `main` with remote
3. Update `agent-integration` with the latest `main`

***

## Step 1 — Push Work to `backend-development`

Navigate to the project folder, sync with remote `main`, then commit and push your changes.

```bash
cd "C:\Users\Caden Tang\OneDrive - Ngee Ann Polytechnic\NextHackathon"

git fetch origin
git checkout backend-development
git merge origin/main
git add .
git commit -m "added blank agent.py, handover branch to raph"
git push -u origin backend-development
```

**What each command does:**
- `git fetch origin` — downloads the latest state of all remote branches without modifying local files
- `git checkout backend-development` — switches to the backend branch
- `git merge origin/main` — brings in the latest changes from remote `main` before pushing
- `git add .` — stages all changed files
- `git commit -m "..."` — saves a snapshot with a descriptive message
- `git push -u origin backend-development` — pushes to GitHub and sets upstream tracking

***

## Step 2 — Update Local `main`

After pushing backend work, switch to `main` and pull the latest remote changes.

```bash
git checkout main
git pull origin main
```

> ⚠️ **Note:** The merge of `backend-development` into `main` below is a **local-only** operation.
> To reflect this on GitHub, you must also run `git push origin main` afterwards.

```bash
git merge backend-development
git push origin main
```

***

## Step 3 — Sync `agent-integration` with `main`

Switch to the `agent-integration` branch and bring it up to date with the latest remote `main`.

```bash
git switch agent-integration
git fetch origin
git merge origin/main
```

**What each command does:**
- `git switch agent-integration` — switches to the agent-integration branch (creates local tracking branch if first time)
- `git fetch origin` — ensures you have the latest remote state
- `git merge origin/main` — merges the latest `main` into `agent-integration`

***

## Recommended Daily Workflow

Use this flow every time before starting work to avoid conflicts.

### For the developer pushing to a feature branch:

```bash
git checkout backend-development      # switch to your branch
git fetch origin                      # get latest remote state
git merge origin/main                 # sync with latest main
# ... make your changes ...
git add .
git commit -m "describe your changes"
git push origin backend-development
```

### For a teammate pulling the latest branch:

```bash
git fetch origin
git checkout backend-development
git pull origin backend-development
```

### For syncing any branch with `main`:

```bash
git fetch origin
git checkout <your-branch-name>
git merge origin/main
```

***

## Known Issues & Notes

### `git init` on an existing repo
Running `git init` inside a folder that already has a `.git/` directory simply reinitialises it — it does **not** reset or break anything, but it is unnecessary. You can safely skip it if the repo is already cloned.

### Directory deletion warnings on Windows (Git Bash)
```
Deletion of directory 'agent' failed. Should I try again? (y/n)
```
This is a **Windows file-locking issue**, not a Git error. It happens when a folder is open in File Explorer, VS Code, or another process during `git checkout`. To avoid it:
- Close File Explorer tabs pointing to those folders
- Close VS Code or reload the window before switching branches

### Local vs. Remote `main`
| Action | Updates local `main` | Updates GitHub `main` |
|---|---|---|
| `git pull origin main` | ✅ | ❌ |
| `git merge backend-development` | ✅ | ❌ |
| `git push origin main` | ❌ | ✅ |

Always push after merging if you want GitHub to reflect your local `main`.

***

## Branch Structure

```
main
├── backend-development   ← Caden's backend work (handed over to Raph)
├── agent-integration     ← Agent logic integration
└── frontend-development  ← Frontend work
```

***

## Summary of Commands Run (Session Log)

| # | Command | Purpose |
|---|---------|---------|
| 1 | `git fetch origin` | Fetch all remote branches |
| 2 | `git checkout backend-development` | Switch to backend branch |
| 3 | `git merge origin/main` | Sync backend with latest main |
| 4 | `git add .` | Stage all changes |
| 5 | `git commit -m "..."` | Commit backend files |
| 6 | `git push -u origin backend-development` | Push to GitHub |
| 7 | `git checkout main` | Switch to main |
| 8 | `git pull origin main` | Update local main from GitHub |
| 9 | `git merge backend-development` | Merge backend into local main |
| 10 | `git switch agent-integration` | Switch to agent branch |
| 11 | `git merge origin/main` | Sync agent branch with main |