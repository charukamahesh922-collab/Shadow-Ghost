
#!/bin/bash
# ShadowGhost Auto-Update Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}[*] ShadowGhost Update Check${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}[!] Git not found. Installing...${NC}"
    sudo apt-get update && sudo apt-get install git -y
fi

# Initialize git if not exists
if [ ! -d ".git" ]; then
    echo -e "${BLUE}[*] Initializing git repository...${NC}"
    git init
    git remote add origin https://github.com/charukamahesh922-collab/Shadow-Ghost.git
    git fetch origin
    git reset --hard origin/main 2>/dev/null || git reset --hard origin/master
    echo -e "${GREEN}[✓] Repository initialized${NC}"
    exit 0
fi

# Ensure remote is correct
git remote set-url origin https://github.com/charukamahesh922-collab/Shadow-Ghost.git 2>/dev/null

# Fetch latest changes
echo -e "${BLUE}[*] Fetching latest changes...${NC}"
git fetch origin --force

# Get current and latest commit
CURRENT=$(git rev-parse HEAD 2>/dev/null)
LATEST=$(git rev-parse origin/main 2>/dev/null || git rev-parse origin/master 2>/dev/null)

# Check if update available
if [ "$1" == "--silent-check" ]; then
    if [ "$CURRENT" != "$LATEST" ] && [ -n "$LATEST" ]; then
        echo -e "${YELLOW}[!] Updates available. Run 'shadowghost-update' to update.${NC}"
    fi
    exit 0
fi

if [ "$CURRENT" != "$LATEST" ] && [ -n "$LATEST" ]; then
    echo -e "${YELLOW}[!] Updates available!${NC}"
    echo -e "${BLUE}[*] Current: ${CURRENT:0:8}${NC}"
    echo -e "${BLUE}[*] Latest:  ${LATEST:0:8}${NC}"
    echo -e "${BLUE}[*] Updating ShadowGhost...${NC}"
    
    # Backup config files
    if [ -f "config/default.conf" ]; then
        cp config/default.conf /tmp/shadowghost_config.conf
        echo -e "${BLUE}[*] Config backed up${NC}"
    fi
    
    # Backup custom wordlists
    if [ -f "wordlists/custom.txt" ]; then
        cp wordlists/custom.txt /tmp/shadowghost_custom.txt
    fi
    
    # Pull latest changes
    echo -e "${BLUE}[*] Pulling latest code...${NC}"
    git reset --hard HEAD
    git pull origin main 2>/dev/null || git pull origin master
    
    # Restore config files
    if [ -f "/tmp/shadowghost_config.conf" ]; then
        mkdir -p config
        cp /tmp/shadowghost_config.conf config/default.conf
        rm /tmp/shadowghost_config.conf
        echo -e "${BLUE}[*] Config restored${NC}"
    fi
    
    if [ -f "/tmp/shadowghost_custom.txt" ]; then
        mkdir -p wordlists
        cp /tmp/shadowghost_custom.txt wordlists/custom.txt
        rm /tmp/shadowghost_custom.txt
    fi
    
    # Update dependencies
    if [ -f "requirements.txt" ] && [ -d "shadowghost-env" ]; then
        echo -e "${BLUE}[*] Updating dependencies...${NC}"
        source shadowghost-env/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt --upgrade
        deactivate
    fi
    
    echo -e "${GREEN}[✓] ✅ Update complete!${NC}"
else
    echo -e "${GREEN}[✓] ✅ Already up to date${NC}"
fi
EOF

chmod +x update.sh
