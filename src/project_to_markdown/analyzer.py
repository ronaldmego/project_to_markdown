"""Main module containing the ProjectAnalyzer class."""

import os
from datetime import datetime
from typing import Optional, Dict, List, Tuple

from project_to_markdown.constants import (
    CODE_FILE_EXTENSIONS,
    NO_EXT_CODE_FILES,
    DEFAULT_EXCLUDE_DIRS,
    MIN_LINES_PER_FILE,
    MAX_FILES,
    MAX_TOTAL_SIZE_BYTES
)

class ProjectAnalyzer:
    """Class for analyzing project directories and creating markdown documentation."""
    
    def __init__(self, 
                 root_path: str,
                 exclude_dirs: Optional[set[str]] = None,
                 exclude_files: Optional[set[str]] = None,
                 max_file_size: int = 1024 * 1024,  # 1MB
                 max_files: int = 1000,
                 max_depth: Optional[int] = None,
                 max_lines: int = 500):
        """Initialize the project analyzer.

        Args:
            root_path: Path to the project root directory
            exclude_dirs: Additional directories to exclude
            exclude_files: Specific files to exclude
            max_file_size: Maximum size of individual files to process
            max_files: Maximum number of files to process
            max_depth: Maximum directory depth to traverse
            max_lines: Maximum number of lines per file
        """
        self.root_path = os.path.abspath(root_path)
        self.exclude_dirs = DEFAULT_EXCLUDE_DIRS | (set(exclude_dirs) if exclude_dirs else set())
        self.exclude_files = set(exclude_files) if exclude_files else set()
        self.max_file_size = max_file_size
        self.max_files = max_files
        self.max_depth = max_depth
        self.max_lines = max_lines
        
        # Statistics
        self.files_analyzed = 0
        self.total_size = 0
        self.skipped_files: Dict[str, str] = {}

    def process_content(self, content: str, filepath: str) -> str:
        """Process and truncate content if necessary."""
        lines = content.split('\n')
        if len(lines) > self.max_lines:
            truncated = lines[:self.max_lines]
            truncated.append(f"\n... [Content truncated - exceeded {self.max_lines} lines] ...")
            return '\n'.join(truncated)
        return content

    def is_text_file(self, file_path: str) -> bool:
        """Determine if a file is a text file by examining its content."""
        try:
            with open(file_path, 'rb') as file:
                chunk = file.read(1024)
                return all(c < 128 for c in chunk)
        except (OSError, PermissionError):
            return False

    def is_code_file(self, file_path: str) -> bool:
        """Determine if a file should be included in documentation."""
        filename = os.path.basename(file_path)
        
        if filename in self.exclude_files:
            return False
            
        if not self.is_text_file(file_path):
            self.skipped_files[file_path] = "binary file"
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
                if line_count < MIN_LINES_PER_FILE:
                    self.skipped_files[file_path] = f"too few lines ({line_count})"
                    return False
        except Exception:
            return False
        
        if filename.lower() in NO_EXT_CODE_FILES:
            return True
        
        _, ext = os.path.splitext(filename)
        if ext.lower() in CODE_FILE_EXTENSIONS:
            return True
        
        self.skipped_files[file_path] = "unknown type"
        return False
        
    def generate_tree(self) -> str:
        """Generate a tree representation of the project structure."""
        lines = []
        root_name = os.path.basename(self.root_path.rstrip(os.sep))
        lines.append(root_name)
        
        def add_to_tree(path: str, prefix: str = "", current_depth: int = 0) -> None:
            if self.max_depth is not None and current_depth > self.max_depth:
                return
                
            try:
                contents = sorted(os.listdir(path))
                contents = [item for item in contents 
                          if item not in self.exclude_dirs]
                
                for i, item in enumerate(contents):
                    is_last = i == len(contents) - 1
                    current_prefix = "└── " if is_last else "├── "
                    full_path = os.path.join(path, item)
                    
                    display_name = f"{item}/" if os.path.isdir(full_path) else item
                    lines.append(f"{prefix}{current_prefix}{display_name}")
                    
                    if os.path.isdir(full_path):
                        next_prefix = prefix + ("    " if is_last else "│   ")
                        add_to_tree(full_path, next_prefix, current_depth + 1)
                        
            except (PermissionError, FileNotFoundError, OSError) as e:
                lines.append(f"{prefix}├── [Error: {str(e)}]")
                return
            
        add_to_tree(self.root_path)
        return "\n".join(lines)
    
    def collect_code_files(self) -> List[Tuple[str, str]]:
        """Collect all code files with their content."""
        code_files = []
        self.files_analyzed = 0
        
        def process_directory(path: str, current_depth: int = 0) -> None:
            if self.max_depth is not None and current_depth > self.max_depth:
                return
                
            if self.files_analyzed >= self.max_files:
                return
            
            if self.total_size > MAX_TOTAL_SIZE_BYTES:
                return

            try:
                for item in sorted(os.listdir(path)):
                    if item in self.exclude_dirs:
                        continue
                        
                    full_path = os.path.join(path, item)
                    
                    if os.path.isdir(full_path):
                        process_directory(full_path, current_depth + 1)
                    elif os.path.isfile(full_path):
                        try:
                            file_size = os.path.getsize(full_path)
                            if file_size > self.max_file_size:
                                self.skipped_files[full_path] = f"file too large ({file_size / 1024:.1f}KB)"
                                continue
                                
                            if self.is_code_file(full_path):
                                try:
                                    with open(full_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                        content = self.process_content(content, full_path)
                                        if len(content.strip()) == 0:
                                            continue
                                            
                                        rel_path = os.path.relpath(full_path, self.root_path)
                                        code_files.append((rel_path, content))
                                        self.files_analyzed += 1
                                        self.total_size += len(content)
                                        
                                except UnicodeDecodeError as e:
                                    self.skipped_files[full_path] = f"encoding error: {str(e)}"
                                except PermissionError:
                                    self.skipped_files[full_path] = "permission denied"
                                except Exception as e:
                                    self.skipped_files[full_path] = f"error: {str(e)}"
                                    
                        except OSError as e:
                            self.skipped_files[full_path] = f"OS error: {str(e)}"
                            
            except (PermissionError, FileNotFoundError) as e:
                self.skipped_files[path] = f"directory error: {str(e)}"
                return
                
        process_directory(self.root_path)
        return code_files
    
    def generate_summary(self, skipped_file_limit: int = 10) -> str:
        """Generate transformation summary including statistics and skipped files."""
        summary = [
            "Project Documentation Summary",
            "=========================",
            f"Root Directory: {self.root_path}",
            f"Files Analyzed: {self.files_analyzed}",
            f"Total Size: {self.total_size / 1024:.2f} KB",
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        
        if self.skipped_files:
            summary.extend([
                "",
                "Skipped Files Sample:",
                "-------------------"
            ])
            
            by_reason: Dict[str, List[str]] = {}
            for file_path, reason in self.skipped_files.items():
                by_reason.setdefault(reason, []).append(os.path.relpath(file_path, self.root_path))
            
            for reason, files in by_reason.items():
                total = len(files)
                if total == 1:
                    summary.append(f"- {reason}: {files[0]}")
                else:
                    sample = files[:skipped_file_limit]
                    remaining = total - len(sample)
                    summary.append(f"- {reason} ({total} files):")
                    for file in sample:
                        summary.append(f"  • {file}")
                    if remaining > 0:
                        summary.append(f"  • ...and {remaining} more")
                        
        return "\n".join(summary)
    
    def generate_report(self) -> str:
        """Generate complete report with tree, summary and file contents."""
        tree = self.generate_tree()
        code_files = self.collect_code_files()
        
        report = []
        
        summary = self.generate_summary()
        report.append(summary)
        
        report.append("\nDirectory Structure\n==================\n")
        report.append(tree)
        
        report.append("\nFile Contents\n=============\n")
        separator = "=" * 80 + "\n"
        
        for file_path, content in code_files:
            report.append(f"\n{separator}File: {file_path}\n{separator}")
            report.append(content)
            report.append("\n")
        
        return "\n".join(report)
    
    def save_report(self, output_path: Optional[str] = None) -> str:
        """Save report to file.
        
        Args:
            output_path: Optional custom path for the report
                
        Returns:
            str: Path where the report was saved
        """
        # Generate default filename based on project name and timestamp
        root_name = os.path.basename(self.root_path.rstrip(os.sep))
        filename = f"project_docs_{root_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        # If no output path specified, save in project root
        if not output_path:
            output_path = os.path.join(self.root_path, filename)
            
        # Generate report and save
        report = self.generate_report()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
            
        return output_path