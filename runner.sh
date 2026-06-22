
#!/bin/bash
# ShadowGhost Runner with auto-update

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the tool (auto-update is now built into shadowghost.py)
cd "$INSTALL_DIR"
if [ -d "shadowghost-env" ]; then
    source shadowghost-env/bin/activate
    python3 shadowghost.py "$@"
    deactivate
else
    python3 shadowghost.py "$@"
fi
