"""Setup file for compatibility with older pip versions."""
from setuptools import setup

setup(
    name="project_to_markdown",
    version="0.1.0",
    packages=["project_to_markdown"],
    package_dir={"": "src"},
    install_requires=[],
    entry_points={
        "console_scripts": [
            "project-to-markdown=project_to_markdown.cli:main",
        ],
    },
    python_requires=">=3.7",
)