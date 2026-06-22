#!/bin/bash
# ShadowGhost Installation Script

echo "👻 Installing ShadowGhost..."
echo "=============================="

# Check Python version
python3 -c "import sys; exit(0) if sys.version_info >= (3,8) else exit(1)"
if [ $? -ne 0 ]; then
    echo "❌ Python 3.8+ is required"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Create directories
mkdir -p wordlists
mkdir -p reports
mkdir -p config

# Create default wordlists
cat > wordlists/directories.txt << EOF
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

cat > wordlists/subdomains.txt << EOF
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

echo "✅ Installation complete!"
echo ""
echo "Usage: python3 shadowghost.py -t example.com"
echo ""
echo "For help: python3 shadowghost.py -h"
