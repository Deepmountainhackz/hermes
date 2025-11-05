#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post-Cleanup Script
===================
Moves the reorganization scripts themselves and handles log files.
Run this AFTER you've run the main reorganization.
"""

import os
import shutil
from pathlib import Path

class PostCleanup:
    def __init__(self, project_root="."):
        self.root = Path(project_root)
        
    def create_logs_directory(self):
        """Create logs directory if it doesn't exist"""
        logs_dir = self.root / 'logs'
        if not logs_dir.exists():
            logs_dir.mkdir(parents=True, exist_ok=True)
            print("Created logs/ directory")
            
            # Create .gitignore in logs/
            gitignore_path = logs_dir / '.gitignore'
            with open(gitignore_path, 'w') as f:
                f.write("# Ignore all log files\n*.log\n")
            print("Created logs/.gitignore")
    
    def move_reorganization_scripts(self):
        """Move the reorganization scripts to scripts/ folder"""
        scripts_to_move = [
            'reorganize_hermes.py',
            'reorganize_hermes_windows.py',
            'cleanup.sh'
        ]
        
        for script in scripts_to_move:
            src = self.root / script
            if src.exists():
                dst = self.root / 'scripts' / script
                shutil.move(str(src), str(dst))
                print(f"Moved {script} to scripts/")
    
    def move_log_files(self):
        """Move log files to logs/ directory"""
        log_files = list(self.root.glob('*.log'))
        
        for log_file in log_files:
            dst = self.root / 'logs' / log_file.name
            shutil.move(str(log_file), str(dst))
            print(f"Moved {log_file.name} to logs/")
    
    def update_gitignore(self):
        """Update .gitignore to ignore logs and other temporary files"""
        gitignore_path = self.root / '.gitignore'
        
        additions = [
            '\n# Logs',
            'logs/',
            '*.log',
            '\n# Database',
            '*.db',
            '*.db-journal',
            '\n# Python',
            '__pycache__/',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.Python',
            'env/',
            'venv/',
            '\n# IDEs',
            '.vscode/',
            '.idea/',
            '*.swp',
            '*.swo',
            '\n# OS',
            '.DS_Store',
            'Thumbs.db',
            '\n# Environment',
            '.env',
            '.env.local'
        ]
        
        # Read existing content
        existing_content = ""
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                existing_content = f.read()
        
        # Add new entries if they don't exist
        with open(gitignore_path, 'a') as f:
            for line in additions:
                if line not in existing_content:
                    f.write(line + '\n')
        
        print("Updated .gitignore")
    
    def run(self):
        """Execute post-cleanup"""
        print("Running Post-Cleanup...")
        print("=" * 60)
        
        self.create_logs_directory()
        self.move_log_files()
        self.move_reorganization_scripts()
        self.update_gitignore()
        
        print("\n" + "=" * 60)
        print("Post-Cleanup Complete!")
        print("\nYour root directory now contains ONLY:")
        print("  - hermes_dashboard.py")
        print("  - config_cities.py")
        print("  - run_hermes.py")
        print("  - hermes.db")
        print("  - .env")
        print("  - .gitignore")
        print("  - requirements.txt")
        print("  - README.md")
        print("  + 5 organized folders (services/, docs/, scripts/, tests/, backups/)")
        print("  + 1 logs folder (logs/)")
        print("\nPerfectly clean!")

if __name__ == "__main__":
    cleanup = PostCleanup()
    cleanup.run()
