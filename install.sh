#!/bin/bash
# ShadowGhost Installation

echo "👻 Installing ShadowGhost..."
echo "=============================="

# Create virtual environment
if [ ! -d "shadowghost-env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv shadowghost-env
fi

# Activate and install dependencies
echo "📦 Installing dependencies..."
source shadowghost-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Create directories
mkdir -p config wordlists reports

# Create default wordlists
cat > wordlists/directories.txt << 'EOF'
admin
login
wp-admin
api
v1
v2
assets
css
js
images
img
uploads
backup
temp
tmp
test
dev
staging
docs
documentation
help
info
about
contact
support
blog
news
shop
cart
checkout
account
profile
settings
dashboard
panel
console
manager
control
system
core
lib
vendor
node_modules
EOF

cat > wordlists/subdomains.txt << 'EOF'
www
mail
ftp
localhost
webmail
smtp
pop
ns1
webdisk
ns2
cpanel
whm
autodiscover
autoconfig
m
imap
test
ns
blog
pop3
dev
www2
admin
forum
news
vpn
ns3
mail2
new
mysql
old
lists
support
mobile
mx
static
docs
beta
shop
sql
secure
demo
cp
calendar
wiki
web
media
email
images
img
download
api
app
staging
test
EOF

# Install global runner
sudo cp runner.sh /usr/local/bin/shadowghost
sudo chmod +x /usr/local/bin/shadowghost

sudo cp update.sh /usr/local/bin/shadowghost-update
sudo chmod +x /usr/local/bin/shadowghost-update

echo ""
echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  shadowghost -t example.com     # Run the tool"
echo "  shadowghost --no-update        # Run without checking updates"
echo "  shadowghost-update             # Manually check for updates"
echo ""
echo "For help: shadowghost -h"
