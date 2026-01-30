#!/usr/bin/env python3
"""
Security scanner for Clawdbot skills.
Scans skill files for potential security issues.
"""

import os
import re
import sys
import json
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional

class SecurityScanner:
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.issues = []
        self.warnings = []
        self.passed = []
        self.file_read_errors = []
        
        # Load multi-language patterns for bypass detection
        self.language_patterns = self._load_language_patterns()

    def _load_language_patterns(self) -> List[tuple[str, str, str]]:
        """Load override patterns in multiple languages."""
        return [
            # Spanish
            (r'ignora\s+instrucciones', 'Spanish', 'override'),
            (r'ignor(a|e|ar)\s+(?:todas?\s+(?:las\s+)?)?instrucciones', 'Spanish', 'override'),
            (r'pasa\s+por\s+alto\s+restricciones', 'Spanish', 'bypass'),
            
            # French
            (r'ignorez\s+toutes\s+les\s+instructions', 'French', 'override'),
            (r'contournez\s+restrictions', 'French', 'bypass'),
            (r'passez\s+outre', 'French', 'bypass'),
            
            # Chinese (Simplified)
            (r'忽略.*指示', 'Chinese', 'override'),
            (r'绕过.*限制', 'Chinese', 'bypass'),
            (r'无视.*指令', 'Chinese', 'override'),
            
            # Arabic
            (r'تجاهل.*التعليمات', 'Arabic', 'override'),
            (r'تجاوز.*القيود', 'Arabic', 'bypass'),
            
            # Russian
            (r'игнорируйте.*инструкции', 'Russian', 'override'),
            (r'обойти.*ограничения', 'Russian', 'bypass'),
            
            # German
            (r'ignorieren\s+alle\s+anweisungen', 'German', 'override'),
            (r'umgehen\s+sicherheitseinschränkungen', 'German', 'bypass'),
            
            # Portuguese
            (r'ignore\s+todas\s+as\s+instruções', 'Portuguese', 'override'),
            (r'contornar\s+restrições', 'Portuguese', 'bypass'),
        ]
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize Unicode text to handle variations while preserving original characters.
        Uses NFKC to convert compatible characters and handle homoglyphs.
        Does NOT convert to ASCII - keeps non-ASCII text intact for pattern matching.
        """
        # NFKC normalization: converts compatible characters and handles homoglyphs
        # This makes 'é' and 'é' equivalent, and similar character variations
        normalized = unicodedata.normalize('NFKC', text)
        
        # Optionally: remove zero-width and invisible characters that hide patterns
        normalized = ''.join(c for c in normalized 
                            if unicodedata.category(c) != 'Cf')  # Control format characters
        
        return normalized

    def _safe_read_file(self, file_path: Path) -> Optional[str]:
        """
        Safely read a file with error handling.
        Returns file content or None if an error occurs.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError as e:
            error_msg = f'Encoding error reading file: {e}'
            self.warnings.append({
                'severity': 'LOW',
                'file': str(file_path.relative_to(self.skill_path)),
                'issue': error_msg,
                'recommendation': 'Check file encoding (UTF-8 expected)'
            })
            self.file_read_errors.append({
                'file': str(file_path.relative_to(self.skill_path)),
                'error': error_msg
            })
            return None
        except (IOError, OSError) as e:
            error_msg = f'File read error: {e}'
            self.warnings.append({
                'severity': 'LOW',
                'file': str(file_path.relative_to(self.skill_path)),
                'issue': error_msg,
                'recommendation': 'Check file permissions and accessibility'
            })
            self.file_read_errors.append({
                'file': str(file_path.relative_to(self.skill_path)),
                'error': error_msg
            })
            return None
        except Exception as e:
            error_msg = f'Unexpected error reading file: {e}'
            self.warnings.append({
                'severity': 'LOW',
                'file': str(file_path.relative_to(self.skill_path)),
                'issue': error_msg,
                'recommendation': 'Review file for unexpected content'
            })
            self.file_read_errors.append({
                'file': str(file_path.relative_to(self.skill_path)),
                'error': error_msg
            })
            return None

    def _check_language_bypass(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """
        Check for language-based prompt injection attempts across multiple languages.
        Normalizes text first to catch Unicode obfuscation.
        """
        normalized = self._normalize_text(content)
        issues_found = []
        
        for pattern, language, intent in self.language_patterns:
            if re.search(pattern, normalized, re.IGNORECASE):
                issues_found.append({
                    'severity': 'HIGH',
                    'file': str(file_path.relative_to(self.skill_path)),
                    'issue': f'Potential language-based bypass: {language} "{intent}" pattern detected',
                    'recommendation': f'Prompt attempts to bypass security via {language} language translation',
                    'context': 'Language-based prompt injection'
                })
        
        return issues_found
    
    def _check_unicode_anomalies(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Check for Unicode obfuscation tricks that bypass pattern matching.
        """
        issues_found = []
        
        # Check for unicode escapes
        if re.search(r'\\u[0-9a-fA-F]{4}', content):
            issues_found.append({
                'severity': 'MEDIUM',
                'file': str(file_path.relative_to(self.skill_path)),
                'issue': 'Unicode escape sequences detected',
                'recommendation': 'Text may contain obfuscated characters',
                'context': 'Unicode obfuscation'
            })
        
        # Check for HTML entities
        if re.search(r'&#\d+;', content):
            issues_found.append({
                'severity': 'MEDIUM',
                'file': str(file_path.relative_to(self.skill_path)),
                'issue': 'HTML entity encoding detected',
                'recommendation': 'Text may contain obfuscated characters',
                'context': 'HTML entity obfuscation'
            })
        
        return issues_found

    def scan(self) -> Dict[str, Any]:
        """Run all security checks on the skill."""
        results = {
            'skill_name': self.skill_path.name,
            'issues': [],
            'warnings': [],
            'passed': [],
            'file_read_errors': [],
            'summary': ''
        }

        # Check SKILL.md
        skill_md = self.skill_path / "SKILL.md"
        if skill_md.exists():
            self._check_skill_md(skill_md)
        else:
            results['issues'].append({
                'severity': 'HIGH',
                'file': 'SKILL.md',
                'issue': 'Missing required SKILL.md file'
            })

        # Scan scripts for dangerous patterns
        scripts_dir = self.skill_path / "scripts"
        if scripts_dir.exists():
            self._scan_scripts(scripts_dir)

        # Scan references for suspicious content
        refs_dir = self.skill_path / "references"
        if refs_dir.exists():
            self._scan_references(refs_dir)

        results['issues'] = self.issues
        results['warnings'] = self.warnings
        results['passed'] = self.passed
        results['file_read_errors'] = self.file_read_errors

        # Generate summary
        if self.issues:
            results['summary'] = f"SECURITY ISSUES FOUND: {len(self.issues)} issue(s), {len(self.warnings)} warning(s)"
        elif self.warnings:
            results['summary'] = f"WARNINGS: {len(self.warnings)} warning(s) (no critical issues)"
        else:
            results['summary'] = "PASSED: No security issues found"

        if self.file_read_errors:
            results['summary'] += f" | {len(self.file_read_errors)} file read error(s)"

        return results

    def _check_skill_md(self, skill_md: Path):
        """Check SKILL.md for security concerns."""
        content = self._safe_read_file(skill_md)
        if content is None:
            return  # Error already recorded in _safe_read_file

        # Check for prompt injection patterns in the skill description
        prompt_injection_patterns = [
            r'ignore (previous|above|earlier)',
            r'disregard (previous|above|earlier)',
            r'forget (previous|above|earlier)',
            r'overwrite (previous|above|earlier)',
            r'bypass (security|restrictions|filters)',
            r'admin.*override',
            r'system.*override',
            r'replace.*instructions',
        ]

        for pattern in prompt_injection_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.issues.append({
                    'severity': 'HIGH',
                    'file': 'SKILL.md',
                    'issue': f'Potential prompt injection pattern detected: {pattern}',
                    'recommendation': 'Review and remove suspicious instruction patterns'
                })

        # Check for external network calls in description
        network_patterns = [
            r'curl.*http[s]?://',
            r'wget.*http[s]?://',
            r'fetch.*http[s]?://',
            r'request.*http[s]?://',
        ]

        for pattern in network_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.warnings.append({
                    'severity': 'MEDIUM',
                    'file': 'SKILL.md',
                    'issue': f'External network call pattern: {pattern}',
                    'recommendation': 'Verify all network calls are intentional and secure'
                })
        
        # NEW: Check for language-based bypasses
        language_issues = self._check_language_bypass(content, skill_md)
        self.issues.extend(language_issues)
        
        # NEW: Check for Unicode anomalies
        unicode_issues = self._check_unicode_anomalies(content, skill_md)
        self.issues.extend(unicode_issues)
        
        self.passed.append({
            'file': 'SKILL.md',
            'check': 'Multi-language prompt injection scan',
            'status': 'Completed'
        })

    def _scan_scripts(self, scripts_dir: Path):
        """Scan scripts directory for dangerous patterns."""
        dangerous_patterns = {
            'HIGH': [
                (r'os\.system\([^)]*rm\s+-rf', 'Deletion command'),
                (r'os\.system\([^)]*rm\s+-r/', 'Recursive deletion'),
                (r'subprocess\.call\([^)]*rm', 'Subprocess deletion'),
                (r'exec\([^)]*rm', 'Exec deletion'),
                (r'eval\(', 'eval() usage'),
                (r'__import__\([^)]*os', 'Dynamic os import'),
                (r'pickle\.load\(', 'pickle.load() - code execution risk'),
                (r'pickle\.loads\(', 'pickle.loads() - code execution risk'),
                (r'yaml\.load\([^)]*Loader=(?!SafeLoader)', 'yaml.load() without SafeLoader'),
                (r'yaml\.load\(\)', 'yaml.load() without SafeLoader'),
                (r'marshal\.load\(', 'marshal.load() - code execution risk'),
                (r'marshal\.loads\(', 'marshal.loads() - code execution risk'),
                (r'verify=False', 'SSL verification bypass'),
            ],
            'MEDIUM': [
                (r'os\.system\(', 'os.system() usage'),
                (r'subprocess\.(call|run|Popen).*shell=True', 'shell=True usage'),
                (r'open\([^)]*[\'"].*password[\'"]', 'Password in file'),
                (r'open\([^)]*[\'"].*secret[\'"]', 'Secret in file'),
                (r'open\([^)]*[\'"].*token[\'"]', 'Token in file'),
                (r'open\([^)]*[\'"].*api_key[\'"]', 'API key in file'),
            ]
        }

        # Shell script specific patterns
        shell_patterns = {
            'HIGH': [
                (r'curl\s+.*\|\s*(sh|bash)', 'curl piped to shell - arbitrary code execution'),
                (r'wget\s+-O-\s+.*\|\s*(sh|bash)', 'wget piped to shell - arbitrary code execution'),
                (r'base64\s+-d\s+.*\|\s*(sh|bash)', 'base64 decode piped to shell - encoded execution'),
                (r'rm\s+-rf\s+/', 'Root deletion command'),
                (r'chmod\s+777', 'Insecure permissions'),
            ],
            'MEDIUM': [
                (r'eval\s+', 'eval in shell script'),
                (r'export\s+.*password', 'Password in environment variable'),
                (r'export\s+.*secret', 'Secret in environment variable'),
                (r'export\s+.*token', 'Token in environment variable'),
            ]
        }

        # Supported file extensions
        file_extensions = ['.py', '.sh', '.bash', '.js', '.ts', '.rb', '.env', '.yaml', '.yml', '.json', '.toml']

        # Walk through all files including hidden ones
        for root, dirs, files in os.walk(scripts_dir):
            # Don't skip hidden directories
            for filename in files:
                file_path = Path(root) / filename
                ext = file_path.suffix.lower()

                # Check if file extension is supported
                if ext not in file_extensions:
                    continue

                content = self._safe_read_file(file_path)
                if content is None:
                    continue  # Error already recorded

                # Choose appropriate patterns based on file type
                if ext in ['.sh', '.bash']:
                    patterns = shell_patterns
                else:
                    patterns = dangerous_patterns

                for severity, pattern_list in patterns.items():
                    for pattern, desc in pattern_list:
                        if re.search(pattern, content, re.IGNORECASE):
                            issue_data = {
                                'severity': severity,
                                'file': str(file_path.relative_to(self.skill_path)),
                                'issue': f'{desc} detected',
                                'recommendation': 'Review and ensure this is intentional and safe'
                            }
                            if severity == 'HIGH':
                                self.issues.append(issue_data)
                            else:
                                self.warnings.append(issue_data)

        self.passed.append({
            'directory': 'scripts/',
            'check': 'Dangerous pattern scan',
            'status': 'Completed'
        })

    def _scan_references(self, refs_dir: Path):
        """Scan references directory for suspicious content."""
        secret_patterns = [
            r'password\s*[=:]\s*[\'"][\w]+[\'"]',
            r'secret\s*[=:]\s*[\'"][\w]+[\'"]',
            r'token\s*[=:]\s*[\'"][\w]{20,}[\'"]',
            r'api[_-]?key\s*[=:]\s*[\'"][\w]{20,}[\'"]',
            r'aws[_-]?(access[_-]?key|secret[_-]?key)\s*[=:]\s*[\'"][\w]{20,}[\'"]',
        ]

        for ref_file in refs_dir.glob('*.md'):
            content = self._safe_read_file(ref_file)
            if content is None:
                continue  # Error already recorded

            for pattern in secret_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    self.issues.append({
                        'severity': 'HIGH',
                        'file': str(ref_file.relative_to(self.skill_path)),
                        'issue': f'Potential hardcoded secrets detected: {len(matches)} match(es)',
                        'recommendation': 'Remove hardcoded secrets and use proper secret management'
                    })

            # Check for suspicious external URLs
            url_pattern = r'https?://[^\s\)]+'
            urls = re.findall(url_pattern, content)
            for url in urls:
                if any(domain in url.lower() for domain in ['pastebin', 'raw.githubusercontent', 'bit.ly', 't.co']):
                    self.warnings.append({
                        'severity': 'LOW',
                        'file': str(ref_file.relative_to(self.skill_path)),
                        'issue': f'Suspicious URL detected: {url}',
                        'recommendation': 'Verify this URL is legitimate and safe'
                    })

        self.passed.append({
            'directory': 'references/',
            'check': 'Secret and URL scan',
            'status': 'Completed'
        })

def main():
    if len(sys.argv) < 2:
        print("Usage: python scan_skill.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    scanner = SecurityScanner(skill_path)
    results = scanner.scan()

    # Print results
    print(json.dumps(results, indent=2))

    # Exit codes for CI/CD integration:
    # - Exit code 2 when HIGH severity issues found
    # - Exit code 1 when MEDIUM severity warnings found
    # - Exit code 0 when clean
    if scanner.issues:
        sys.exit(2)
    elif scanner.warnings:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
