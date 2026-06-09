# Git Push/Pull & Branching Guide
### Module: Git Operations — Practical Guide

> **Objective:** Initialize the empty repository, push the workspace structure to main, and establish team workflows for cloning, pulling, and pushing to feature-specific branches.

---

## 📋 Table of Contents

| Step | Title | Description |
|------|-------|-------------|
| [Step 1](#step-1--initialize-and-push-workspace-structure-to-main) | Initialize and Push Workspace Structure to Main | Configure remote, add placeholder files to track folder structure, commit, and push to main. |
| [Step 2](#step-2--clone-the-repository) | Clone the Repository | Clone the repository for the first time on a developer machine. |
| [Step 3](#step-3--sync-and-update-with-main) | Sync and Update with Main | Safely pull the latest changes from the main branch to stay up to date. |
| [Step 4](#step-4--develop-and-push-to-role-specific-branches) | Develop and Push to Role-Specific Branches | Switch to dedicated feature branches and push changes to frontend, backend, or agent branches. |

---

## Prerequisites

Before you begin, ensure the following:

- ✅ You have **Git installed** locally on your machine.
- ✅ You have **Write access / Collaborator permissions** to the GitHub repository: `https://github.com/mynoveldownloads/superai-3-musketeres`.
- ✅ You have configured your **Git user credentials** (`git config --global user.name` and `git config --global user.email`).

> **Note on Authentication:** Modern GitHub requires Personal Access Tokens (PAT) or SSH keys for pushing. Ensure your credentials are authenticated.

---

## Step 1 — Initialize and Push Workspace Structure to Main

### What this does
Since Git does not track completely empty directories by default, we must create placeholder `.gitkeep` files in our empty directories (`agent/`, `backend/`, `frontend/`). Then, we configure the remote repository URL, stage all base files (including `.gitignore`), make the initial commit, and push them to the `main` branch. This populates the repository so the rest of the team can immediately use the folder structure.

### Commands
```sh
# 1. Create .gitkeep placeholder files in the empty folders
touch agent/.gitkeep backend/.gitkeep frontend/.gitkeep

# 2. Add the remote GitHub repository URL
git remote add origin https://github.com/mynoveldownloads/superai-3-musketeres

# 3. Stage all files including configuration and folders
git add .

# 4. Commit the initial folder structure
git commit -m "chore: initial workspace structure setup"

# 5. Rename the default branch to main (avoids master/main mismatch)
git branch -M main

# 6. Push the initial structure to the main branch
git push -u origin main
```

### Breakdown

| Command / Parameter | Explanation |
|---------------------|-------------|
| `touch <dir>/.gitkeep` | Creates a hidden empty file inside empty directories so Git tracks and preserves the folders. |
| `git remote add origin <URL>` | Configures a new remote link named `origin` pointing to the GitHub repository URL. |
| `git add .` | Stages all changes in the current directory (including the `.gitignore` file). |
| `git commit -m "<msg>"` | Records a snapshot of the staged files to the local repository history. |
| `git branch -M main` | Renames the current branch to `main` (required if Git initialized the default branch as `master`). |
| `git push -u origin main` | Pushes the commits to the remote `main` branch, and sets `origin/main` as the default upstream tracking branch. |

### Verify
```sh
git status
```
Expected output:
```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

---

## Step 2 — Clone the Repository

### What this does
This step is for developers joining the project who need to copy the remote repository onto their local machine. Cloning fetches all branch histories and checks out the base branch.

### Commands
```sh
# Clone the repository
git clone https://github.com/mynoveldownloads/superai-3-musketeres

# Navigate into the workspace directory
cd superai-3-musketeres
```

### Breakdown

| Command / Parameter | Explanation |
|---------------------|-------------|
| `git clone <URL>` | Copies the target GitHub repository and its commit history to your local machine. |
| `cd superai-3-musketeres` | Changes the working directory to the cloned repository folder. |

### Verify
```sh
git branch -a
```
Expected output:
```
* main
  remotes/origin/main
```

---

## Step 3 — Sync and Update with Main

### What this does
Before writing new code or merging features, developers must keep their local copies synced with `main` to prevent merge conflicts. This pulls downstream changes into the local working directory.

### Commands
```sh
# Switch to main branch
git checkout main

# Fetch and integrate remote updates
git pull origin main
```

### Breakdown

| Command / Parameter | Explanation |
|---------------------|-------------|
| `git checkout main` | Switches the local environment active branch to `main`. |
| `git pull origin main` | Fetches changes from origin's `main` branch and automatically merges them into your current local `main` branch. |

### Verify
```sh
git log -n 1
```
Expected output:
```
commit abc123xyz... (HEAD -> main, origin/main)
Author: Developer <dev@email.com>
Date:   ...
```

---

## Step 4 — Develop and Push to Role-Specific Branches

### What this does
To keep the codebase organized, developers must push to their respective feature branches instead of committing directly to `main`.
* **Frontend developers:** Push to `frontend-development`
* **Backend developers:** Push to `backend-development`
* **Agent developers:** Push to `agent-integration`

### Commands
```sh
# 1. Switch to your feature branch (creates it locally if it doesn't exist yet)
git checkout -b <branch-name>

# 2. Stage and commit your feature changes
git add .
git commit -m "feat: add feature details"

# 3. Push feature changes to the remote branch
git push -u origin <branch-name>
```

> **Who needs this?** Use the branch name corresponding to your role:
> * Frontend: `frontend-development`
> * Backend: `backend-development`
> * Agent: `agent-integration`

### Breakdown

| Command / Parameter | Explanation |
|---------------------|-------------|
| `git checkout -b <branch>` | Creates a new branch named `<branch>` and switches to it. |
| `git push -u origin <branch>` | Pushes commits to the remote branch, setting up the default upstream connection. |

### Verify
```sh
git branch
```
Expected output:
```
* frontend-development
  main
```

---

## 🔁 Quick Reference — Full Command Sequence

```sh
# 1. Initialize and Push Workspace Structure to Main (Run once on source local repo)
touch agent/.gitkeep backend/.gitkeep frontend/.gitkeep
git remote add origin https://github.com/mynoveldownloads/superai-3-musketeres
git add .
git commit -m "chore: initial workspace structure setup"
git branch -M main
git push -u origin main

# 2. Clone the Repository (For other team members)
git clone https://github.com/mynoveldownloads/superai-3-musketeres
cd superai-3-musketeres

# 3. Sync and Update with Main
git checkout main
git pull origin main

# 4. Develop and Push to Role-Specific Branches
# (Substitute <branch-name> with: frontend-development, backend-development, or agent-integration)
git checkout -b <branch-name>
git add .
git commit -m "feat: commit changes"
git push -u origin <branch-name>
```

---

## 🛠️ Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `error: src refspec main does not match any` | The local default branch name is `master` rather than `main`, so pushing to `main` fails. | Run `git branch -M main` to rename your local branch to `main`, and then run the push command again. |
| `[rejected] main -> main (fetch first) error: failed to push some refs to...` | The remote GitHub repository is not completely empty (e.g. contains a README.md or LICENSE) and has commits you do not have locally. | Run `git pull origin main --allow-unrelated-histories` to fetch and merge the remote commits, resolve any merge screens, and then run `git push -u origin main` again. |
| `fatal: remote origin already exists.` | A remote named `origin` is already defined in this local repository. | Run `git remote set-url origin https://github.com/mynoveldownloads/superai-3-musketeres` to update it. |
| `fatal: Pathspec 'agent/.gitkeep' did not match any files` | The directories don't exist yet in the local working directory. | Make sure the folders exist. Run `mkdir -p agent backend frontend` before running the `touch` commands. |
| `fatal: Authentication failed for...` | Incorrect credentials or GitHub personal access token (PAT) has expired. | Re-authenticate using a personal access token or set up Git SSH keys. |

---

*Guide version: 1.2 — Git branch management & initial project onboarding*
