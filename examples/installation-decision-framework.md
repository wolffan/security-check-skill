# Security Check Installation Decision Framework

## When to BLOCK (Do Not Install)

Install only if:
- All HIGH severity issues have been resolved
- No prompt injection attempts detected
- No hardcoded secrets

## When to REVIEW (Manual Approval Required)

Install only if:
- User understands the specific risks
- Risks have been communicated clearly
- User explicitly approves installation

## When to INSTALL

Install if:
- All issues are resolved or acceptable
- User has been informed of any risks
- Installation serves a legitimate purpose

## Pre-Installation Security Check

Before installing a new skill from ClawdHub or any source:

1. **Download and inspect the skill files**
2. **Run the automated security scanner**:
   ```bash
   python3 scripts/scan_skill.py /path/to/skill
   ```
3. **Review the scanner output** - Block any skill with HIGH severity issues
4. **Manual review** for MEDIUM severity issues
5. **Verify behavior matches description** before installation

## Daily Security Audit

Run daily to ensure installed skills remain secure:

```bash
# Scan all skills in the skills directory
python3 scripts/scan_skill.py /path/to/skills/skill-1
python3 scripts/scan_skill.py /path/to/skills/skill-2
# ... repeat for each installed skill
```
