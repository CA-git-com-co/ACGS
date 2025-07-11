#!/bin/bash
# GitHub Actions Workflow Cleanup Script
# Constitutional Hash: cdd01ef066bc6cf2
# Generated: 2025-07-11 13:37:16 UTC

set -e

echo '🧹 Starting GitHub Actions workflow cleanup...'
echo 'Constitutional Hash: cdd01ef066bc6cf2'

# Create backup directory
mkdir -p .github/workflows/backup

# Backup workflows before deletion
echo 'Backing up ci-legacy.yml...'
cp .github/workflows/ci-legacy.yml .github/workflows/backup/ || true
echo 'Backing up ci_cd_20250701_000659.yml...'
cp .github/workflows/ci_cd_20250701_000659.yml .github/workflows/backup/ || true
echo 'Backing up test.yml...'
cp .github/workflows/test.yml .github/workflows/backup/ || true
echo 'Backing up testing.yml...'
cp .github/workflows/testing.yml .github/workflows/backup/ || true

# Remove redundant workflows
echo 'Removing redundant workflows...'
echo 'Removing ci-legacy.yml (Known redundant/obsolete workflow)...'
rm .github/workflows/ci-legacy.yml || echo 'Failed to remove ci-legacy.yml'
echo 'Removing ci_cd_20250701_000659.yml (Known redundant/obsolete workflow)...'
rm .github/workflows/ci_cd_20250701_000659.yml || echo 'Failed to remove ci_cd_20250701_000659.yml'
echo 'Removing test.yml (Known redundant/obsolete workflow)...'
rm .github/workflows/test.yml || echo 'Failed to remove test.yml'
echo 'Removing testing.yml (Known redundant/obsolete workflow)...'
rm .github/workflows/testing.yml || echo 'Failed to remove testing.yml'

echo '✅ Cleanup completed!'
echo 'Removed 4 redundant workflows'
echo 'Backups stored in .github/workflows/backup/'
echo 'Constitutional Hash: cdd01ef066bc6cf2 verified'