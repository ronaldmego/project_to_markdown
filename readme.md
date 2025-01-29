# Project Documentation Generator for LLMs

Generate consolidated documentation of your local projects for Large Language Models analysis, debugging, and improvement suggestions.

## Features

- **Directory Tree Structure**: Visual representation of project layout
- **Code File Analysis**: Extracts content from common programming files
- **Smart Filtering**: Excludes binary files, large files, and common system directories
- **Multiple Output Locations**: Saves documentation in both current directory and project root
- **Markdown Output**: Well-formatted documentation for LLMs

## Installation

Just download `project_to_markdown.py` and ensure Python is installed on your system.

## Usage

Basic syntax:
```bash
python project_to_markdown.py "path/to/your/project" [options]
```

Example:
```bash
python project_to_markdown.py "C:\Users\username\Projects\my-project" --exclude-dirs ref logs
```

## Options

# Uso básico
```bash
python project_to_markdown.py /path/to/project
```

# Con opciones
```bash
python project_to_markdown.py /path/to/project \
    --output report.md \
    --max-depth 3 \
    --exclude-dirs tests docs \
    --exclude-files README.md LICENSE \
    --max-file-size 2097152 \
    --max-files 500
```

## Default Exclusions

### Directories
`.git`, `__pycache__`, `node_modules`, `venv`, `.venv`, `env`, `.env`, `.idea`, `.vscode`, `dist`, `build`, `coverage`, `tmp`, `.next`, `.nuxt`

### File Extensions
The script processes common programming languages:
- Python (`.py`)
- JavaScript/TypeScript (`.js`, `.ts`, `.jsx`, `.tsx`)
- Java (`.java`)
- C/C++ (`.c`, `.cpp`, `.h`, `.hpp`)
- And many more...

## Example Output

The script generates a markdown file named `script_docs_for_project_[projectname].md` containing:

1. Project Analysis Summary
2. Directory Structure
3. File Contents

## OS-Specific Examples

### Windows
```bash
python project_to_markdown.py "C:\Users\username\my-project" --exclude-dirs temp cache
```

### Linux/Mac
```bash
python project_to_markdown.py "/home/username/my-project" --exclude-dirs temp cache
```

### Current use case:
```bash
python project_to_markdown.py "C:\Users\ronal\APPs\telco_analytics" --exclude-dirs ref logs
python project_to_markdown.py "C:\Users\ronal\APPs\work\chat-bedrock\BedrockChatInterface" --exclude-dirs ref logs
```

## Notes

- The project path should come BEFORE any options
- Use quotes for paths with spaces
- The script handles UTF-8 encoding automatically
- Large files are skipped to prevent memory issues

## Error Handling

The script gracefully handles:
- Permission errors
- Non-text files
- Directory access issues
- File encoding problems