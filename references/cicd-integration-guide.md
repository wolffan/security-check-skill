# CI/CD Integration Guide for Security-Check Skill

**Purpose:** Integrate security scanner into CI/CD pipelines to automatically check skills for security issues before installation or deployment.

**Scanner Exit Codes:**
- `0` = PASS (No security issues found)
- `1` = WARN (MEDIUM/LOW severity warnings found)
- `2` = FAIL (HIGH severity issues found)

---

## Quick Start

### Option 1: Fail on HIGH Severity (Recommended)

Block installation/commit when critical security issues are detected. MEDIUM/LOW warnings don't block pipeline.

### Option 2: Fail on HIGH + MEDIUM Severity (Strict)

Block installation/commit when HIGH or MEDIUM severity issues are detected. Only LOW severity doesn't block.

---

## GitHub Actions Integration

### Workflow: Fail on HIGH Severity (Recommended)

**File:** `.github/workflows/security-check.yml`

```yaml
name: Security Check

on:
  pull_request:
    paths:
      - 'skills/**'
      - '.github/workflows/**'
  push:
    branches: [main, develop]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          # Security scanner uses only stdlib, but Python 3.11 required
          pip3 install --upgrade pip

      - name: Run security scanner on changed skills
        run: |
          # Find all skill directories
          find skills -name "SKILL.md" -type f | while read skill_path; do
            skill_dir=$(dirname "$skill_path")
            echo "🔍 Scanning: $skill_dir"

            # Run scanner
            python3 /path/to/security-check/scripts/scan_skill.py "$skill_dir" || echo "SCAN_FAILED"

            # Check exit code
            if [ $? -eq 2 ]; then
              echo "❌ HIGH severity issues found - blocking"
              exit 1
            elif [ $? -eq 1 ]; then
              echo "⚠️  MEDIUM/LOW warnings found - continuing"
            else
              echo "✅ No security issues found"
            fi
          done

      - name: Upload scan results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: security-scan-results
          path: security-scan-*.json
          retention-days: 30

      - name: Comment PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const scanResults = fs.readFileSync('security-scan-results.json', 'utf8');
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `## 🔒 Security Scan Results\n\n\`\`\`json\n${scanResults}\n\`\`\``
            });
```

---

### Workflow: Fail on HIGH + MEDIUM (Strict Mode)

**File:** `.github/workflows/security-check-strict.yml`

```yaml
name: Security Check (Strict)

on:
  pull_request:
    paths: ['skills/**']

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Scan all skills
        run: |
          for skill_dir in skills/*/; do
            if [ -f "$skill_dir/SKILL.md" ]; then
              python3 /path/to/security-check/scripts/scan_skill.py "$skill_dir"

              # Fail on HIGH or MEDIUM
              if [ $? -eq 2 ] || [ $? -eq 1 ]; then
                echo "🚫 Blocking installation: security issues found"
                exit 1
              fi
            fi
          done

      - name: Report status
        if: failure()
        run: |
          echo "::error::Security check failed. Review scan results in artifacts."
```

---

## GitLab CI Integration

### Basic GitLab CI (Fail on HIGH)

**File:** `.gitlab-ci.yml`

```yaml
stages:
  - security

security-scan:
  stage: security
  image: python:3.11
  before_script:
    - apt-get update && apt-get install -y python3
  script:
    - |
      FAILED=0
      WARNINGS=0

      # Scan all skill directories
      for skill_dir in skills/*/; do
        if [ -f "$skill_dir/SKILL.md" ]; then
          echo "🔍 Scanning: $skill_dir"

          # Run scanner
          python3 /path/to/security-check/scripts/scan_skill.py "$skill_dir"
          EXIT_CODE=$?

          # Track results
          if [ $EXIT_CODE -eq 2 ]; then
            echo "❌ HIGH severity in: $skill_dir"
            FAILED=1
          elif [ $EXIT_CODE -eq 1 ]; then
            echo "⚠️  Warnings in: $skill_dir"
            WARNINGS=1
          else
            echo "✅ Clean: $skill_dir"
          fi
        fi
      done

      # Fail pipeline if HIGH severity found
      if [ $FAILED -eq 1 ]; then
        echo "🚫 Pipeline failed: HIGH severity issues detected"
        exit 1
      elif [ $WARNINGS -eq 1 ]; then
        echo "⚠️  Pipeline passed with warnings"
      else
        echo "✅ All skills passed security check"
      fi

  artifacts:
    paths:
      - security-scan-*.json
    expire_in: 7 days
    when: always

  only:
    - merge_requests
    - main
```

---

### GitLab CI with Auto-Merge Blocking

**File:** `.gitlab-ci.yml`

```yaml
security-scan:
  stage: security
  image: python:3.11
  script:
    - |
      # Scan skills
      python3 /path/to/security-check/scripts/scan_skill.py skills/

      # Exit code 2 = HIGH severity - block merge
      if [ $? -eq 2 ]; then
        echo "🚫 BLOCKING: HIGH severity issues found"
        echo "To unblock, fix all HIGH severity issues and push changes."
        exit 1
      fi

  artifacts:
    reports:
      security: security-scan-results.json
```

---

## Pre-Commit Hook Integration

### Basic Pre-Commit Hook (Local Protection)

**File:** `.git/hooks/pre-commit`

```bash
#!/bin/bash
# Pre-commit security scanner for Clawdbot skills

echo "🔍 Running security scanner..."

# Run scanner on repository root
python3 /path/to/security-check/scripts/scan_skill.py .

EXIT_CODE=$?

# Check results
if [ $EXIT_CODE -eq 2 ]; then
  echo "❌ HIGH severity issues found"
  echo "🚫 Commit blocked"
  echo ""
  echo "Fix issues before committing:"
  echo "1. Review scanner output"
  echo "2. Fix HIGH severity issues"
  echo "3. Run: python3 /path/to/security-check/scripts/scan_skill.py ."
  exit 1
elif [ $EXIT_CODE -eq 1 ]; then
  echo "⚠️  MEDIUM/LOW warnings found"
  read -p "Commit anyway? (y/N): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "🚫 Commit cancelled"
    exit 1
  fi
else
  echo "✅ No security issues found"
  echo "📝 Proceeding with commit..."
fi
```

**Install Hook:**
```bash
# Make executable
chmod +x .git/hooks/pre-commit

# Or install using pre-commit framework
pre-commit install
```

---

### Pre-Commit with Automatic Commenting

**File:** `.git/hooks/pre-commit`

```bash
#!/bin/bash
# Pre-commit security scanner with detailed output

echo "🔍 Running security scanner..."

# Scan and capture output
RESULT=$(python3 /path/to/security-check/scripts/scan_skill.py . 2>&1)
EXIT_CODE=$?

echo "$RESULT"

# Parse and check
if echo "$RESULT" | grep -q '"summary": "SECURITY ISSUES FOUND'; then
  echo "❌ CRITICAL: Security issues detected"
  echo ""
  echo "🚫 Commit BLOCKED"
  echo ""
  echo "Affected files:"
  echo "$RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print('\\n'.join([f\"  - {i['file']}: {i['issue']}\" for i in data['issues']]))"
  exit 1
elif echo "$RESULT" | grep -q '"severity": "MEDIUM"'; then
  echo "⚠️  WARNING: Medium severity issues found"
  echo ""
  read -p "Continue commit? (y/N): " -n 1 -r
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
else
  echo "✅ Security check passed"
fi
```

---

## Best Practices

### 1. Choose When to Run Scanner

**Recommended Triggers:**
- **Pull Requests:** Always scan (primary line of defense)
- **Push to main/master:** Scan to catch direct merges
- **Scheduled Daily:** Detect new vulnerabilities in existing skills
- **Before Installation:** Manual scan of external skills

### 2. Handle Exit Codes Correctly

| Exit Code | Meaning | Pipeline Action |
|------------|-----------|-----------------|
| `0` | PASS | Continue (green) |
| `1` | WARN | Optional fail (yellow) or continue with warning |
| `2` | FAIL | Block (red) - stop deployment/installation |

### 3. Publish Scan Results as Artifacts

Store scan results for auditing and debugging:

```yaml
# GitHub Actions
- name: Upload scan results
  uses: actions/upload-artifact@v4
  with:
    name: security-scan-results
    path: security-scan-*.json
    retention-days: 30
```

### 4. Configure Strictness Based on Risk Tolerance

**Low Risk Tolerance:**
- Fail only on HIGH severity
- Continue with MEDIUM/LOW warnings
- Use for: Development environments, fast iteration

**Medium Risk Tolerance:**
- Fail on HIGH and MEDIUM severity
- Continue with LOW severity
- Use for: Staging environments

**High Risk Tolerance (Strict):**
- Fail on ANY severity (HIGH, MEDIUM, LOW)
- Use for: Production, public releases

### 5. Add Security Status to Pull Requests

Automatically comment on PRs with security scan results:

```yaml
# GitHub Actions
- name: Comment PR
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v7
  with:
    script: |
      const results = require('./security-scan-results.json');
      let comment = '## 🔒 Security Scan Results\n\n';

      if (results.issues?.length > 0) {
        comment += '❌ **HIGH Severity Issues:**\n\n';
        results.issues.forEach(i => {
          comment += `**${i.file}:** ${i.issue}\n`;
        });
        comment += '\n🚫 PR blocked until fixed.\n';
      } else if (results.warnings?.length > 0) {
        comment += '⚠️ **Warnings:**\n\n';
        results.warnings.forEach(w => {
          comment += `**${w.file}:** ${w.issue}\n`;
        });
      } else {
        comment += '✅ **No security issues found.**\n';
      }

      github.rest.issues.createComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: context.issue.number,
        body: comment
      });
```

---

## Troubleshooting

### Issue: Scanner Not Found in CI

**Symptoms:**
```
python3: can't open file '/path/to/security-check/scripts/scan_skill.py'
```

**Cause:** Incorrect path in CI/CD config

**Solution:**
```yaml
# Use relative path from repository root
- python3 ./skills/security-check/scripts/scan_skill.py .

# Or use absolute path if scanner is external
- python3 /absolute/path/to/scan_skill.py .
```

---

### Issue: Exit Codes Not Interpreted Correctly

**Symptoms:** Pipeline passes even when HIGH severity issues found

**Cause:** Shell script not checking exit code properly

**Solution:**
```bash
# Run scanner
python3 /path/to/security-check/scripts/scan_skill.py .
EXIT_CODE=$?

# Explicitly check exit code
if [ $EXIT_CODE -eq 2 ]; then
  echo "Blocking: HIGH severity"
  exit 1
fi
```

---

### Issue: False Positives Blocking Pipeline

**Symptoms:** Legitimate code flagged, preventing deployment

**Common False Positives:**
- `rm` in test cleanup scripts
- `eval()` for JSON parsing
- `subprocess.run()` with shell=True

**Solutions:**

1. **Document False Positives:**
   Add SECURITY.md to skill explaining why flagged code is safe

2. **Exclude Test Files:**
   Don't scan `test/` or `spec/` directories

3. **Use Exit Code 1 (WARN) Mode:**
   Don't block pipeline on warnings, only HIGH severity

---

## Summary

- **Exit Code 0:** Pass (no issues)
- **Exit Code 1:** Warn (MEDIUM/LOW severity)
- **Exit Code 2:** Fail (HIGH severity)

Choose strictness level based on environment risk tolerance:
- Development: Fail on HIGH only
- Staging: Fail on HIGH + MEDIUM
- Production: Fail on HIGH + MEDIUM + LOW (strict)

---

**Last Updated:** February 7, 2026
**Scanner Version:** 1.0
**Exit Codes:** 0=PASS, 1=WARN, 2=FAIL
