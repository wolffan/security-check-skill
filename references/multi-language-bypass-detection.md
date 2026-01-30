# Multi-Language Bypass Detection

## Overview

The security-check skill now includes comprehensive detection of language-based prompt injection attempts. Attackers often translate malicious prompts into non-English languages to bypass security filters trained primarily on English patterns.

## Supported Languages

The scanner detects bypass patterns in 8 major languages:

### 1. Spanish
- **Override patterns**: `ignora instrucciones`, `ignorar todas las instrucciones`
- **Bypass patterns**: `pasa por alto restricciones`

### 2. French
- **Override patterns**: `ignorez toutes les instructions`
- **Bypass patterns**: `contournez restrictions`, `passez outre`

### 3. Chinese (Simplified)
- **Override patterns**: `忽略指示`, `无视指令`
- **Bypass patterns**: `绕过限制`

### 4. Arabic
- **Override patterns**: `تجاهل التعليمات`
- **Bypass patterns**: `تجاوز القيود`

### 5. Russian
- **Override patterns**: `игнорируйте инструкции`
- **Bypass patterns**: `обойти ограничения`

### 6. German
- **Override patterns**: `ignorieren alle anweisungen`
- **Bypass patterns**: `umgehen sicherheitseinschränkungen`

### 7. Portuguese
- **Override patterns**: `ignore todas as instruções`
- **Bypass patterns**: `contornar restrições`

## Detection Method

### Unicode Normalization

Text is processed through NFKC (Normalization Form Compatibility Composition) normalization before pattern matching. This:

1. **Decomposes compatibility characters**: Converts equivalent characters to canonical forms
2. **Handles homoglyphs**: Makes look-alike characters from different alphabets comparable
3. **Preserves original text**: Non-ASCII characters are retained for accurate matching
4. **Removes invisible characters**: Zero-width and control format characters are stripped

### Pattern Categories

The scanner detects two types of malicious intent:

1. **Override patterns**: Attempts to replace or ignore system instructions
2. **Bypass patterns**: Attempts to circumvent security restrictions

Both are classified as HIGH severity threats.

## Example Output

### Successful Detection

```json
{
  "severity": "HIGH",
  "file": "SKILL.md",
  "issue": "Potential language-based bypass: Spanish \"override\" pattern detected",
  "recommendation": "Prompt attempts to bypass security via Spanish language translation",
  "context": "Language-based prompt injection"
}
```

### Unicode Obfuscation Detection

```json
{
  "severity": "MEDIUM",
  "file": "SKILL.md",
  "issue": "Unicode escape sequences detected",
  "recommendation": "Text may contain obfuscated characters",
  "context": "Unicode obfuscation"
}
```

## Testing

Comprehensive test suites are available:

- `/tmp/test-spanish` - Spanish bypass detection
- `/tmp/test-language-bypass/skill` - Multi-language detection
- `/tmp/comprehensive-bypass-tests/skill` - All 8 languages
- `/tmp/unicode-obfuscation-test/skill` - Unicode obfuscation techniques

### Run Tests

```bash
cd /Users/rlapuente/clawd/skills/security-check
python3 scripts/scan_skill.py /tmp/test-spanish
```

## Implementation Details

The feature is implemented in `scripts/scan_skill.py`:

1. **Pattern Loading**: `_load_language_patterns()` - Returns list of (pattern, language, intent) tuples
2. **Normalization**: `_normalize_text()` - Applies NFKC normalization
3. **Detection**: `_check_language_bypass()` - Scans for language patterns
4. **Obfuscation Check**: `_check_unicode_anomalies()` - Detects encoding tricks

## Pattern Syntax

Patterns use Python regex with these constructs:

- `\s+` - One or more whitespace characters
- `(?:group)?` - Optional non-capturing group
- `|` - Alternation (OR)
- `.*` - Any characters (greedy)

Example Spanish pattern:
```regex
ignor(a|e|ar)\s+(?:todas?\s+(?:las\s+)?)?instrucciones
```

Matches:
- `ignora instrucciones`
- `ignorar instrucciones`
- `ignora todas las instrucciones`
- `ignorar todas las instrucciones`

## False Positive Mitigation

Legitimate non-English content in skill descriptions (e.g., Spanish comments, Chinese examples) should:

1. Use neutral language that doesn't match override/bypass patterns
2. Avoid direct translations of instruction words
3. Context should clearly indicate documentation/educational content

If false positives occur, review the specific pattern and context. Consider adjusting the pattern regex to be more specific or adding whitelist exceptions.

## Extension

To add support for additional languages:

1. Identify common prompt injection phrases in the target language
2. Translate "override" and "bypass" concepts
3. Create regex patterns with appropriate whitespace handling
4. Add to the `_load_language_patterns()` return list with format:
   ```python
   (r'pattern_regex', 'LanguageName', 'intent_type'),
   ```

## References

Based on security research from:
- OWASP GenAI Security Project - LLM01: Prompt Injection
- ArXiv:2307.15043 - Universal and Transferable Adversarial Attacks on Aligned Language Models
- Known multi-language prompt injection techniques

All patterns are sourced from documented security research, not from AI analysis, to avoid exposing detection methods.
