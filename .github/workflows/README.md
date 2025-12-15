# GitHub Actions Workflows

This project has two automated workflows:

## 1. Tests and Quality Checks (`tests.yml`)

**Triggers:**
- Every push to `master` or `main` branch
- Every pull request to `master` or `main` branch

**What it does:**

### Test Job
- Sets up Python 3.11
- Installs all dependencies
- Runs pytest with coverage
- Uploads coverage report to Codecov (if configured)

### Security Job
- Runs Bandit to scan for security vulnerabilities
- Runs Safety to check for vulnerable dependencies
- Generates security reports
- Uploads reports as artifacts

### Type Check Job
- Runs mypy for static type checking
- Ensures type hints are correct
- Catches type errors before deployment

**Viewing Results:**
- Go to your repository on GitHub
- Click "Actions" tab
- Click on any workflow run to see details
- Green checkmark = all passed
- Red X = something failed

## 2. Deploy to Toolforge (`deploy.yml`)

**Triggers:**
- Push to `master` branch
- Manual trigger via "workflow_dispatch"

**What it does:**
- SSHs into Toolforge
- Pulls latest code from git
- Installs dependencies
- Runs database migrations
- Restarts the web service

**Required Secrets:**
- `TOOLFORGE_USER` - Your Toolforge username
- `TOOLFORGE_SSH_KEY` - Your SSH private key

## How They Work Together

```
Push to GitHub
    ↓
Tests Workflow Runs
    ↓
├─ Unit Tests
├─ Security Checks
└─ Type Checking
    ↓
If on master branch
    ↓
Deploy Workflow Runs
    ↓
Deploy to Toolforge
```

## Setting Up Branch Protection

To prevent deployment if tests fail:

1. Go to repository Settings → Branches
2. Add rule for `master` branch
3. Enable "Require status checks to pass before merging"
4. Select: `test`, `security`, `typecheck`
5. Enable "Require branches to be up to date before merging"

Now merges to master will only happen if all checks pass!

## Local Testing Before Push

Run these commands before pushing to catch issues early:

```bash
# Run all checks locally
make all           # Linux/Mac
run-checks.bat     # Windows

# Or individually
pytest
bandit -r src/
safety check
mypy src/
```

## Viewing Workflow Logs

To see detailed logs when a workflow fails:

1. Go to GitHub repository
2. Click "Actions" tab
3. Click the failed workflow run
4. Click the failed job (e.g., "test", "security", "typecheck")
5. Expand the failed step to see error details

## Common Issues

### Tests fail on GitHub but pass locally
- Different Python version (workflows use 3.11)
- Missing environment variables
- Database differences (workflows use SQLite)

Solution: Check the workflow logs for exact error

### Security checks fail
- Bandit found a security issue in code
- Safety found vulnerable dependency

Solution: Fix the security issue or update the dependency

### Type checking fails
- Missing type hints
- Incorrect type annotations

Solution: Fix type errors or add to mypy.ini ignore list

## Optional: Code Coverage Badge

Add coverage badge to README.md:

1. Sign up at https://codecov.io
2. Connect your GitHub repository
3. Add `CODECOV_TOKEN` to repository secrets
4. Add badge to README:
   ```markdown
   [![codecov](https://codecov.io/gh/username/repo/branch/master/graph/badge.svg)](https://codecov.io/gh/username/repo)
   ```

## Optional: Status Badges

Add workflow status badges to README.md:

```markdown
![Tests](https://github.com/username/repo/actions/workflows/tests.yml/badge.svg)
![Deploy](https://github.com/username/repo/actions/workflows/deploy.yml/badge.svg)
```

Replace `username/repo` with your GitHub username and repository name.
