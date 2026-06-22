#!/bin/bash
# ShadowGhost Runner with auto-update

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check for updates silently
if [ "$1" != "--no-update" ] && [ "$1" != "-nu" ]; then
    bash "$INSTALL_DIR/update.sh" --silent-check
fi

# Run the tool
cd "$INSTALL_DIR"
if [ -d "shadowghost-env" ]; then
    source shadowghost-env/bin/activate
    python3 shadowghost.py "$@"
    deactivate
else
    python3 shadowghost.py "$@"
fi
