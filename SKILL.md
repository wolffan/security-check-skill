---
name: security-check
description: Security audit and inspection for Clawdbot skills before installation and for regular monitoring. Use when needing to check skills for security vulnerabilities, perform regular security audits on installed skills, verify skill descriptions match actual behavior, scan for prompt injection attempts, check for hardcoded secrets/credentials, verify no malicious intent in skill code or documentation, review file access patterns for configuration/secrets exposure, or audit dependencies for known vulnerabilities. Inputs: skill directories or skill packages. Outputs: security reports with severity levels (HIGH/MEDIUM/LOW), vulnerability assessments, and installation recommendations. Provides automated scanner (scripts/scan_skill.py) and manual checklists for comprehensive security assessment.
license: Complete terms in LICENSE.txt
---

# Security Check Skill

Comprehensive security auditing for Clawdbot skills to detect malicious intent, prompt injection, secrets exposure, and misaligned behavior.

## Quick Start

### Pre-Installation Security Check

Before installing a new skill from ClawdHub or any source:

1. **Download and inspect the skill files**
2. **Run the automated security scanner**:
   ```bash
   python3 scripts/scan_skill.py /path/to/skill
   ```
3. **Review the scanner output** - Block any skill with HIGH severity issues
4. **Manual review** for MEDIUM severity issues
5. **Verify behavior matches description** before installation

### Daily Security Audit

Run daily to ensure installed skills remain secure:

```bash
# Scan all skills in the skills directory
python3 scripts/scan_skill.py /path/to/skills/skill-1
python3 scripts/scan_skill.py /path/to/skills/skill-2
# ... repeat for each installed skill
```

## Security Scanner

### Running the Scanner

The `scripts/scan_skill.py` tool provides automated security analysis:

```bash
python3 scripts/scan_skill.py <skill-path>
```

**Output includes:**
- HIGH severity issues (immediate action required)
- MEDIUM severity warnings (review recommended)
- LOW severity notes (informational)
- Summary of checks performed

**Example output:**
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

### What the Scanner Checks

1. **SKILL.md Analysis**
   - Prompt injection patterns
   - External network calls
   - Suspicious instructions

2. **Scripts Directory Scan**
   - Dangerous command patterns (rm -rf, eval, exec)
   - Hardcoded secrets and credentials
   - Unsafe subprocess usage
   - File system operations outside skill directory

3. **References Directory Scan**
   - Hardcoded secrets (passwords, API keys, tokens)
   - Suspicious URLs (pastebin, raw GitHub links)
   - Sensitive information exposure

4. **Supply Chain & Dependency Analysis** (NEW)
   - Dependency download count validation
   - Suspicious package name detection
   - Pre/post install script analysis
   - Lockfile integrity verification

## Supply Chain Attack Detection (NEW PROTOCOL)

Based on real-world supply chain attacks in crypto/blockchain sectors, these protocols detect malicious packages that steal credentials (AWS, Azure, GCP, Vercel) or exfiltrate data.

### Critical: Pre-Clone Repository Vetting

Before cloning any skill repository, run these checks. **Do not clone until all pass or you explicitly approve proceeding.**

#### Repository Metadata Analysis

```bash
# GitHub API check (if GitHub)
curl -s "https://api.github.com/repos/<owner>/<repo>"

# Check for RED FLAGS:
# - Repository age < 30 days
# - < 10 commits total
# - 0 stars + 0 forks but claimed as production
# - Owner account created < 3 months ago
# - No commit activity for months, suddenly active again
```

**RED FLAGS - BLOCK CLONE:**
- Repo created < 30 days ago AND claims to be production code
- < 10 commits total with professional description
- 0 stars, 0 forks, but marketed as "widely used"
- New owner account (< 3 months) with multiple "company projects"

#### Package.json Dependency Analysis (CRITICAL)

Before any `npm install`, read package.json first:

```bash
# Get all dependencies
cat package.json | jq '.dependencies, .devDependencies, .optionalDependencies'

# Check each package on NPM
npm view <package-name> --json | jq '{name, version, downloads: {lastWeek, lastMonth, lastYear}, maintainers, homepage, repository, author, license, deprecated}'
```

**CRITICAL RED FLAGS - BLOCK INSTALL:**
- Packages with **< 1,000 downloads total**
- Packages with **last-week downloads < 10**
- Packages with **no homepage or repository link**
- Packages with **single maintainer who is not repo owner**
- Packages with **non-standard or missing license**
- **Typosquatting names** (e.g., `expresss` instead of `express`)
- **Suspicious package names**: `loader`, `installer`, `setup`, `runner`, `writer`, `json-merge-tool`, `jsonify-core`

**Suspicious pattern from real attack:**
- Package `json-merge-tool` with 97 downloads in "professional" codebase
- Immediately red-flagged as malicious supply chain component

#### Script Analysis (package.json)

```bash
cat package.json | jq '.scripts'
```

**CRITICAL RED FLAGS - BLOCK INSTALL:**
- **Pre/post install hooks** that run arbitrary commands
- Scripts with `curl` or `wget` downloading from external URLs
- Scripts executing binaries from node_modules
- Scripts generating files in system directories

**Real attack pattern:**
```json
{
  "scripts": {
    "postinstall": "node node_modules/writer.js"  // Suspicious utility file
  }
}
```

#### Lockfile Integrity Check

```bash
# npm lockfile (npm 7+)
cat package-lock.json | jq -r '.packages[].integrity'

# yarn lockfile
grep -A 1 "resolved:" yarn.lock

# pnpm lockfile
grep -A 2 "integrity:" pnpm-lock.yaml
```

**RED FLAGS:**
- Missing integrity hashes (tampered lockfile)
- Unusual resolved URLs (not registry.npmjs.org)
- Multiple versions of same package (dependency confusion)

### Code Red Flag Detection (After Safe Clone)

#### Environment Variable Access (CREDENTIAL THEFT VECTOR)

```bash
# Find files reading ALL env vars
grep -r "process\.env\[" --include="*.js" --include="*.ts" .

# Find credential scanning patterns
grep -rE "(AWS_|AZURE_|GCP_|VERCEL_|DATABASE_|API_KEY|SECRET|PASSWORD|TOKEN)" --include="*.js" --include="*.ts" .

# Check for exfiltration
grep -rE "(fetch|axios|request|http\.get)" --include="*.js" -A 5 | grep -E "(process\.env|Buffer\.from|atob|btoa)"
```

**CRITICAL RED FLAGS - IMMEDIATE BLOCK:**
- Files that read **ALL env vars**: `const env = process.env`
- Files combining env vars with Base64 encoding/decoding
- HTTP requests sending env vars to external endpoints
- Code scanning for **AWS_, AZURE_, GCP_, VERCEL_** credentials specifically
- Code searching `~/.aws`, `~/.config`, `~/.azure` for credentials

**Real attack pattern:**
```javascript
// writer.js - malicious utility file
const env = process.env;  // Reads ALL environment variables
const ip = await getPublicIP();  // Gets user IP
const payload = { env, ip, ua: navigator.userAgent };
const encoded = Buffer.from(JSON.stringify(payload)).toString('base64');
// Sends to external endpoint - credential theft + full fingerprint
```

#### Base64 Encoded Payloads

```bash
# Find suspicious Base64 strings (32+ chars)
grep -rE "[A-Za-z0-9+/]{32,}={0,2}" --include="*.js" --include="*.ts" -n

# Decode suspicious strings
echo "<base64-string>" | base64 -d
```

**RED FLAGS:**
- Base64 strings that decode to **URLs**
- Base64 strings that decode to **shell commands or code**
- Base64 strings that decode to **credential patterns**
- Multiple encoding layers (Base64 + Unicode + hex)

#### Network Exfiltration Detection

```bash
# Find all HTTP requests
grep -rE "(fetch|axios|request|http\.(get|post)|https\.get|https\.post)" --include="*.js" --include="*.ts" -n

# Find WebSocket connections
grep -rE "(WebSocket|ws\.connect|new WebSocket)" --include="*.js" --include="*.ts" -n
```

**Analyze each request with context:**
```bash
grep -rE "(fetch|axios)" --include="*.js" -B 5 -A 5
```

**CRITICAL RED FLAGS:**
- Requests to **non-HTTPS endpoints** (http:// not https://)
- Requests to **unknown external domains** (not project's own API)
- Requests sending **user data without explicit action**
- Requests in **library/utility code** that shouldn't make network calls
- Requests combining **multiple data sources** (user agent + IP + env vars)

#### Suspicious File Patterns

```bash
# Find recently created files
find . -name "*.js" -o -name "*.ts" | xargs ls -lt | head -20

# Find executable .js/.ts files (NOT NORMAL)
find . -perm /111 -type f -name "*.js" -o -name "*.ts"

# Find shell shebangs in JS/TS files
grep -r "#!/" --include="*.js" --include="*.ts"
```

**RED FLAGS:**
- Execute permissions on .js/.ts files
- Shell shebangs in JS/TS files
- Files in unexpected locations (node_modules/.cache, .vscode/extensions)
- Suspicious file names: `writer.js`, `loader.js`, `installer.js`, `setup.js`

### NPM Audit Before Install (Non-Execution)

```bash
# Audit without installing
npm audit --json --package-lock-only 2>/dev/null || npm audit --json

# Check for known vulnerabilities
npm audit --audit-level=high

# Check for deprecated packages
npm outdated --json 2>/dev/null | jq '.[] | select(.deprecated == true)'
```

**CRITICAL FINDINGS:**
- High/critical severity vulnerabilities in dependencies
- Deprecated packages with no replacement
- Dependency chains with multiple vulnerabilities

### Container/VM Isolation (If Proceeding Despite Red Flags)

If any red flags found but user wants to proceed:

**REQUIRE ISOLATED EXECUTION:**
1. Docker container with network restrictions
2. VM with no access to host credentials
3. Separate user account with no sudo/cred access

**Dockerfile template for safe execution:**
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
# NETWORK ISOLATION: Block external requests during install
RUN npm ci --ignore-scripts
COPY . .
# Run with restricted capabilities
CMD ["node", "--no-network", "index.js"]
```

### Post-Install Verification

After npm/yarn/pnpm install, verify:

```bash
# Check what was actually installed
npm list --depth=0
npm list --depth=1

# Verify integrity of installed packages
npm verify  # npm 7+

# Check if postinstall hooks ran
npm run env 2>&1 | grep -E "(npm_config_|INIT_CWD)"

# Check for suspicious binaries created
find node_modules/.bin -type f -executable
```

## Supply Chain Security Checklist (10-Point Pre-Install Verification)

**Before ANY npm/yarn/pnpm install, confirm ALL 10:**

1. ✓ Repository age > 30 days OR you explicitly trust the source
2. ✓ All dependencies have > 1,000 downloads OR you've manually audited the package
3. ✓ No packages with suspicious names (loader, installer, setup, writer, runner, json-merge-tool, jsonify-core)
4. ✓ No pre/post install hooks that execute external code
5. ✓ No files reading ALL env vars without clear, documented purpose
6. ✓ No Base64-encoded suspicious strings (32+ chars) in code
7. ✓ No HTTP requests to unknown external domains in library/utility code
8. ✓ npm audit shows 0 high/critical vulnerabilities OR you explicitly accept risk
9. ✓ Code will run in isolated environment (Docker/VM) OR you trust it fully
10. ✓ No credentials (AWS, Azure, GCP, Vercel) in environment during execution

**If ANY fail → BLOCK INSTALL until resolved or explicitly approved.**

## Manual Security Checklist

Use the comprehensive checklist in `references/security-checklist.md` for manual reviews.

### Critical Checks (Before Installation)

#### 1. Documentation Integrity (SKILL.md)
- ✅ Description accurately reflects skill functionality
- ❌ No prompt injection patterns (see `references/prompt-injection-patterns.md`)
- ❌ No instructions to ignore/discard context
- ❌ No system override commands
- ✅ No hidden capabilities beyond description

#### 2. Code Review (scripts/)
- ❌ No hardcoded credentials or secrets
- ❌ No dangerous file operations (rm -rf outside skill dir)
- ❌ No eval() or exec() with user input
- ❌ No unauthorized network requests
- ✅ All operations within skill directory
- ✅ Proper input validation

#### 3. Reference Materials (references/)
- ❌ No hardcoded passwords, API keys, or tokens
- ❌ No production credentials in documentation
- ✅ Links only to legitimate, trusted sources
- ✅ No documentation of security bypasses

#### 4. Behavior Alignment
- ✅ Every command matches stated purpose
- ✅ No hidden capabilities
- ✅ No unnecessary file system access
- ✅ Network access only when explicitly required

### Daily Audit Checks

1. **Scan all installed skills** with the automated scanner
2. **Review any new HIGH severity issues**
3. **Check for modified files** in skill directories
4. **Verify skill descriptions still match behavior**
5. **Audit new dependencies** if added

## Specific Security Concerns

### Prompt Injection Detection

Read `examples/prompt-injection-patterns.md` for comprehensive patterns.

**Key indicators:**
- Instructions to ignore/discard context
- System override or bypass commands
- Authority impersonation (act as administrator, etc.)
- Jailbreak attempts (unrestricted mode, etc.)
- Instruction replacement patterns

**Detection:**
```python
# Automated pattern matching
import re
dangerous_patterns = [
    r'ignore\s+previous\s+instructions',
    r'override\s+security',
    r'act\s+as\s+administrator',
]
```

### Secrets and Credentials Exposure

**What to scan for:**
- Hardcoded passwords, API keys, tokens
- AWS access keys and secret keys
- SSH private keys
- Database connection strings
- Other sensitive credentials

**Patterns to detect:**
```
password="..."
secret='...'
token="1234567890abcdef"
api_key="..."
aws_access_key_id="..."
```

### Local Configuration Access

**Block access to:**
- `~/.clawdbot/credentials/`
- `~/.aws/credentials`
- `~/.ssh/` directory
- `~/.npmrc` and other config files
- Shell history files
- System keychain

**Allow only:**
- Skill-specific configuration files
- User-provided file paths
- Designated workspace directories
- Approved environment variables

### Command-Behavior Alignment

**Verification process:**
1. Extract all commands/operations from skill code
2. Compare against description in SKILL.md
3. Identify any operations not documented
4. Flag suspicious or hidden capabilities

**Example misalignment:**

❌ **BLOCK:**
- Description: "Format text documents"
- Actual: Scans filesystem, sends data to external server

✅ **SAFE:**
- Description: "Convert Markdown to PDF with templates"
- Actual: Reads Markdown, applies template, generates PDF

## Security Severity Levels

### HIGH (Immediate Block)
- Prompt injection patterns detected
- Hardcoded secrets or credentials
- Data exfiltration capabilities
- Unauthorized file system access
- Dangerous file operations (rm -rf, dd, etc.)
- eval() or exec() with untrusted input
- **NEW:** Dependencies with < 1,000 downloads and suspicious names
- **NEW:** Files reading ALL environment variables without clear purpose
- **NEW:** Base64-encoded payloads that decode to URLs/commands
- **NEW:** HTTP requests to unknown external endpoints
- **NEW:** Pre/post install hooks executing external code

**Action:** Do not install. Report to skill author.

### MEDIUM (Review Required)
- Suspicious but not clearly malicious
- Requires user approval for specific operations
- Limited network access to unverified endpoints
- Unsafe subprocess usage (shell=True)
- Environment variable exposure risks

**Action:** Manual review. Install only if justified and understood.

### LOW (Informational)
- Suspicious URLs (may be legitimate)
- Documentation of deprecated practices
- Minor code quality issues
- Potential improvements for security

**Action:** Note for future review. Generally safe to install.

## Installation Decision Framework

### When to BLOCK (Do Not Install)
- Any HIGH severity issues present
- Clear prompt injection attempts
- Hardcoded secrets
- Data exfiltration
- Unauthorized access patterns

### When to WARN (Install with Caution)
- MEDIUM severity issues present
- Suspicious patterns requiring verification
- Needs specific user approvals
- Network access to unknown endpoints

**Before installing with WARN:**
1. Understand the risk
2. Verify the skill author's reputation
3. Test in isolated environment first
4. Monitor behavior closely
5. Be prepared to uninstall

### When to APPROVE (Safe to Install)
- No security issues detected
- Well-documented and transparent
- Matches description perfectly
- From trusted source
- Regularly audited

## Dependency Security

Check skill dependencies for vulnerabilities:

```bash
# For Node.js skills
npm audit
npm audit fix

# For Python skills
pip-audit
safety check
```

**What to check:**
- Known CVEs in dependencies
- Outdated packages with security updates
- Transitive dependency vulnerabilities
- Untrusted or unmaintained packages

## Security Reporting

### Report Template

```markdown
# Security Audit Report
**Date:** [Date]
**Skill:** [Skill Name]
**Version:** [Version]

## Executive Summary
[Overall security posture: SAFE, WARNING, or BLOCK]

## Critical Issues (Immediate Action Required)
[List HIGH severity issues]

## Warnings (Review Recommended)
[List MEDIUM severity issues]

## Informational Notes
[List LOW severity issues]

## Recommendations
[Actionable items to address issues]

## Conclusion
[Final verdict: Install/Block/Requires Changes]
```

### Escalation Process

1. **Detect issue** during scan or review
2. **Document findings** using report template
3. **Assess severity** (HIGH/MEDIUM/LOW)
4. **Take action:**
   - HIGH: Block skill, report to author
   - MEDIUM: Review, install with caution or wait for fix
   - LOW: Note, monitor
5. **Follow up** on resolved issues

## Real-World Supply Chain Attack Case Study

### Crypto/Blockchain Developer Targeting (February 2026)

**Attack vector:** Malicious package disguised as legitimate tool in professional job codebase

**How it unfolded:**
1. **Legitimate-looking recruitment:** Real company, real recruiter, professional PDF briefing, detailed Figma
2. **Suspicious repo structure:** Forced monorepo with unnatural backend/frontend separation for MVP
3. **Red flag discovered:** Package named `json-merge-tool` with only **97 downloads**
4. **Malicious entry point:** `writer.js` file designed to:
   - Read **ALL environment variables** (`const env = process.env`)
   - Get user's **public IP address**
   - Combine env vars + IP + user agent
   - Encode in **Base64** to evade detection
   - Send to external endpoint for exfiltration
5. **Targets:** Specifically scanned for **AWS, Azure, GCP, Vercel** credentials
6. **Goal:** Drain wallets, steal cookies, exfiltrate cloud provider credentials

**Lessons learned:**
- ✅ **Always check download counts** before installing packages
- ✅ **Investigate suspicious package names** in unexpected contexts
- ✅ **Never run npm install** without auditing package.json first
- ✅ **Be suspicious of "over-engineered" repos** for simple projects
- ✅ **Scan for env var access** - it's a credential theft vector
- ✅ **Decode Base64 strings** to find hidden payloads
- ✅ **Check where network requests go** - external endpoints = red flag

**What blocked this attack:**
- Investigating the suspicious `json-merge-tool` package (97 downloads)
- Reading `writer.js` before running npm install
- Noticing the env var collection pattern
- Decoding the Base64 payload to see the exfiltration endpoint

**What would have happened if install ran:**
- All cloud provider credentials stolen (AWS, Azure, GCP, Vercel)
- Crypto wallets drained
- Browser cookies stolen
- Full system compromise via credential theft

This is **exactly why** supply chain security protocols are critical for all code execution, not just production workloads.

## Reference Materials

### Essential Reading

1. **Security Checklist** (`references/security-checklist.md`)
2. **Supply Chain Security Checklist** (10-point verification above)
3. **Real-World Attack Case Study** (this section)
   - Comprehensive security criteria
   - Command alignment verification
   - Secrets exposure checks
   - Installation guidelines
   - Daily audit procedures

2. **Prompt Injection Patterns** (`references/prompt-injection-patterns.md`)
   - Detection categories and patterns
   - Automated detection strategies
   - Red flag indicators
   - Mitigation techniques
   - Reporting templates

3. **Scanner Usage Examples** (`references/scanner-usage-examples.md`)
   - Real-world scanner output examples (clean, HIGH, MEDIUM, LOW)
   - Exit code meanings for CI/CD integration
   - Troubleshooting guide (encoding errors, missing files, false positives)
   - Best practices for scanning skills

4. **CI/CD Integration Guide** (`references/cicd-integration-guide.md`)
   - GitHub Actions workflows (fail on HIGH, strict mode)
   - GitLab CI pipelines (basic, auto-merge blocking)
   - Pre-commit hooks (local protection)
   - Exit code handling (0=PASS, 1=WARN, 2=FAIL)
   - Best practices for CI/CD security

### Internal Security Docs

Refer to workspace security documents:
- `SECURITY_AUDIT_REPORT.md` - Overall Clawdbot security posture
- Any additional security policies or guidelines

## Workflow Examples

### Example 1: New Skill from ClawdHub

**User request:** "Check if skill 'xyz' is safe to install"

**Response:**
1. Download skill to temporary location
2. Run scanner: `python3 scripts/scan_skill.py /tmp/xyz-skill`
3. Review output:
   - If HIGH issues: "❌ BLOCKED: [list issues] - Do not install"
   - If MEDIUM issues: "⚠️ WARNING: [list issues] - Requires manual review"
   - If clean: "✅ SAFE: No security issues detected - Can install"
4. If MEDIUM issues: Provide detailed manual review using checklist

### Example 2: Daily Security Audit

**Daily routine:**
```bash
# Scan all installed skills
for skill in /Users/rlapuente/clawd/skills/*/; do
    python3 scripts/scan_skill.py "$skill"
done

# Review any HIGH issues immediately
# Monitor MEDIUM issues for trends
```

### Example 3: Verification of Skill Update

**After skill update:**
1. Compare new version with previous
2. Scan new version with security scanner
3. Check for new issues introduced
4. Verify changes match update notes
5. Re-approve only if security posture maintained

## Best Practices

1. **Always scan before installing** - Never skip security check
2. **Review HIGH issues immediately** - Don't ignore critical problems
3. **Document all security findings** - Maintain audit trail
4. **Report issues to skill authors** - Help improve ecosystem
5. **Stay updated on threats** - Monitor security research
6. **Regular audits** - Daily automated scans, weekly manual reviews
7. **Isolate testing** - Test new skills in sandbox environment
8. **Monitor behavior** - Watch for unexpected actions during use

## Maintenance

### Regular Updates

- Update detection patterns for new threats
- Add new security indicators to checklist
- Improve scanner accuracy based on false positives/negatives
- Update reference materials with latest security research
- **NEW:** Monitor supply chain attack trends in crypto/web3/dev communities
- **NEW:** Update package name blocklist with known malicious packages
- **NEW:** Add Base64 pattern detection to automated scanner

### Automated Scanner Enhancements (Planned)

**Add to `scripts/scan_skill.py`:**
1. Dependency download count validation
2. Suspicious package name detection
3. Pre/post install script pattern matching
4. Environment variable access detection
5. Base64 payload identification (32+ chars, decode and analyze)
6. Network request endpoint validation
7. Lockfile integrity verification
8. Repository metadata analysis (if GitHub URL provided)

**Exit codes for CI/CD:**
- 0: PASS (no security issues)
- 1: WARN (MEDIUM severity, manual review needed)
- 2: FAIL (HIGH severity, block installation)
- 3: CRITICAL (supply chain attack detected)

### Feedback Loop

When security issues are found:
1. Document the pattern
2. Add to detection rules
3. Share with community
4. Improve security posture overall
5. **NEW:** Report malicious packages to npm registry
6. **NEW:** Document real-world attacks for educational purposes

## Tools

- **`scripts/scan_skill.py`** - Automated security scanner (planned enhancements for supply chain)
- **`references/security-checklist.md`** - Manual security checklist
- **`references/prompt-injection-patterns.md`** - Prompt injection detection guide
- **`references/scanner-usage-examples.md`** - Scanner output examples + troubleshooting
- **`references/cicd-integration-guide.md`** - GitHub Actions, GitLab CI, pre-commit hooks
- **`references/supply-chain-attack-patterns.md`** (TODO) - Documented attack vectors and detection methods

## Quick Reference Commands (Supply Chain Security)

```bash
# Check package downloads
npm view <package-name> --json | jq '{name, downloads: {lastWeek, lastMonth}}'

# Check repo age and stats
curl -s "https://api.github.com/repos/<owner>/<repo>"

# NPM audit without install
npm audit --json --package-lock-only

# Find env var access
grep -r "process\.env\[" --include="*.js" .

# Find Base64 payloads
grep -rE "[A-Za-z0-9+/]{32,}={0,2}" --include="*.js" -n

# Decode Base64
echo "<base64>" | base64 -d

# Find network requests
grep -rE "(fetch|axios)" --include="*.js" -B 3 -A 3

# Check what was installed
npm list --depth=0
```

Remember: Security is an ongoing process, not a one-time check. Regular audits and vigilance are essential to maintaining a secure Clawdbot environment. Supply chain attacks are increasingly sophisticated - always audit before installing.
