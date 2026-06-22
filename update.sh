#!/bin/bash
# ShadowGhost Update Script (Manual fallback)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[*] Manual update check..."

if [ -d ".git" ]; then
    # Stash local changes if any
    git stash push -m "Auto-stash before update" 2>/dev/null || true
    
    # Fetch and pull
    git fetch origin
    git pull origin main 2>/dev/null || git pull origin master
    
    # Pop stashed changes
    git stash pop 2>/dev/null || true
    
    # Update dependencies if needed
    if [ -f "requirements.txt" ] && [ -d "shadowghost-env" ]; then
        echo "[*] Updating dependencies..."
        source shadowghost-env/bin/activate
        pip install -r requirements.txt --upgrade
        deactivate
    fi
    
    echo "[✓] Update complete"
else
    echo "[!] Not a git repository"
fi
