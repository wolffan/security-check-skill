# Gemini CLI Security Extension - Inspiration Analysis

**Analysis Date:** February 7, 2026
**Source:** https://github.com/gemini-cli-extensions/security
**Purpose:** Identify adoptable features for security-check skill

---

## Overview

The Gemini CLI Security Extension is an open-source AI-powered security analysis tool for the Gemini CLI. It provides intelligent, context-aware security analysis of code changes and pull requests.

### Key Features
- **AI-powered security analysis** - Leverages Gemini's LLM capabilities
- **PR-focused analysis** - Specifically designed to analyze code changes within pull requests
- **Dependency scanning** - Uses OSV-Scanner to identify known vulnerabilities
- **GitHub Actions integration** - Pre-built workflows for automated security checks
- **Benchmarked performance** - 90% precision, 93% recall on real vulnerabilities

### Vulnerability Categories Detected

1. **Secrets Management**
   - Hardcoded secrets (API keys, private keys, passwords)
   - Symmetric encryption keys in source code

2. **Insecure Data Handling**
   - Weak cryptographic algorithms (DES, Triple DES, RC4, ECB mode)
   - Logging of sensitive information (passwords, PII, API keys, tokens)
   - PII handling violations
   - Insecure deserialization

3. **Injection Vulnerabilities**
   - Cross-site scripting (XSS)
   - SQL injection (SQLi)
   - Command injection
   - Server-side request forgery (SSRF)
   - Server-side template injection (SSTI)

4. **Authentication**
   - Authentication bypass
   - Weak or predictable session tokens
   - Insecure password reset

5. **LLM Safety**
   - Insecure Prompt Handling (Prompt Injection)
   - Improper Output Handling
   - Insecure Plugin and Tool Usage

---

## Adoptable Features for Security-Check Skill

### High Priority (Easy Integration)

#### 1. Expand Vulnerability Categories

**Current State:** Security-check detects prompt injection, hardcoded secrets, and dangerous file operations.

**Adopt from Gemini CLI:**
- **Injection Vulnerabilities:**
  - XSS detection patterns (unsanitized user input in HTML)
  - SQLi patterns (string concatenation with user input)
  - Command injection patterns (user input in system commands)
  - SSRF patterns (URLs from user input without validation)
  - SSTI patterns (user input in templates)

- **Weak Cryptography:**
  - DES, Triple DES detection
  - RC4 cipher patterns
  - ECB mode in block ciphers

- **PII Handling:**
  - Logging of sensitive information (passwords, API keys, tokens)
  - PII in application logs

- **Insecure Deserialization:**
  - `pickle.loads()` from untrusted sources
  - JSON `eval()` patterns
  - Unsafe deserialization in code

#### 2. Enhanced Secret Detection

**Current State:** Basic regex patterns for API keys, passwords, tokens.

**Adopt from Gemini CLI:**
- Expand patterns to detect encoding tricks (base64, hex)
- Detect symmetric encryption keys embedded in code
- Detect session tokens and authentication cookies

### Medium Priority (Requires Enhancement)

#### 3. AI-Powered Analysis

**Current State:** Pure pattern matching with regex.

**Adopt from Gemini CLI:**
- Hybrid approach: Pattern matching + AI verification
- Context-aware analysis for complex patterns
- Intelligent recommendation generation
- Reduced false positives through AI verification

**Implementation Options:**
- Claude API integration
- Gemini API integration
- Local LLM options (Ollama, Llama)

#### 4. GitHub Actions Workflows

**Current State:** Basic workflow documentation in cicd-integration-guide.md.

**Adopt from Gemini CLI:**
- Create pre-built workflow templates:
  - `security-check-basic.yml` (fail on HIGH)
  - `security-check-strict.yml` (fail on HIGH + MEDIUM)
  - `security-check-pr.yml` (PR-focused analysis)
- Add workflow customization examples
- Include configuration options

#### 5. Benchmarking Framework

**Current State:** No benchmarking.

**Adopt from Gemini CLI:**
- Create test dataset with known vulnerabilities
- Build benchmarking script to measure precision/recall
- Set performance targets:
  - Precision: >90% (matches Gemini CLI)
  - Recall: >90% (matches Gemini CLI)
  - False positive rate: <5%

### Low Priority (Future Enhancement)

#### 6. Dependency Scanning Integration

**Current State:** Manual npm audit / pip-audit integration.

**Adopt from Gemini CLI:**
- Integrate OSV-Scanner for known vulnerabilities
- Cross-reference dependencies with OSV.dev
- Aggregate reports from multiple sources

#### 7. PR-Focused Analysis

**Current State:** Full skill scans.

**Adopt from Gemini CLI:**
- Scan only changed files in PRs
- Use `git diff` to identify modifications
- Focus analysis on new/changed code
- Provide PR-specific recommendations

---

## Comparison: Current vs. Potential

| Feature | Current (security-check) | Potential (inspired by Gemini CLI) |
|---------|------------------------|-------------------------------------|
| **Analysis Method** | Pattern matching (regex) | AI-powered (LLM) + pattern matching |
| **Scope** | Prompt injection, secrets, file access | Injection types, weak crypto, PII, auth issues |
| **Dependency Scanning** | npm audit / pip-audit (manual) | OSV-Scanner integration (automated) |
| **GitHub Integration** | Basic workflows | Pre-built, tested workflows |
| **Benchmarking** | None | Precision/recall metrics |
| **Focus** | Skills for Clawdbot | Code changes, PRs, repositories |
| **Exit Codes** | 0=PASS, 1=WARN, 2=FAIL | Same, with severity levels |

---

## Performance Targets

Based on Gemini CLI Security Extension benchmarks:

| Metric | Target | Gemini CLI Achievement |
|--------|---------|------------------------|
| **Precision** | >90% | 90% |
| **Recall** | >90% | 93% |
| **False Positive Rate** | <5% | 10% (100% - 90%) |

---

## Implementation Roadmap

### Phase 1: Expand Vulnerability Categories
- Add injection vulnerability patterns
- Add weak cryptography detection
- Add PII handling checks
- Add insecure deserialization detection

### Phase 2: AI-Powered Analysis
- Evaluate LLM integration options
- Design AI analysis workflow
- Implement prototype
- Test on known vulnerabilities

### Phase 3: GitHub Actions Workflows
- Create pre-built workflow templates
- Add workflow documentation
- Test workflows on test repository

### Phase 4: Benchmarking Framework
- Create test dataset
- Build benchmarking script
- Measure precision/recall
- Compare against baseline

### Phase 5: Dependency Scanning Integration
- Integrate OSV-Scanner
- Enhance existing dependency checks
- Add to CI/CD workflow

### Phase 6: PR-Focused Analysis
- Add diff-based scanning
- Context-aware analysis
- PR-specific recommendations

---

## Resources

### Gemini CLI Security Extension
- **Repository:** https://github.com/gemini-cli-extensions/security
- **License:** Apache 2.0
- **Documentation:** https://github.com/gemini-cli-extensions/security#readme
- **Issues:** https://github.com/gemini-cli-extensions/security/issues

### Related Tools
- **OSV-Scanner:** https://github.com/google/osv-scanner
- **OSV.dev:** https://osv.dev (Open Source Vulnerabilities database)
- **OpenSSF CVE Benchmark:** https://github.com/ossf-cve-benchmark/ossf-cve-benchmark

---

## Notes

### License Compatibility
- Gemini CLI Security Extension: Apache 2.0
- Compatible with most open-source licenses (MIT, Apache 2.0, BSD)
- Check license compatibility before copying code

### Benchmark Dataset
- OpenSSF CVE Benchmark dataset available
- Contains real-world vulnerabilities
- TypeScript / JavaScript repositories
- Pre-commit and post-commit pairs for testing

### Performance Metrics
- Gemini CLI achieved 90% precision, 93% recall
- Used OpenSSF CVE Benchmark dataset
- Manual review for small dataset
- Planning to automate evaluation framework

---

## Conclusion

The Gemini CLI Security Extension provides an excellent blueprint for enhancing the security-check skill. Key adoptable features include:

1. **Expanded vulnerability categories** (injection types, weak crypto, PII)
2. **AI-powered analysis** for reduced false positives
3. **Pre-built GitHub Actions workflows** for easy CI/CD integration
4. **Benchmarking framework** for performance validation
5. **Dependency scanning integration** for supply chain security
6. **PR-focused analysis** for faster scans on large codebases

By adopting these features, the security-check skill can achieve comparable performance (90%+ precision and recall) and provide a more comprehensive security analysis for Clawdbot skills.

---

**Analysis Date:** February 7, 2026
**Next Steps:** Implement Phase 1 (Expand Vulnerability Categories)
**Timeline:** Q1-Q2 2026
**Maintainer:** Raimon (@wolffan)
