"""Constants and configurations for project_to_markdown."""

# File size limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_TOTAL_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB

# File count limits
MAX_FILES = 1000
MIN_LINES_PER_FILE = 5
MAX_LINES_PER_FILE = 500

# Directory traversal limit
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
    '.md', '.rst', '.tex', '.txt',
    # Other languages
    '.scala', '.kt', '.kts', '.swift', '.m', '.mm', '.r', '.pl', '.pm',
    '.groovy', '.gradle', '.clj', '.cls', '.ex', '.exs', '.lock'
}

# Files without extensions that are typically code
NO_EXT_CODE_FILES = {
    'dockerfile', 'containerfile', 'makefile', 'jenkinsfile', 'vagrantfile',
    'gemfile', 'rakefile', 'procfile', 'brewfile', 'justfile', 'gitignore',
    'dockerignore', 'editorconfig', 'pylintrc', 'env'
}