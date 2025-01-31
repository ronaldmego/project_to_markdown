# src/project_to_markdown/constants.py

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

# Output directory name
OUTPUT_DIR = "project_to_markdown_output"

# Files that might contain sensitive information - these will always be excluded
SENSITIVE_FILES = {
    # Environment and configuration files that might contain secrets
    '.env',
    '.env.local',
    '.env.development',
    '.env.production',
    '.env.test',
    '.Renviron',
    '.Rprofile',
    'credentials.json',
    'client_secrets.json',
    'service-account.json',
    'config.json',
    'settings.json',
    'secrets.yaml',
    'secrets.yml',
    '.npmrc',
    '.pypirc',
    'id_rsa',
    'id_dsa',
    'id_ecdsa',
    '.aws/credentials',
    'wp-config.php',
    'connection.json',
    'database.ini',
    'database.yml',
    'database.yaml'
}

# Known text files that should always be processed if they exist
IMPORTANT_CONFIG_FILES = {
    '.gitignore',
}

# Known text file extensions that don't need content verification
KNOWN_TEXT_EXTENSIONS = {
    '.txt', '.md', '.tex', '.py', '.json',
    '.yml', '.yaml', '.qmd'
}

# Default files to exclude
DEFAULT_EXCLUDE_FILES = {
    'package-lock.json',
    'yarn.lock',
    'renv.lock',
    'poetry.lock',
    'Gemfile.lock',
    'composer.lock',
    'Cargo.lock',
    'packages.lock.json',
    *SENSITIVE_FILES  # Incluimos todos los archivos sensibles aquí
}

# Default directories to exclude
DEFAULT_EXCLUDE_DIRS = {
    '.git', '__pycache__', 'node_modules', 'venv', '.venv',
    'env', '.env', 'renv', '.idea', '.vscode', 'dist', 'build',
    'coverage', 'tmp', '.next', '.nuxt', '.pytest_cache',
    '.mypy_cache', '.ruff_cache', '.hypothesis',
    '.next', '.nuxt', '_site', '.jekyll-cache',
    'project_to_markdown_output'
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
    '.md', '.rst', '.tex', '.txt', '.qmd',
    # Other languages
    '.scala', '.kt', '.kts', '.swift', '.m', '.mm', '.r', '.pl', '.pm',
    '.groovy', '.gradle', '.clj', '.cls', '.ex', '.exs'
}

# Files without extensions that are typically code
NO_EXT_CODE_FILES = {
    'dockerfile', 'containerfile', 'makefile', 'jenkinsfile', 'vagrantfile',
    'gemfile', 'rakefile', 'procfile', 'brewfile', 'justfile',
    'dockerignore', 'editorconfig', 'pylintrc'
}

