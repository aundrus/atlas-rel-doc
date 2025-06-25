#!/usr/bin/env python3
"""
Python migration of ardoc_errortester.pl using Claude Sonnet
Author: Migration by Claude Sonnet (original: A. Undrus)

This script analyzes log files for errors, warnings, and success patterns,
generating HTML reports for build and test analysis.
"""

import os
import sys
import re
import argparse
import shutil
from pathlib import Path
from html import escape
from typing import Dict, List, Tuple, Optional


class LogPatterns:
    """Container for all pattern definitions and matching logic."""
    
    def __init__(self, env_vars: Dict[str, str], is_testing: bool = False, is_qa: bool = False, light_mode: bool = False):
        self.env = env_vars
        self.is_testing = is_testing
        self.is_qa = is_qa
        self.light_mode = light_mode
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Initialize all pattern arrays based on mode."""
        # Error patterns
        self.error_patterns = [
            ": error:", "CMake Error", "runtime error:", 
            "No rule to make target", self.env.get('ARDOC_BUILD_FAILURE_PATTERN', 'CVBFGG'),
            "raceback (most recent", "error: ld", "error: Failed to execute", "no build logfile"
        ]
        self.error_ignore = ["CVBFGG"] * len(self.error_patterns)
        
        # Warning patterns
        self.warning_patterns = [
            "Errors/Problems found", "CMake Warning", "CMake Deprecation Warning",
            "Error in", "control reaches end of non-void", "suggest explicit braces",
            "> Warning:", "type qualifiers ignored on function return type",
            r"\[-Wsequence-point\]", "mission denied", "nvcc warning :", "Warning: Fortran"
        ]
        self.warning_ignore = [
            "Errors/Problems found : 0", "CVBFGG", "CVBFGG", "CVBFGG", "/external",
            "/external", "> Warning: template", "/external", "/external", "CVBFGG", "CVBFGG", "CVBFGG"
        ]
        
        # Minor warning patterns
        self.minor_patterns = [
            ": warning: ", "Warning: the last line", "Warning: Unused class rule",
            r"Warning:\s.*rule", "#pragma message:", r"WARNING\s+.*GAUDI"
        ]
        self.minor_ignore = ["make[", "CVBFGG", "CVBFGG", "CVBFGG", "CVBFGG", "ClassIDSvc"]
        
        # Success patterns
        self.success_patterns = ["Package build succeeded"]
        
        # Test-specific patterns
        if self.is_testing or self.is_qa:
            self._setup_test_patterns()
        
        # Apply light mode restrictions
        if self.light_mode:
            self._apply_light_mode()
    
    def _setup_test_patterns(self):
        """Setup patterns specific to testing modes."""
        if self.is_qa:
            self.test_failure_patterns = [
                "*Timeout", "time quota spent", "*Failed", "ERROR_MESSAGE",
                "severity=FATAL", "Error: execution_error", "command not found",
                "tests FAILED", "tester: Error", "Errors while running CTest"
            ]
        else:
            self.test_failure_patterns = [
                "test issue message: Timeout", "test status fail", "*Failed",
                "TEST FAILURE", "severity=FATAL", ": FAILURE ", "command not found",
                "ERROR_MESSAGE", " ERROR ", "exit code: 143", "time quota spent"
            ]
        
        self.test_failure_ignore = ["CVBFGG"] * len(self.test_failure_patterns)
        
        # Test warning patterns
        test_warning_pattern = self.env.get('ARDOC_QA_WARNING_PATTERN' if self.is_qa 
                                          else 'ARDOC_TEST_WARNING_PATTERN', '')
        self.test_warning_patterns = [
            test_warning_pattern, "raceback (most recent", "file not found", "CVBFGG"
        ]
        
        # Test success patterns
        test_success_pattern = self.env.get('ARDOC_QA_SUCCESS_PATTERN' if self.is_qa 
                                          else 'ARDOC_TEST_SUCCESS_PATTERN', '')
        self.test_success_patterns = ["Info: test completed", test_success_pattern]
    
    def _apply_light_mode(self):
        """Apply light mode restrictions to patterns."""
        if self.is_testing or self.is_qa:
            # Disable most patterns in light mode
            for i in range(len(self.test_failure_patterns)):
                self.test_failure_patterns[i] = "CVBFGG"
            
            # Keep only critical patterns
            self.test_failure_patterns[0] = "test issue message: Timeout"
            self.test_failure_patterns[1] = "test status fail"
            self.test_failure_patterns[2] = "TEST FAILURE"


class LogAnalyzer:
    """Main log analysis class."""
    
    def __init__(self, patterns: LogPatterns):
        self.patterns = patterns
        self.reset_counters()
    
    def reset_counters(self):
        """Reset all analysis counters."""
        self.error_matches = []
        self.warning_matches = []
        self.minor_matches = []
        self.first_error = None
        self.first_warning = None
        self.first_minor = None
    
    def analyze_file(self, log_file: Path) -> Tuple[int, str, int, str]:
        """
        Analyze a log file and return problem level, message, line number, and line content.
        
        Returns:
            Tuple of (problem_level, message, line_number, line_content)
            problem_level: 0=no problems, 0.5=minor, 1=warning, 2=error
        """
        self.reset_counters()
        
        try:
            with open(log_file, 'r', errors='ignore', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    self._analyze_line(line, line_num)
        except IOError as e:
            return 2, f"Failed to read log file: {e}", 0, ""
        
        return self._determine_result()
    
    def _analyze_line(self, line: str, line_num: int):
        """Analyze a single line for patterns."""
        line_stripped = line.strip()
        
        # Check error patterns
        if self.patterns.is_testing or self.patterns.is_qa:
            patterns = self.patterns.test_failure_patterns
            ignore_patterns = self.patterns.test_failure_ignore
        else:
            patterns = self.patterns.error_patterns
            ignore_patterns = self.patterns.error_ignore
        
        for pattern, ignore in zip(patterns, ignore_patterns):
            if self._matches_pattern(line, pattern, ignore):
                if not self.first_error:
                    self.first_error = (line_num, line_stripped, pattern)
                self.error_matches.append((line_num, pattern))
                return  # Stop at first error pattern match
        
        # Check warning patterns
        if not (self.patterns.is_testing or self.patterns.is_qa):
            for pattern, ignore in zip(self.patterns.warning_patterns, self.patterns.warning_ignore):
                if self._matches_pattern(line, pattern, ignore):
                    if not self.first_warning:
                        self.first_warning = (line_num, line_stripped, pattern)
                    self.warning_matches.append((line_num, pattern))
                    return
        
        # Check minor warning patterns
        minor_patterns = (self.patterns.minor_patterns if not (self.patterns.is_testing or self.patterns.is_qa)
                         else getattr(self.patterns, 'test_warning_patterns', []))
        minor_ignore = (self.patterns.minor_ignore if not (self.patterns.is_testing or self.patterns.is_qa)
                       else ["CVBFGG"] * len(minor_patterns))
        
        for pattern, ignore in zip(minor_patterns, minor_ignore):
            if self._matches_pattern(line, pattern, ignore):
                if not self.first_minor:
                    self.first_minor = (line_num, line_stripped, pattern)
                self.minor_matches.append((line_num, pattern))
                return
    
    def _matches_pattern(self, line: str, pattern: str, ignore: str) -> bool:
        """Check if line matches pattern but not ignore pattern."""
        if pattern == "CVBFGG" or not pattern:
            return False
        
        # Handle regex patterns
        if any(char in pattern for char in r'.*+?^$[]{}()|\\'): 
            try:
                if not re.search(pattern, line):
                    return False
            except re.error:
                if pattern not in line:
                    return False
        else:
            if pattern not in line:
                return False
        
        # Check ignore pattern
        if ignore and ignore != "CVBFGG":
            try:
                if re.search(ignore, line):
                    return False
            except re.error:
                if ignore in line:
                    return False
        
        return True
    
    def _determine_result(self) -> Tuple[int, str, int, str]:
        """Determine final analysis result."""
        if self.error_matches:
            return (2, f"Error pattern found: {self.first_error[2]}", 
                   self.first_error[0], self.first_error[1])
        elif self.warning_matches:
            return (1, f"Serious warning pattern found: {self.first_warning[2]}", 
                   self.first_warning[0], self.first_warning[1])
        elif self.minor_matches:
            return (0.5, f"Minor warning pattern found: {self.first_minor[2]}", 
                   self.first_minor[0], self.first_minor[1])
        else:
            return (0, "No problems found", 0, "")


class HTMLReportGenerator:
    """Generate HTML reports for log analysis."""
    
    def __init__(self, env_vars: Dict[str, str]):
        self.env = env_vars
    
    def generate_report(self, log_file: Path, problem_level: int, message: str, 
                       line_number: int, line_content: str, component_name: str) -> Path:
        """Generate HTML report and return path to generated file."""
        html_file = log_file.with_suffix('.html')
        
        with open(html_file, 'w', encoding='utf-8') as f:
            self._write_header(f, problem_level, component_name)
            self._write_summary(f, message, log_file)
            self._write_log_content(f, log_file, line_number)
            self._write_footer(f)
        
        return html_file
    
    def _write_header(self, f, problem_level: int, component_name: str):
        """Write HTML header with styling."""
        comment = {0.5: "M", 1: "W", 2: "E"}.get(problem_level, "")
        
        f.write(f'''<!DOCTYPE html>
<html>
<!-- {comment} -->
<head>
    <title>{component_name} Logfile</title>
    <style>
        body {{
            color: black;
            background: floralwhite;
            font-family: 'Lucida Console', 'Courier New', Courier, monospace;
            font-size: 10pt;
        }}
        .problem-line {{
            background-color: orange;
            font-weight: bold;
        }}
        .header {{
            background-color: #CFECEC;
            font-family: Verdana, Arial, Helvetica, sans-serif;
            font-size: 10pt;
            padding: 10px;
        }}
        .log-content {{
            white-space: pre-wrap;
            font-family: monospace;
        }}
        .footer {{
            font-weight: bold;
            text-align: center;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
''')
    
    def _write_summary(self, f, message: str, log_file: Path):
        """Write summary section."""
        f.write(f'''<div class="header">
    <b>{escape(message)}</b><br>
    <b>Original log file:</b> <code>{escape(str(log_file))}</code>
</div>
<div class="log-content">
''')
    
    def _write_log_content(self, f, log_file: Path, highlight_line: int):
        """Write log file content with optional line highlighting."""
        try:
            with open(log_file, 'r', errors='ignore', encoding='utf-8') as log_f:
                for line_num, line in enumerate(log_f, 1):
                    escaped_line = escape(line)
                    if line_num == highlight_line:
                        f.write(f'<div class="problem-line">{escaped_line}</div>')
                    else:
                        f.write(escaped_line)
        except IOError:
            f.write("Error: Could not read log file content")
    
    def _write_footer(self, f):
        """Write HTML footer."""
        f.write('''</div>
<div class="footer">END OF LOGFILE</div>
</body>
</html>
''')


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze log files for errors, warnings, and generate HTML reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s package release tags.txt package_name
  %(prog)s -t test_name release
  %(prog)s -q qa_test release
        """
    )
    
    parser.add_argument('-s', '--short', action='store_true',
                       help='Short output format')
    parser.add_argument('-e', '--specformat', action='store_true', 
                       help='Special format output')
    parser.add_argument('-t', '--testtesting', action='store_true',
                       help='Enable test mode')
    parser.add_argument('-q', '--qatesting', action='store_true',
                       help='Enable QA test mode')
    parser.add_argument('-l', '--light', action='store_true',
                       help='Light mode (limited error analysis)')
    parser.add_argument('args', nargs='*', help='Positional arguments')
    
    return parser.parse_args()


def get_environment_variables() -> Dict[str, str]:
    """Retrieve all required environment variables."""
    env_vars = {}
    required_vars = [
        'ARDOC_LOG', 'ARDOC_TESTLOG', 'ARDOC_QALOG', 'ARDOC_HOME',
        'ARDOC_PROJECT_NAME', 'ARDOC_PROJECT_RELNAME', 'ARDOC_PROJECT_RELNAME_COPY',
        'ARDOC_WEBDIR', 'ARDOC_WEBPAGE', 'ARDOC_VERSION',
        'ARDOC_TEST_SUCCESS_PATTERN', 'ARDOC_TEST_FAILURE_PATTERN', 
        'ARDOC_TEST_WARNING_PATTERN', 'ARDOC_BUILD_FAILURE_PATTERN',
        'ARDOC_QA_SUCCESS_PATTERN', 'ARDOC_QA_FAILURE_PATTERN', 
        'ARDOC_QA_WARNING_PATTERN'
    ]
    
    for var in required_vars:
        env_vars[var] = os.environ.get(var, '')
    
    # Set default for build failure pattern
    if not env_vars['ARDOC_BUILD_FAILURE_PATTERN']:
        env_vars['ARDOC_BUILD_FAILURE_PATTERN'] = 'CVBFGG'
    
    return env_vars


def find_log_file(log_dir: Path, component_name: str) -> Optional[Path]:
    """Find the most recent log file for the given component."""
    pattern = f"{component_name}.loglog"
    log_files = list(log_dir.glob(pattern))
    
    if not log_files:
        return None
    
    # Return most recently modified file
    return max(log_files, key=lambda f: f.stat().st_mtime)


def copy_to_web_directory(html_file: Path, env_vars: Dict[str, str], 
                         is_testing: bool = False, is_qa: bool = False) -> bool:
    """Copy HTML report to web directory if configured."""
    web_dir = env_vars.get('ARDOC_WEBDIR')
    if not web_dir:
        return False
    
    # Determine subdirectory name
    rel_name = env_vars.get('ARDOC_PROJECT_RELNAME_COPY', '')
    if is_qa:
        subdir_name = f"ARDOC_QALog_{rel_name}"
    elif is_testing:
        subdir_name = f"ARDOC_TestLog_{rel_name}"
    else:
        subdir_name = f"ARDOC_Log_{rel_name}"
    
    dest_dir = Path(web_dir) / subdir_name
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        shutil.copy2(html_file, dest_dir / html_file.name)
        print(f"Copied report to {dest_dir / html_file.name}")
        return True
    except IOError as e:
        print(f"Warning: Failed to copy to web directory: {e}")
        return False


def main():
    """Main execution function."""
    args = parse_arguments()
    env_vars = get_environment_variables()
    
    # Validate arguments based on mode
    if args.testtesting or args.qatesting:
        if len(args.args) != 2:
            print("Error: Test mode requires exactly 2 arguments: test_name release")
            sys.exit(2)
        component_name, release = args.args
        log_base_dir = env_vars['ARDOC_QALOG'] if args.qatesting else env_vars['ARDOC_TESTLOG']
    else:
        if len(args.args) != 4:
            print("Error: Build mode requires exactly 4 arguments: directory_package release tags_file package_name")
            sys.exit(2)
        component_name, release, tags_file, package_name = args.args
        log_base_dir = env_vars['ARDOC_LOG']
    
    # Determine log directory
    if not log_base_dir:
        print("Error: Required environment variable not set")
        sys.exit(2)
    
    log_dir = Path(log_base_dir).parent
    
    # Find log file
    log_file = find_log_file(log_dir, component_name)
    if not log_file:
        print(f"Error: No log file found for {component_name} in {log_dir}")
        sys.exit(0)
    
    # Initialize analysis components
    patterns = LogPatterns(env_vars, args.testtesting, args.qatesting, args.light)
    analyzer = LogAnalyzer(patterns)
    report_generator = HTMLReportGenerator(env_vars)
    
    # Analyze log file
    problem_level, message, line_number, line_content = analyzer.analyze_file(log_file)
    
    # Generate HTML report
    html_file = report_generator.generate_report(
        log_file, problem_level, message, line_number, line_content, component_name
    )
    
    print(f"Analysis complete. HTML report: {html_file}")
    
    # Copy to web directory
    copy_to_web_directory(html_file, env_vars, args.testtesting, args.qatesting)
    
    # Print summary unless in short mode
    if not args.short:
        if problem_level >= 2:
            print(f"ERROR: {message}")
        elif problem_level >= 1:
            print(f"WARNING: {message}")
        elif problem_level >= 0.5:
            print(f"MINOR: {message}")
        else:
            print("SUCCESS: No problems found")
    
    # Exit with appropriate code
    if problem_level >= 2:
        sys.exit(2)
    elif problem_level >= 1:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
