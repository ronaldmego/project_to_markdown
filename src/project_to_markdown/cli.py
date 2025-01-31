"""Command-line interface for project_to_markdown."""

import os
import sys
import argparse

from project_to_markdown.analyzer import ProjectAnalyzer

def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Analyze a project directory and create a consolidated markdown report for LLMs',
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
                       help='Maximum depth to traverse in directory tree')
    
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

    parser.add_argument('--max-lines',
                       type=int,
                       default=500,
                       help='Maximum number of lines per file (default: 500)')
    
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
            max_lines=args.max_lines
        )
        
        output_file = analyzer.save_report(args.output)
        print(f"\nProject documentation completed successfully!")
        print(f"Report saved to: {output_file}")
        
    except Exception as e:
        print(f"Error during documentation generation: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()