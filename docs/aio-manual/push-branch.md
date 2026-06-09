# Git Branch Workflow: `backend-development`

**Repository:** https://github.com/mynoveldownloads/superai-3-musketeres

---

## For the Pusher — Push to `backend-development`

### Step 1 — Clone the repository *(skip if already cloned)*

```bash
git clone https://github.com/mynoveldownloads/superai-3-musketeres.git
cd superai-3-musketeres
```

### Step 2 — Switch to `backend-development`

```bash
git checkout backend-development
```

> If the branch isn't tracked locally yet:
> ```bash
> git checkout -b backend-development origin/backend-development
> ```

### Step 3 — Stage and commit your changes

```bash
git add .
git commit -m "your commit message here"
```

### Step 4 — Push to remote

```bash
git push origin backend-development
```

> **First-time push only** — set upstream tracking so future `git push` works without arguments:
> ```bash
> git push -u origin backend-development
> ```

---

## For Team Members — Pull & Sync

### Step 1 — Clone the repository *(skip if already cloned)*

```bash
git clone https://github.com/mynoveldownloads/superai-3-musketeres.git
cd superai-3-musketeres
```

### Step 2 — Fetch all remote branches

```bash
git fetch origin
```

### Step 3 — Switch to `backend-development`

```bash
git checkout backend-development
```

> If the branch doesn't exist locally yet:
> ```bash
> git checkout -b backend-development origin/backend-development
> ```

### Step 4 — Pull latest changes

```bash
git pull origin backend-development
```

---

## Ongoing Workflow (Both Members)

Always sync before starting new work to avoid merge conflicts:

```bash
git checkout backend-development
git pull origin backend-development

# ... make your changes ...

git add .
git commit -m "describe your changes"
git push origin backend-development
```

### Resolving Merge Conflicts

If `git pull` flags conflicts:

1. Open the affected files — Git marks conflicts with `<<<<<<<`, `=======`, and `>>>>>>>` markers
2. Edit the files to resolve the conflict
3. Stage and finalize the merge:

```bash
git add .
git commit -m "resolve merge conflict"
```

