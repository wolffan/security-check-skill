# Security Scanner Output Examples

## Scanner Usage Examples

The `scripts/scan_skill.py` tool provides automated security analysis:

```bash
python3 scripts/scan_skill.py <skill-path>
```

**Output includes:**
- HIGH severity issues (immediate action required)
- MEDIUM severity warnings (review recommended)
- LOW severity notes (informational)
- Summary of checks performed

### Example 1: Skill with Issues

```json
{
  "skill_name": "example-skill",
  "issues": [
    {
      "severity": "HIGH",
      "file": "SKILL.md",
      "issue": "Potential prompt injection pattern",
      "recommendation": "Review and remove suspicious patterns"
    }
  ],
  "warnings": [
    {
      "severity": "MEDIUM",
      "file": "scripts/helper.py",
      "issue": "os.system() usage detected",
      "recommendation": "Review and ensure this is safe"
    }
  ],
  "passed": [
    {"file": "SKILL.md", "check": "Prompt injection scan", "status": "Completed"}
  ],
  "summary": "SECURITY ISSUES FOUND: 1 issue(s), 1 warning(s)"
}
```

### Example 2: Clean Skill

```json
{
  "skill_name": "clean-skill",
  "issues": [],
  "warnings": [],
  "passed": [
    {"file": "SKILL.md", "check": "Prompt injection scan", "status": "Completed"},
    {"file": "scripts/tool.py", "check": "Hardcoded secrets scan", "status": "Completed"},
    {"file": "references/docs.md", "check": "Secrets exposure scan", "status": "Completed"}
  ],
  "summary": "NO ISSUES FOUND: All security checks passed"
}
```

### Example 3: Multiple Issues

```json
{
  "skill_name": "complex-skill",
  "issues": [
    {
      "severity": "HIGH",
      "file": "SKILL.md",
      "issue": "Potential prompt injection pattern",
      "recommendation": "Review and remove suspicious patterns"
    },
    {
      "severity": "HIGH",
      "file": "scripts/helper.py",
      "issue": "Hardcoded API key detected",
      "recommendation": "Remove hardcoded API key and use environment variables"
    },
    {
      "severity": "MEDIUM",
      "file": "scripts/tool.py",
      "issue": "Unsafe subprocess usage",
      "recommendation": "Review and ensure shell=True is safe"
    }
  ],
  "warnings": [],
  "passed": [
    {"file": "SKILL.md", "check": "Prompt injection scan", "status": "Completed"},
    {"file": "scripts/helper.py", "check": "Dangerous commands scan", "status": "Completed"},
    {"file": "references/docs.md", "check": "Secrets exposure scan", "status": "Completed"}
  ],
  "summary": "SECURITY ISSUES FOUND: 2 HIGH, 0 MEDIUM, 0 LOW"
}
```

### Example 4: Low Severity Only

```json
{
  "skill_name": "experimental-skill",
  "issues": [],
  "warnings": [],
  "passed": [
    {"file": "SKILL.md", "check": "Prompt injection scan", "status": "Completed"},
    {"file": "scripts/tool.py", "check": "Hardcoded secrets scan", "status": "Completed"}
  ],
  "summary": "NO ISSUES FOUND: All security checks passed"
}
```

## Scanner What-Checks

The scanner performs these checks:

### 1. SKILL.md Analysis
- Prompt injection patterns
- External network calls
- Suspicious instructions

### 2. Scripts Directory Scan
- Dangerous command patterns (rm -rf, eval, exec)
- Hardcoded secrets and credentials
- Unsafe subprocess usage
- File system operations outside skill directory

### 3. Reference Materials Scan
- Hardcoded secrets (passwords, API keys, tokens)
- Suspicious URLs (pastebin, raw GitHub links)
- Sensitive information exposure

## Error Messages

### HIGH Severity Issues

```
ERROR: HIGH severity issue found in SKILL.md:
  Issue: Potential prompt injection pattern
  File: SKILL.md
  Recommendation: Review and remove suspicious patterns
```

### MEDIUM Severity Warnings

```
WARNING: MEDIUM severity warning in scripts/helper.py:
  Issue: os.system() usage detected
  File: scripts/helper.py
  Recommendation: Review and ensure this is safe
```

### SKILL Not Found

```
ERROR: Skill directory not found: /path/to/nonexistent-skill
```

### File Not Found in Skill

```
ERROR: File not found in skill: /path/to/skill/nonexistent-file.py
```
