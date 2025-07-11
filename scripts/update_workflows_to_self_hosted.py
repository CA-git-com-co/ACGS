#!/usr/bin/env python3
"""
Script to update all GitHub Actions workflow files to use self-hosted runners.
Updates 'runs-on: ubuntu-latest' to 'runs-on: self-hosted' in all workflow files.
"""

import os
import re
import glob
from pathlib import Path

def update_workflow_file(file_path):
    """Update a single workflow file to use self-hosted runners."""
    print(f"Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count original occurrences
        original_count = content.count('runs-on: ubuntu-latest')
        
        if original_count == 0:
            print(f"  ✅ No changes needed (no ubuntu-latest found)")
            return False
        
        # Replace ubuntu-latest with self-hosted
        updated_content = content.replace('runs-on: ubuntu-latest', 'runs-on: self-hosted')
        
        # Verify the replacement worked
        new_count = updated_content.count('runs-on: self-hosted')
        remaining_ubuntu = updated_content.count('runs-on: ubuntu-latest')
        
        if remaining_ubuntu > 0:
            print(f"  ⚠️  Warning: {remaining_ubuntu} ubuntu-latest entries remain")
        
        # Write the updated content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"  ✅ Updated {original_count} occurrences to self-hosted")
        return True
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to update all workflow files."""
    print("🚀 Updating GitHub Actions workflows to use self-hosted runners...")
    print("=" * 60)
    
    # Find all workflow files
    workflow_dir = Path('.github/workflows')
    if not workflow_dir.exists():
        print(f"❌ Workflow directory not found: {workflow_dir}")
        return
    
    workflow_files = list(workflow_dir.glob('*.yml')) + list(workflow_dir.glob('*.yaml'))
    
    if not workflow_files:
        print("❌ No workflow files found")
        return
    
    print(f"📁 Found {len(workflow_files)} workflow files")
    print()
    
    updated_files = []
    skipped_files = []
    error_files = []
    
    for workflow_file in sorted(workflow_files):
        try:
            if update_workflow_file(workflow_file):
                updated_files.append(workflow_file.name)
            else:
                skipped_files.append(workflow_file.name)
        except Exception as e:
            print(f"  ❌ Error: {e}")
            error_files.append(workflow_file.name)
        print()
    
    # Summary
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Updated files: {len(updated_files)}")
    for file in updated_files:
        print(f"   - {file}")
    
    if skipped_files:
        print(f"\n⏭️  Skipped files (no changes needed): {len(skipped_files)}")
        for file in skipped_files:
            print(f"   - {file}")
    
    if error_files:
        print(f"\n❌ Error files: {len(error_files)}")
        for file in error_files:
            print(f"   - {file}")
    
    print(f"\n🎯 Total processed: {len(workflow_files)} files")
    print("✅ All GitHub Actions workflows now use self-hosted runners!")

if __name__ == "__main__":
    main()
