# Security-Check Skill Roadmap

This document outlines planned enhancements and future improvements for the security-check skill, inspired by industry-standard security tools like the [Gemini CLI Security Extension](https://github.com/gemini-cli-extensions/security).

---

## Current Status

### Completed ✅
- [x] Automated security scanner (`scripts/scan_skill.py`)
- [x] Prompt injection pattern detection
- [x] Hardcoded secrets scanning
- [x] Command-behavior alignment verification
- [x] Security severity levels (HIGH/MEDIUM/LOW)
- [x] Manual security checklist
- [x] Prompt injection patterns reference
- [x] Scanner usage examples documentation
- [x] CI/CD integration guide
- [x] GitHub Actions, GitLab CI, pre-commit hooks
- [x] Exit code handling (0=PASS, 1=WARN, 2=FAIL)

---

## Planned Enhancements

### Phase 1: Expand Vulnerability Categories 🎯 (High Priority)

**Estimated Effort:** 2-3 hours
**Impact:** High - Broader security coverage

**Tasks:**
- [ ] Add injection vulnerability patterns:
  - [ ] Cross-site scripting (XSS) detection
  - [ ] SQL injection (SQLi) patterns
  - [ ] Command injection detection
  - [ ] Server-side request forgery (SSRF) patterns
  - [ ] Server-side template injection (SSTI) patterns

- [ ] Add weak cryptography detection:
  - [ ] DES, Triple DES patterns
  - [ ] RC4 cipher patterns
  - [ ] ECB mode in block ciphers

- [ ] Add PII handling checks:
  - [ ] Logging of passwords/API keys/tokens
  - [ ] Personally identifiable information in logs
  - [ ] Insecure data transmission

- [ ] Add insecure deserialization:
  - [ ] `pickle.loads()` from untrusted sources
  - [ ] JSON `eval()` patterns
  - [ ] Unsafe deserialization in code

---

### Phase 2: AI-Powered Analysis Integration 🤖 (Medium Priority)

**Estimated Effort:** 4-6 hours
**Impact:** Medium - Reduced false positives, smarter detection

**Tasks:**
- [ ] Evaluate LLM integration options:
  - [ ] Claude API integration
  - [ ] Gemini API integration
  - [ ] Local LLM options (Ollama, etc.)

- [ ] Design AI analysis workflow:
  - [ ] Hybrid approach: Pattern matching + AI verification
  - [ ] Context-aware analysis for complex patterns
  - [ ] Intelligent recommendation generation

- [ ] Implement prototype:
  - [ ] Add `ai_analyze()` function to scanner
  - [ ] Test on known vulnerabilities
  - [ ] Compare precision/recall vs. pure pattern matching

---

### Phase 3: GitHub Actions Workflows ⚙️ (Medium Priority)

**Estimated Effort:** 2-3 hours
**Impact:** High - Better CI/CD integration

**Tasks:**
- [ ] Create pre-built workflow templates:
  - [ ] `.github/workflows/security-check-basic.yml` (fail on HIGH)
  - [ ] `.github/workflows/security-check-strict.yml` (fail on HIGH + MEDIUM)
  - [ ] `.github/workflows/security-check-pr.yml` (PR-focused analysis)

- [ ] Add workflow documentation:
  - [ ] Quick start guide for GitHub Actions
  - [ ] Configuration options
  - [ ] Example customizations

- [ ] Test workflows:
  - [ ] Create test repository
  - [ ] Run workflows on test PRs
  - [ ] Verify exit code handling

---

### Phase 4: Benchmarking Framework 📊 (Medium Priority)

**Estimated Effort:** 3-4 hours
**Impact:** Medium - Validate scanner effectiveness

**Tasks:**
- [ ] Create test dataset:
  - [ ] Use OpenSSF CVE Benchmark dataset
  - [ ] Add skill-specific test cases
  - [ ] Include false positive examples

- [ ] Build benchmarking script:
  - [ ] Measure precision and recall
  - [ ] Compare against baseline (current scanner)
  - [ ] Generate performance reports

- [ ] Set targets:
  - [ ] Precision: >90% (matches Gemini CLI Security)
  - [ ] Recall: >90% (matches Gemini CLI Security)
  - [ ] False positive rate: <5%

---

### Phase 5: Dependency Scanning Integration 🔍 (Low Priority)

**Estimated Effort:** 2-3 hours
**Impact:** Medium - Better supply chain security

**Tasks:**
- [ ] Integrate OSV-Scanner:
  - [ ] Install OSV-Scanner dependency
  - [ ] Add `scan_dependencies()` function
  - [ ] Cross-reference dependencies with OSV.dev

- [ ] Enhance existing dependency checks:
  - [ ] Improve npm audit integration
  - [ ] Improve pip-audit integration
  - [ ] Aggregate reports from multiple sources

- [ ] Add to workflow:
  - [ ] Include dependency scanning in CI/CD
  - [ ] Generate combined security report

---

### Phase 6: PR-Focused Analysis 🎯 (Low Priority)

**Estimated Effort:** 2-3 hours
**Impact:** Medium - Faster analysis for large codebases

**Tasks:**
- [ ] Add diff-based scanning:
  - [ ] Scan only changed files in PRs
  - [ ] Use `git diff` to identify modifications
  - [ ] Focus analysis on new/changed code

- [ ] Context-aware analysis:
  - [ ] Understand surrounding code context
  - [ ] Provide PR-specific recommendations
  - [ ] Generate PR comments with findings

---

## Inspiration Sources

### Gemini CLI Security Extension
- **Repository:** https://github.com/gemini-cli-extensions/security
- **Features:**
  - AI-powered security analysis (Gemini LLM)
  - PR-focused code change analysis
  - Dependency scanning (OSV-Scanner)
  - GitHub Actions integration
  - Comprehensive vulnerability categories
  - Benchmarking (90% precision, 93% recall)

### Vulnerability Categories from Gemini CLI
- Secrets management
- Insecure data handling
- Injection vulnerabilities (XSS, SQLi, command injection, SSRF, SSTI)
- Authentication issues (bypass, weak tokens, insecure password reset)
- LLM safety (prompt injection, improper output handling, insecure tool usage)

---

## Timeline

### Q1 2026 (Feb - Mar)
- ✅ **Feb 7:** Documentation complete (scanner-usage-examples, cicd-integration-guide)
- 🎯 **Feb 8-15:** Phase 1 - Expand vulnerability categories
- 🤖 **Feb 16-28:** Phase 2 - AI-powered analysis integration (prototype)

### Q2 2026 (Apr - Jun)
- ⚙️ **Apr 1-15:** Phase 3 - GitHub Actions workflows
- 📊 **Apr 16-30:** Phase 4 - Benchmarking framework

### Q3 2026 (Jul - Sep)
- 🔍 **Jul 1-15:** Phase 5 - Dependency scanning integration
- 🎯 **Jul 16-31:** Phase 6 - PR-focused analysis

### Q4 2026 (Oct - Dec)
- 🧪 **Oct - Nov:** Testing and validation
- 📝 **Dec:** Documentation updates and release

---

## Contributing

Contributions are welcome! If you'd like to help implement any of these enhancements:

1. Check this roadmap for available tasks
2. Comment on GitHub Issues to claim a task
3. Submit a PR with your implementation
4. Include tests for new features
5. Update documentation as needed

---

## Questions?

If you have questions or suggestions for this roadmap:
- Open an issue on GitHub
- Contact the maintainer
- Join the discussion in the repository

---

**Last Updated:** February 7, 2026
**Next Milestone:** Phase 1 - Expand Vulnerability Categories (Feb 8-15)
**Maintainer:** Raimon (@wolffan)
