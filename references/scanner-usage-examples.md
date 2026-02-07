# Security Scanner Usage Examples

This document provides practical examples of using `scan_skill.py` scanner, including output examples for each severity level, troubleshooting guide, and exit code meanings for CI/CD integration.

---

## Basic Usage

### Scan a Single Skill

```bash
python3 scripts/scan_skill.py /path/to/skill
```

**Output:** JSON-formatted security report with issues, warnings, and passed checks.

---

## Severity Levels

The scanner categorizes findings into three severity levels:

| Severity | Meaning | Action Required |
|-----------|-----------|-----------------|
| **HIGH** | Critical security issue | **Block installation** - immediate fix required |
| **MEDIUM** | Potential security concern | Review and fix before production use |
| **LOW** | Informational note | Best practice suggestion, optional |

---

## Output Examples

### Example 1: Clean Skill (No Issues)

**Scenario:** A well-written skill with proper security practices

**Command:**
```bash
python3 scripts/scan_skill.py /Users/rlapuente/clawd/skills/apple-notes
```

**Output:**
```json
{
  "skill_name": "apple-notes",
  "issues": [],
  "warnings": [],
  "passed": [
    {"file": "SKILL.md", "check": "Multi-language prompt injection scan", "status": "Completed"},
    {"directory": "scripts/", "check": "Dangerous pattern scan", "status": "Completed"},
    {"directory": "references/", "check": "Secret and URL scan", "status": "Completed"}
  ],
  "file_read_errors": [],
  "summary": "PASSED: No security issues found"
}
```

**Exit Code:** `0` (success)

**Interpretation:** Skill passed all security checks. Safe to install.

---

### Example 2: HIGH Severity Issue

**Scenario:** Skill with prompt injection attempt in SKILL.md

**Command:**
```bash
python3 scripts/scan_skill.py /path/to/suspicious-skill
```

**Output:**
```json
{
  "skill_name": "suspicious-skill",
  "issues": [
    {
      "severity": "HIGH",
      "file": "SKILL.md",
      "issue": "Potential prompt injection pattern detected: ignore (previous|above|earlier)",
      "recommendation": "Review and remove suspicious instruction patterns"
    }
  ],
  "warnings": [],
  "passed": [
    {"file": "SKILL.md", "check": "Multi-language prompt injection scan", "status": "Completed"}
  ],
  "file_read_errors": [],
  "summary": "SECURITY ISSUES FOUND: 1 issue(s), 0 warning(s)"
}
```

**Exit Code:** `2` (HIGH severity found)

**Interpretation:** **BLOCK installation** - Skill contains critical prompt injection pattern. Do not install until fixed.

---

### Example 3: HIGH Severity - Language-Based Bypass

**Scenario:** Skill attempting to bypass security using non-English language

**Command:**
```bash
python3 scripts/scan_skill.py /path/to/suspicious-skill
```

**Output:**
```json
{
  "skill_name": "suspicious-skill",
  "issues": [
    {
      "severity": "HIGH",
      "file": "SKILL.md",
      "issue": "Potential language-based bypass: Spanish \"override\" pattern detected",
      "recommendation": "Prompt attempts to bypass security via Spanish language translation",
      "context": "Language-based prompt injection"
    },
    {
      "severity": "HIGH",
      "file": "SKILL.md",
      "issue": "Potential language-based bypass: Chinese \"bypass\" pattern detected",
      "recommendation": "Prompt attempts to bypass security via Chinese language translation",
      "context": "Language-based prompt injection"
    }
  ],
  "warnings": [],
  "passed": [
    {"file": "SKILL.md", "check": "Multi-language prompt injection scan", "status": "Completed"}
  ],
  "file_read_errors": [],
  "summary": "SECURITY ISSUES FOUND: 2 issue(s), 0 warning(s)"
}
```

**Exit Code:** `2` (HIGH severity found)

**Interpretation:** **BLOCK installation** - Multiple language-based bypass attempts detected across different languages.

---

### Example 4: HIGH Severity - Hardcoded Secrets

**Scenario:** Skill with API key hardcoded in references directory

**Command:**
```bash
python3 scripts/scan_skill.py /path/to/leaky-skill
```

**Output:**
```json
{
  "skill_name": "leaky-skill",
  "issues": [
    {
      "severity": "HIGH",
      "file": "references/api-config.md",
      "issue": "Potential hardcoded secrets detected: 1 match(es)",
      "recommendation": "Remove hardcoded secrets and use proper secret management"
    }
  ],
  "warnings": [],
  "passed": [
    {"directory": "references/", "check": "Secret and URL scan", "status": "Completed"}
  ],
  "file_read_errors": [],
  "summary": "SECURITY ISSUES FOUND: 1 issue(s), 0 warning(s)"
}
```

**Exit Code:** `2` (HIGH severity found)

**Interpretation:** **BLOCK installation** - Skill contains hardcoded secrets that could expose credentials.

---

### Example 5: HIGH Severity - Dangerous Commands

**Scenario:** Shell script with recursive deletion command

**Command:**
```bash
python3 scripts/scan_skill.py /path/to/destructive-skill
```

**Output:**
```json
{
  "skill_name": "destructive-skill",
  "issues": [
    {
      "severity": "HIGH",
      "file": "scripts/cleanup.sh",
      "issue": "Root deletion command detected",
      "recommendation": "Review and ensure this is intentional and safe"
    }
  ],
  "warnings": [],
  "passed": [
    {"directory": "scripts/", "check": "Dangerous pattern scan", "status": "Completed"}
  ],
  "file_read_errors": [],
  "summary": "SECURITY ISSUES FOUND: 1 issue(s), 0 warning(s)"
}
```

**Exit Code:** `2` (HIGH severity found)

**Interpretation:** **BLOCK installation** - Script contains `rm -rf /` which could destroy system files.

---

### Example 6: MEDIUM Severity Warnings

**Scenario:** Skill with `os.system()` usage (potentially unsafe)

**Command:**
```bash
python3 scripts/scan_skill.py /path/to/cautious-skill
```

**Output:**
```json
{
  "skill_name": "cautious-skill",
  "issues": [],
  "warnings": [
    {
      "severity": "MEDIUM",
      "file": "scripts/helper.py",
      "issue": "os.system() usage",
      "recommendation": "Review and ensure this is safe"
    },
    {
      "severity": "MEDIUM",
      "file": "SKILL.md",
      "issue": "External network call pattern: curl.*http[s]?://",
      "recommendation": "Verify all network calls are intentional and secure"
    }
  ],
  "passed": [
    {"file": "SKILL.md", "check": "Multi-language prompt injection scan", "status": "Completed"},
    {"directory": "scripts/", "check": "Dangerous pattern scan", "status": "Completed"}
  ],
  "file_read_errors": [],
  "summary": "WARNINGS: 2 warning(s) (no critical issues)"
}
```

**Exit Code:** `1` (MEDIUM severity found)

**Interpretation:** **Review before production** - Skill has potential security concerns. Manual review required before installing in production environment.

---

### Example 7: LOW Severity Notes

**Scenario:** Skill with suspicious URL in documentation

**Command:**
```bash
python3 scripts/scan_skill.py /path/to/info-skill
```

**Output:**
```json
{
  "skill_name": "info-skill",
  "issues": [],
  "warnings": [
    {
      "severity": "LOW",
      "file": "references/setup.md",
      "issue": "Suspicious URL detected: https://pastebin.com/raw/xyz123",
      "recommendation": "Verify this URL is legitimate and safe"
    }
  ],
  "passed": [
    {"directory": "references/", "check": "Secret and URL scan", "status": "Completed"}
  ],
  "file_read_errors": [],
  "summary": "WARNINGS: 1 warning(s) (no critical issues)"
}
```

**Exit Code:** `1` (MEDIUM/LOW severity found)

**Interpretation:** **Best practice review** - Pastebin link flagged as suspicious. Verify URL is legitimate before installing.

---

### Example 8: Mixed Issues (HIGH + MEDIUM + LOW)

**Scenario:** Skill with multiple security concerns

**Command:**
```bash
python3 scripts/scan_skill.py /path/to/complex-skill
```

**Output:**
```json
{
  "skill_name": "complex-skill",
  "issues": [
    {
      "severity": "HIGH",
      "file": "SKILL.md",
      "issue": "Potential prompt injection pattern detected: bypass security",
      "recommendation": "Review and remove suspicious instruction patterns"
    },
    {
      "severity": "HIGH",
      "file": "scripts/processor.py",
      "issue": "eval() usage detected",
      "recommendation": "Review and ensure this is intentional and safe"
    }
  ],
  "warnings": [
    {
      "severity": "MEDIUM",
      "file": "scripts/processor.py",
      "issue": "os.system() usage",
      "recommendation": "Review and ensure this is safe"
    },
    {
      "severity": "LOW",
      "file": "references/external.md",
      "issue": "Suspicious URL detected: https://bit.ly/abc123",
      "recommendation": "Verify this URL is legitimate and safe"
    }
  ],
  "passed": [
    {"file": "SKILL.md", "check": "Multi-language prompt injection scan", "status": "Completed"},
    {"directory": "scripts/", "check": "Dangerous pattern scan", "status": "Completed"},
    {"directory": "references/", "check": "Secret and URL scan", "status": "Completed"}
  ],
  "file_read_errors": [],
  "summary": "SECURITY ISSUES FOUND: 2 issue(s), 2 warning(s)"
}
```

**Exit Code:** `2` (HIGH severity found)

**Interpretation:** **BLOCK installation** - Multiple HIGH severity issues prevent installation. Fix all HIGH issues before reviewing MEDIUM warnings.

---

### Example 9: File Read Errors

**Scenario:** Skill with UTF-8 encoding issues

**Command:**
```bash
python3 scripts/scan_skill.py /path/to/encoding-error-skill
```

**Output:**
```json
{
  "skill_name": "encoding-error-skill",
  "issues": [],
  "warnings": [
    {
      "severity": "LOW",
      "file": "SKILL.md",
      "issue": "Encoding error reading file: 'utf-8' codec can't decode byte 0xff",
      "recommendation": "Check file encoding (UTF-8 expected)"
    }
  ],
  "passed": [],
  "file_read_errors": [
    {
      "file": "SKILL.md",
      "error": "Encoding error reading file: 'utf-8' codec can't decode byte 0xff"
    }
  ],
  "summary": "WARNINGS: 1 warning(s) (no critical issues) | 1 file read error(s)"
}
```

**Exit Code:** `1` (MEDIUM/LOW severity found)

**Interpretation:** **Review needed** - File encoding issues prevented complete scan. Fix encoding and rescan.

---

## Exit Codes

The scanner uses the following exit codes for CI/CD integration:

| Exit Code | Severity | Meaning | CI/CD Action |
|------------|-----------|-----------|----------------|
| `0` | None | No security issues found | **Pass** - Allow installation |
| `1` | MEDIUM/LOW | Warnings found | **Fail build** or **Warn only** (configurable) |
| `2` | HIGH | Critical security issues found | **Block** - Stop deployment |

---

## Troubleshooting Guide

### Issue: "Encoding error reading file"

**Symptoms:**
```
"Encoding error reading file: 'utf-8' codec can't decode byte"
```

**Cause:** File uses non-UTF-8 encoding

**Solution:**
```bash
# Detect encoding
file -i path/to/file

# Convert to UTF-8
iconv -f ISO-8859-1 -t UTF-8 input.md > output.md
```

---

### Issue: "Missing required SKILL.md file"

**Symptoms:**
```json
{
  "severity": "HIGH",
  "file": "SKILL.md",
  "issue": "Missing required SKILL.md file"
}
```

**Cause:** SKILL.md file doesn't exist in skill directory

**Solution:**
```bash
# Check if file exists
ls -la /path/to/skill/

# Create SKILL.md if missing
touch /path/to/skill/SKILL.md
```

---

### Issue: Scanner reports false positives

**Symptoms:** Legitimate code flagged as dangerous

**Common Causes:**
- `rm` used in test cleanup (not production code)
- `eval()` used for configuration parsing (not code execution)
- `subprocess.run()` with shell=True for legitimate reasons

**Solution:** Review flagged code and verify it's safe. If legitimate, document why it's safe in skill's README.

---

### Issue: Scanner crashes or hangs

**Symptoms:** No output, command never completes

**Common Causes:**
- Skill directory doesn't exist
- Permission denied on skill files
- Very large files causing slow scanning

**Solutions:**
```bash
# Check skill path exists
ls -la /path/to/skill

# Check permissions
chmod -R +r /path/to/skill

# Use verbose mode (add print statements to scanner)
python3 -u scripts/scan_skill.py /path/to/skill
```

---

### Issue: Exit code doesn't match expectations

**Symptoms:** Scanner exits with code `0` but you see warnings

**Cause:** Exit codes only track HIGH and MEDIUM severity. LOW severity notes don't affect exit codes.

**Solution:**
- Use JSON output to check for LOW severity warnings
- Review `warnings` array for all non-critical issues

---

## CI/CD Integration

### GitHub Actions Example

**File:** `.github/workflows/security-check.yml`

```yaml
name: Security Check

on: [pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run security scanner
        run: |
          pip install python3
          python3 /path/to/security-check/scripts/scan_skill.py .

      # Exit code 2: HIGH severity - fail build
      # Exit code 1: MEDIUM severity - fail build (optional)
      # Exit code 0: Pass

      - name: Upload scan results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: security-scan-results
          path: scan-results.json
```

---

### GitLab CI Example

**File:** `.gitlab-ci.yml`

```yaml
security-scan:
  stage: test
  script:
    - pip3 install python3
    - python3 /path/to/security-check/scripts/scan_skill.py .
  artifacts:
    paths:
      - scan-results.json
    expire_in: 1 week
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
```

---

### Pre-Commit Hook

**File:** `.git/hooks/pre-commit`

```bash
#!/bin/bash
# Run security scanner before commit
python3 /path/to/security-check/scripts/scan_skill.py .

# Exit on HIGH or MEDIUM severity
exit_code=$?
if [ $exit_code -ne 0 ]; then
  echo "❌ Security check failed. Commit blocked."
  echo "Run: python3 /path/to/security-check/scripts/scan_skill.py ."
  exit 1
fi

echo "✅ Security check passed."
exit 0
```

---

## Best Practices

### 1. Scan Before Installation

Always scan skills before installing, especially from untrusted sources:

```bash
# Download skill
git clone https://github.com/unknown/skill.git

# Scan before installing
python3 /path/to/security-check/scripts/scan_skill.py ./skill

# Only install if exit code is 0
if [ $? -eq 0 ]; then
  cp -r ./skill ~/.openclaw/skills/
fi
```

---

### 2. Scan All Installed Skills Periodically

```bash
# Scan all skills
for skill in ~/.openclaw/skills/*; do
    echo "Scanning: $skill"
    python3 /path/to/security-check/scripts/scan_skill.py "$skill"
done
```

---

### 3. Review Warnings Manually

MEDIUM severity warnings require human review before blocking installation:

1. Read warning details
2. Review flagged code
3. Verify pattern is intentional and safe
4. Document why it's safe in a SECURITY.md file

---

### 4. Keep Scanner Updated

The scanner patterns evolve to detect new threats:

```bash
# Check for updates
cd /path/to/security-check
git pull origin main

# Run updated scanner
python3 scripts/scan_skill.py /path/to/skill
```

---

## Summary

- **Clean skill:** Exit code `0`, summary: "PASSED: No security issues found"
- **Warnings:** Exit code `1`, summary: "WARNINGS: X warning(s)"
- **Critical issues:** Exit code `2`, summary: "SECURITY ISSUES FOUND: X issue(s)"
- **File read errors:** Appended to summary with count

For more information, see:
- Security checklist: `references/security-checklist.md`
- Prompt injection patterns: `references/prompt-injection-patterns.md`

---

**Last Updated:** February 7, 2026
**Scanner Version:** 1.0
