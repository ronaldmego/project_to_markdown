# Project to Markdown

Generate consolidated documentation of your local projects for LLM (Large Language Model) analysis, debugging, and improvement suggestions. This tool creates a comprehensive markdown report of your codebase, making it easy to share context with LLMs.

## Features

- **Smart Directory Tree**: Visual representation of project layout
- **Intelligent Code Filtering**: Automatically excludes:
  - Binary and large files
  - System directories and caches
  - Lock files and environment files
  - Sensitive data (credentials, tokens, etc.)
- **Configurable Analysis**: Control depth, file size, and exclusions
- **Security First**: Built-in protection against sensitive data exposure
- **Organized Output**: All reports saved in a dedicated output directory
- **Multiple Format Support**: Handles various file types including:
  - Python, JavaScript, TypeScript
  - R, Quarto documents
  - Configuration files
  - Documentation files
  - Many more...

## Installation

Install from source:
```bash
git clone https://github.com/yourusername/project_to_markdown
cd project_to_markdown
pip install -e .
```

Or install directly from your local path:
```bash
pip install -e /path/to/project_to_markdown
```

## Basic Usage

Generate documentation for current directory:
```bash
project-to-markdown .
```

Exclude specific directories:
```bash
project-to-markdown . --exclude-dirs tests docs logs
```

## Advanced Options

```bash
project-to-markdown <path> [OPTIONS]

Options:
  --exclude-dirs TEXT     Additional directories to exclude
  --exclude-files TEXT    Specific files to exclude
  --max-depth INTEGER     Maximum directory depth to traverse
  --max-file-size INTEGER Maximum file size in bytes (default: 1MB)
  --max-files INTEGER     Maximum number of files to process (default: 1000)
  --max-lines INTEGER     Maximum lines per file (default: 500)
  --output TEXT          Custom output file path
```

## Project Structure

```
project_to_markdown/
├── src/
│   └── project_to_markdown/
│       ├── __init__.py
│       ├── analyzer.py        # Main analyzer class
│       ├── cli.py            # CLI interface
│       └── constants.py      # Configuration constants
├── tests/                    # Unit tests
├── LICENSE
├── README.md
├── pyproject.toml           # Python project config
├── requirements.txt
└── setup.py                 # Installation script
```

## Default Protections

### Automatically Excluded
- Environment files (`.env`, `.Renviron`)
- Configuration with secrets
- Lock files and dependencies
- Cache directories
- Build artifacts
- Binary files
- Large files (>1MB by default)
- Files with sensitive patterns in names

### File Size and Content Limits
- Maximum file size: 1MB
- Maximum files per project: 1000
- Maximum lines per file: 500

## Output

The tool creates a markdown file in the `project_to_markdown_output` directory containing:
1. Project Summary
   - Files analyzed
   - Total size
   - Timestamp
2. Directory Structure
3. File Contents
4. Skipped Files Report

## Examples

Analyze a Python project:
```bash
project-to-markdown . --exclude-dirs tests docs
```

Analyze with custom limits:
```bash
project-to-markdown . --max-depth 3 --max-files 200 --max-lines 300
```

Specify custom output:
```bash
project-to-markdown . --output custom_report.md
```

## Notes

- Always verify no sensitive data is included in the output
- Use `--exclude-dirs` for project-specific exclusions
- Reports are saved in `project_to_markdown_output` by default
- Use quotes for paths with spaces
- The tool uses UTF-8 encoding

## Error Handling

The tool gracefully handles:
- Permission errors
- Non-text files
- Directory access issues
- File encoding problems
- Memory constraints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.