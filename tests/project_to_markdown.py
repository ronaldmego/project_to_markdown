import os
import argparse
import sys
from datetime import datetime
from typing import Set, List, Tuple, Optional, Dict

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_FILES = 1000
MAX_TOTAL_SIZE_BYTES = 500 * 1024 * 1024
MAX_LINES_PER_FILE = 500
MIN_LINES_PER_FILE = 5
MAX_DEPTH = 10

# Default directories to exclude
DEFAULT_EXCLUDE_DIRS = {
    '.git', '__pycache__', 'node_modules', 'venv', '.venv',
    'env', '.env', 'renv', '.idea', '.vscode', 'dist', 'build',
    'coverage', 'tmp', '.next', '.nuxt', '.pytest_cache',
    '.mypy_cache', '.ruff_cache', '.hypothesis',
    '.next', '.nuxt', '_site', '.jekyll-cache'
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
    '.md', '.rst', '.tex','.txt','.qmd',
    # Other languages
    '.scala', '.kt', '.kts', '.swift', '.m', '.mm', '.r', '.pl', '.pm',
    '.groovy', '.gradle', '.clj', '.cls', '.ex', '.exs','.lock'
}

# Files without extensions that are typically code
NO_EXT_CODE_FILES = {
    'Dockerfile','dockerfile', 'containerfile', 'makefile', 'jenkinsfile', 'vagrantfile',
    'gemfile', 'rakefile', 'procfile', 'brewfile', 'justfile', 'gitignore',
    'dockerignore', 'editorconfig', 'pylintrc', 'env'
}

class ProjectAnalyzer:
    def __init__(self, 
                 root_path: str,
                 exclude_dirs: Optional[Set[str]] = None,
                 exclude_files: Optional[Set[str]] = None,
                 max_file_size: int = 1024 * 1024,
                 max_files: int = 1000,
                 max_depth: Optional[int] = None,
                 max_lines: int = 500):  # Añadir parámetro
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
        self.max_lines = max_lines
        
        # Statistics
        self.files_analyzed = 0
        self.total_size = 0
        self.skipped_files: Dict[str, str] = {}  # filepath: reason

        # Add new configuration options
        self.min_content_lines = 5  # Skip files with fewer lines
        self.max_content_lines = 500  # Truncate files with more lines
        self.exclude_generated_patterns = [
            'package-lock.json',
            'yarn.lock',
            'Gemfile.lock',
            '*.pyc',
            '*.pyo',
            '__pycache__',
            'node_modules'
        ]
        
        # Add content quality filters
        self.code_quality_checks = {
            'has_meaningful_content': lambda content: len(content.strip()) > 0,
            'not_binary': lambda content: not self._is_binary(content),
            'reasonable_line_length': lambda content: max(len(line) for line in content.split('\n')) < 500
        }
        
        # Add language-specific handlers
        self.language_handlers = {
            '.py': self._handle_python,
            '.js': self._handle_javascript,
            '.html': self._handle_html,
            '.css': self._handle_css
        }

    def process_content(self, content: str, filepath: str) -> str:
        """Procesa y trunca el contenido si es necesario."""
        lines = content.split('\n')
        if len(lines) > self.max_lines:
            truncated = lines[:self.max_lines]
            truncated.append(f"\n... [Contenido truncado por exceder {self.max_lines} líneas] ...")
            return '\n'.join(truncated)
        return content

    def _handle_python(self, content):
        """Special handling for Python files."""
        lines = content.split('\n')
        # Remove doctest output
        lines = [l for l in lines if not l.startswith('>>>') and not l.startswith('...')]
        # Remove print debugging
        lines = [l for l in lines if not l.strip().startswith('print(')]
        return '\n'.join(lines)

    def _handle_javascript(self, content):
        """Special handling for JavaScript files."""
        lines = content.split('\n')
        # Remove console.log statements
        lines = [l for l in lines if not 'console.log(' in l]
        # Remove commented-out code blocks
        lines = [l for l in lines if not l.strip().startswith('//')]
        return '\n'.join(lines)

    def _is_binary(self, content: str) -> bool:
        """Check if content appears to be binary."""
        try:
            # Try decoding as text
            content.encode('utf-8').decode('utf-8')
            return False
        except (UnicodeError, UnicodeDecodeError):
            return True

    def _handle_html(self, content: str) -> str:
        """Clean up HTML content."""
        lines = content.split('\n')
        # Remove commented blocks
        lines = [l for l in lines if not l.strip().startswith('<!--')]
        # Remove empty script tags
        lines = [l for l in lines if not '<script></script>' in l]
        return '\n'.join(lines)

    def _handle_css(self, content: str) -> str:
        """Clean up CSS content."""
        lines = content.split('\n')
        # Remove commented blocks
        lines = [l for l in lines if not l.strip().startswith('/*')]
        # Remove empty rules
        lines = [l for l in lines if not '{ }' in l]
        return '\n'.join(lines)

    def process_file(self, filepath):
        """Enhanced file processing with quality filters."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Apply quality checks
        if not all(check(content) for check in self.code_quality_checks.values()):
            return None
            
        # Apply language-specific handling
        ext = os.path.splitext(filepath)[1]
        if ext in self.language_handlers:
            content = self.language_handlers[ext](content)
            
        # Apply line limits
        lines = content.split('\n')
        if len(lines) < self.min_content_lines:
            return None
        if len(lines) > self.max_content_lines:
            content = '\n'.join(lines[:self.max_content_lines]) + '\n... (truncated)'
            
        return content

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

        # Add line count check
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
                if line_count < MIN_LINES_PER_FILE:
                    self.skipped_files[file_path] = f"too few lines ({line_count})"
                    return False
        except Exception:
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
        """Collect all code files with their content."""
        code_files = []
        self.files_analyzed = 0
        
        def process_directory(path: str, current_depth: int = 0) -> None:
            if self.max_depth is not None and current_depth > self.max_depth:
                return
                
            if self.files_analyzed >= self.max_files:
                return
            
            if self.total_size > MAX_TOTAL_SIZE_BYTES:
                print(f"Skipping further files: total size limit ({MAX_TOTAL_SIZE_BYTES/1024/1024:.1f}MB) reached")
                return code_files

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
                                        content = self.process_content(content, full_path)  # Aplicar truncamiento
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
    

    parser.add_argument('--max-lines',
                       type=int,
                       default=500,
                       help='Maximum number of lines per file (default: 500)')

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
            max_depth=args.max_depth,
            max_lines=args.max_lines  # Añadir el nuevo parámetro
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