import os
import shutil
import glob
from pathlib import Path

# Paths
base_dir = Path(os.getcwd())

def move_dir(src, dst):
    if os.path.exists(src):
        if os.path.exists(dst):
            shutil.rmtree(dst, ignore_errors=True)
        shutil.move(src, dst)
        print(f"Moved {src} to {dst}")

def copy_templates(src, dst):
    if os.path.exists(src):
        os.makedirs(dst, exist_ok=True)
        shutil.copytree(src, dst, dirs_exist_ok=True)
        shutil.rmtree(src)
        print(f"Copied templates from {src} to {dst}")

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replacements
        new_content = content.replace('apps.accounts', 'authentication') \
                             .replace('apps.scraper', 'core') \
                             .replace('apps.dashboard', 'dashboard')
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated imports in {filepath}")
    except Exception as e:
        print(f"Failed to update {filepath}: {e}")

if __name__ == "__main__":
    print("Starting safe refactor...")
    
    # 1. Move Apps
    move_dir('apps/accounts', 'authentication')
    move_dir('apps/scraper', 'core')
    move_dir('apps/dashboard', 'dashboard')
    
    # 2. Centralize Templates
    copy_templates('authentication/templates/accounts', 'templates/authentication')
    copy_templates('dashboard/templates/dashboard', 'templates/dashboard')
    copy_templates('core/templates/scraper', 'templates/core')
    
    # Remove old templates folders entirely
    for d in ['authentication/templates', 'dashboard/templates', 'core/templates']:
        if os.path.exists(d):
            shutil.rmtree(d)
    
    # Remove apps/
    if os.path.exists('apps'):
        # Usually holds (__init__.py, etc)
        shutil.rmtree('apps', ignore_errors=True)

    # 3. Update Imports and Config
    targets = ['authentication/**/*.py', 'core/**/*.py', 'dashboard/**/*.py', 'config/**/*.py', 'manage.py', 'test_*.py', 'verify_*.py']
    for p in targets:
        for f in glob.glob(str(base_dir / p), recursive=True):
            if os.path.isfile(f):
                replace_in_file(f)
    print("Done refactoring imports.")
