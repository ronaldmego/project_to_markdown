import os
import argparse
import sys
from datetime import datetime
from typing import Set, List, Tuple, Optional, Dict

# Default directories to exclude
DEFAULT_EXCLUDE_DIRS = {
    '.git', '__pycache__', 'node_modules', 'venv', '.venv',
    'env', '.env', '.idea', '.vscode', 'dist', 'build',
    'coverage', 'tmp', '.next', '.nuxt', '.pytest_cache',
    '.mypy_cache', '.ruff_cache', '.hypothesis'
}

# Common code file extensions
CODE_FILE_EXTENSIONS = {
    # Python
    '.py', '.pyi', '.pyx', '.pxd',
    # Web
    '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte', '.html', '.css', '.scss', '.less',
    # Backend
    '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.go', '.rs', '.php', '.rb',
    # Shell and scripts
    '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
    # Data and config
    '.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.env',
    # Documentation
    '.md', '.rst', '.tex','.txt',
    # Other languages
    '.scala', '.kt', '.kts', '.swift', '.m', '.mm', '.r', '.pl', '.pm',
    '.groovy', '.gradle', '.clj', '.cls', '.ex', '.exs'
}

# Files without extensions that are typically code
NO_EXT_CODE_FILES = {
    'Dockerfile','dockerfile', 'containerfile', 'makefile', 'jenkinsfile', 'vagrantfile',
    'gemfile', 'rakefile', 'procfile', 'brewfile', 'justfile', 'gitignore',
    'dockerignore', 'editorconfig', 'pylintrc', 'env'
}

class ProjectAnalyzer:
    def __init__(
        self, 
        root_path: str,
        exclude_dirs: Optional[Set[str]] = None,
        exclude_files: Optional[Set[str]] = None,
        max_file_size: int = 1024 * 1024,  # 1MB default
        max_files: int = 1000,
        max_depth: Optional[int] = None
    ):
        """
        Initialize the project analyzer with the given configuration.

        Args:
            root_path: Path to the project root directory
            exclude_dirs: Additional directories to exclude
            exclude_files: Specific files to exclude
            max_file_size: Maximum size of individual files to process
            max_files: Maximum number of files to process
            max_depth: Maximum directory depth to traverse
        """
        self.root_path = os.path.abspath(root_path)
        self.exclude_dirs = DEFAULT_EXCLUDE_DIRS | (set(exclude_dirs) if exclude_dirs else set())
        self.exclude_files = set(exclude_files) if exclude_files else set()
        self.max_file_size = max_file_size
        self.max_files = max_files
        self.max_depth = max_depth
        
        # Statistics
        self.files_analyzed = 0
        self.total_size = 0
        self.skipped_files: Dict[str, str] = {}  # filepath: reason
        
    def is_text_file(self, file_path: str) -> bool:
        """
        Determine if a file is a text file by examining its content.
        Now more permissive with common text files.
        """
        # Extensiones que sabemos son texto
        known_text_extensions = {'.txt', '.md', '.tex', '.log', '.py', '.json', '.yml', '.yaml'}
        _, ext = os.path.splitext(file_path.lower())
        
        # Si la extensión es conocida, asumimos que es texto
        if ext in known_text_extensions:
            return True
            
        # Para otras extensiones, hacemos la verificación de contenido
        try:
            with open(file_path, 'rb') as file:
                chunk = file.read(1024)
                # Permitimos más caracteres comunes en archivos de texto
                return all(c in range(128) for c in chunk)  # Más permisivo con ASCII
        except (OSError, PermissionError):
            return False

    def is_code_file(self, file_path: str) -> bool:
        """Determine if a file should be included in documentation."""
        filename = os.path.basename(file_path)
        
        # Debug logging
        print(f"Checking file: {filename}")
        
        if filename in self.exclude_files:
            print(f"  Skipped: in exclude list")
            return False
            
        if not self.is_text_file(file_path):
            print(f"  Skipped: not a text file")
            self.skipped_files[file_path] = "binary file"
            return False
        
        # Verificar archivos sin extensión
        if filename.lower() in NO_EXT_CODE_FILES:  # Añade esta verificación
            print(f"  Included: known no-extension code file")
            return True
        
        # Verificar extensiones
        name, ext = os.path.splitext(filename)
        if ext.lower() in CODE_FILE_EXTENSIONS:
            print(f"  Included: known extension")
            return True
        
        print(f"  Skipped: unknown type")
        self.skipped_files[file_path] = "unknown type"
        return False
        
    def generate_tree(self) -> str:
        """
        Generate a tree representation of the project structure.
        
        Returns:
            str: Formatted tree structure of the project
        """
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
                    
                    # Add trailing slash for directories
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
        """
        Collect all code files with their content.
        
        Returns:
            List[Tuple[str, str]]: List of (relative_path, content) pairs
        """
        code_files = []
        self.files_analyzed = 0  # Reset counter
        
        def process_directory(path: str, current_depth: int = 0) -> None:
            if self.max_depth is not None and current_depth > self.max_depth:
                return
                
            if self.files_analyzed >= self.max_files:
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
                                print(f"Skipping {item}: file too large ({file_size / 1024:.1f}KB)")
                                self.skipped_files[full_path] = f"file too large ({file_size / 1024:.1f}KB)"
                                continue
                                
                            if self.is_code_file(full_path):
                                print(f"Attempting to read: {item}")
                                try:
                                    with open(full_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                        print(f"Debug: Content length for {item}: {len(content)} chars")
                                        if len(content.strip()) == 0:
                                            print(f"Warning: Empty content for {item}")
                                            continue
                                            
                                        rel_path = os.path.relpath(full_path, self.root_path)
                                        code_files.append((rel_path, content))
                                        self.files_analyzed += 1
                                        self.total_size += len(content)
                                        print(f"Successfully read: {item} (size: {len(content)} chars)")
                                        
                                except UnicodeDecodeError as e:
                                    print(f"Encoding error in {item}: {str(e)}")
                                    self.skipped_files[full_path] = f"encoding error: {str(e)}"
                                except PermissionError:
                                    print(f"Permission denied for {item}")
                                    self.skipped_files[full_path] = "permission denied"
                                except Exception as e:
                                    print(f"Error reading {item}: {str(e)}")
                                    self.skipped_files[full_path] = f"error: {str(e)}"
                                    
                        except OSError as e:
                            print(f"OS error with {item}: {str(e)}")
                            self.skipped_files[full_path] = f"OS error: {str(e)}"
                            
            except (PermissionError, FileNotFoundError) as e:
                print(f"Directory error: {str(e)}")
                self.skipped_files[path] = f"directory error: {str(e)}"
                return
                
        process_directory(self.root_path)
        print(f"\nDebug Summary:")
        print(f"Total files collected: {len(code_files)}")
        print(f"Files analyzed: {self.files_analyzed}")
        print(f"Total size: {self.total_size / 1024:.2f} KB")
        
        return code_files
    
    def generate_summary(self, skipped_file_limit: int = 10) -> str:
        """
        Generate transformation summary including statistics and skipped files.
        
        Args:
            skipped_file_limit: Maximum number of skipped files to list
            
        Returns:
            str: Formatted summary
        """
        summary = [
            "Project transformation Summary",
            "=====================",
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
            
            # Group skipped files by reason
            by_reason: Dict[str, List[str]] = {}
            for file_path, reason in self.skipped_files.items():
                by_reason.setdefault(reason, []).append(os.path.relpath(file_path, self.root_path))
            
            # Show samples for each reason
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
        print("\nDebug - Generating Report:")
        
        tree = self.generate_tree()
        code_files = self.collect_code_files()
        print(f"Debug: Collected {len(code_files)} files for report")
        
        report = []
        
        # Generate and store summary first
        summary = self.generate_summary()
        report.append(summary)
        
        # Add tree structure
        report.append("\nDirectory Structure\n==================\n")
        report.append(tree)
        
        # Add file contents with explicit tracking
        report.append("\n\nFile Contents\n=============\n")
        separator = "=" * 80 + "\n"
        
        files_included = 0
        for file_path, content in code_files:
            print(f"Debug: Adding file {file_path} to report")
            report.append(f"\n{separator}File: {file_path}\n{separator}")
            report.append(content)
            report.append("\n")
            files_included += 1
        
        print(f"Debug: Added {files_included} files to report")
        
        final_report = "\n".join(report)
        print(f"Debug: Final report length: {len(final_report)} characters")
        
        return final_report
    
    def save_report(self, output_path: Optional[str] = None) -> list[str]:
        """
        Save report to specified path and project directory.
        
        Args:
            output_path: Optional custom path for the report
                
        Returns:
            list[str]: Paths where the reports were saved
        """
        saved_paths = []
        
        # Generate default filename based on project name and timestamp
        root_name = os.path.basename(self.root_path.rstrip(os.sep))
        filename = f"project_transformation_{root_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        # Save in current working directory's ref folder
        if not output_path:
            ref_dir = os.path.join(os.getcwd(), "ref")
            os.makedirs(ref_dir, exist_ok=True)
            output_path = os.path.join(ref_dir, filename)
        
        # Save in project directory's ref folder
        project_ref_dir = os.path.join(self.root_path, "ref")
        os.makedirs(project_ref_dir, exist_ok=True)
        project_output_path = os.path.join(project_ref_dir, filename)
        
        # Generate report once and save to both locations
        report = self.generate_report()
        
        # Save to current directory ref folder
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        saved_paths.append(output_path)
        
        # Save to project directory ref folder
        with open(project_output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        saved_paths.append(project_output_path)
            
        return saved_paths

def main():
    parser = argparse.ArgumentParser(
        description='Analyze a project directory and create a consolidated report for LLMs',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('directory', 
                       type=str, 
                       help='Root directory path to analyze')
    
    parser.add_argument('--output', 
                       type=str,
                       help='Output file path for the report')
    
    parser.add_argument('--max-depth',
                       type=int,
                       help='Maximum depth to traverse in the directory tree')
    
    parser.add_argument('--exclude-dirs',
                       nargs='+',
                       help='Additional directories to exclude')
    
    parser.add_argument('--exclude-files',
                       nargs='+',
                       help='Specific files to exclude')
    
    parser.add_argument('--max-file-size',
                       type=int,
                       default=1024 * 1024,
                       help='Maximum file size in bytes (default: 1MB)')
    
    parser.add_argument('--max-files',
                       type=int,
                       default=1000,
                       help='Maximum number of files to process (default: 1000)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"Error: Directory {args.directory} does not exist")
        sys.exit(1)
    
    try:
        analyzer = ProjectAnalyzer(
            root_path=args.directory,
            exclude_dirs=set(args.exclude_dirs) if args.exclude_dirs else None,
            exclude_files=set(args.exclude_files) if args.exclude_files else None,
            max_file_size=args.max_file_size,
            max_files=args.max_files,
            max_depth=args.max_depth
        )
        
        output_files = analyzer.save_report(args.output)
        print(f"\ntransformation completed successfully!")
        print("Reports saved to:")
        for path in output_files:
            print(f"- {path}")
        
    except Exception as e:
        print(f"Error during transformation: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()