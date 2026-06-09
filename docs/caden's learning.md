# Git Bash branch commands

## Change branches

```bash
git branch
git switch main
```

Create and switch to a new branch:

```bash
git switch -c new-branch
```

## Update your branch with the latest `main`

### Merge `main` into your branch

```bash
git fetch origin
git switch branch-123
git merge origin/main
```

If there are conflicts:

```bash
git add .
git commit -m "Merge main into branch-123 and resolve conflicts"
```

Push the updated branch:

```bash
git push origin branch-123
```

### Rebase your branch onto `main`

```bash
git fetch origin
git switch branch-123
git rebase origin/main
```

If there are conflicts:

```bash
git add .
git rebase --continue
```

Push after rebasing:

```bash
git push origin branch-123
```

### Force your branch to exactly match `main` (discard branch-only commits)

```bash
git fetch origin
git switch branch-123
git branch --force branch-123 origin/main
git reset --hard HEAD
```

## Push your branch and create a PR/MR into `main`

Update your branch first:

```bash
git fetch origin
git switch branch-123
git merge origin/main
```

Then push it:

```bash
git push -u origin branch-123
```

Then on GitHub:

1. Open the repository.
2. Go to **Pull requests**.
3. Click **New pull request**.
4. Set **base** = `main` and **compare** = `branch-123`.
5. Create the pull request and merge it.

## Update your local `main` after merge

```bash
git switch main
git fetch origin
git merge origin/main
```

Or force local `main` to exactly match remote `main`:

```bash
git switch main
git fetch origin
git reset --hard origin/main
```