#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="ifiasoft"
APP_DIR="/opt/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
REPO_URL="https://github.com/yourusername/ifiasoft.git"
BRANCH="main"
DOMAIN="your-domain.com"  # Replace with your domain

# Create application directory if it doesn't exist
sudo mkdir -p $APP_DIR

# Clone or update repository
if [ ! -d "$APP_DIR/.git" ]; then
    sudo git clone $REPO_URL $APP_DIR
else
    cd $APP_DIR
    sudo git fetch origin
    sudo git reset --hard origin/$BRANCH
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    sudo python3 -m venv $VENV_DIR
fi

# Activate virtual environment and install dependencies
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r $APP_DIR/requirements.txt

# Create static directory
sudo mkdir -p $APP_DIR/static

# Copy service file
sudo cp $APP_DIR/deploy/$APP_NAME.service /etc/systemd/system/

# Setup Nginx
if [ ! -f "/etc/nginx/sites-available/$APP_NAME" ]; then
    # Create Nginx configuration
    sudo cp $APP_DIR/deploy/nginx.conf /etc/nginx/sites-available/$APP_NAME
    sudo sed -i "s/your-domain.com/$DOMAIN/g" /etc/nginx/sites-available/$APP_NAME
    
    # Enable the site
    sudo ln -s /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
    
    # Remove default Nginx site
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test Nginx configuration
    sudo nginx -t
    
    # Reload Nginx
    sudo systemctl reload nginx
fi

# Setup SSL with Certbot if not already configured
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
    sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email your-email@example.com
fi

# Reload systemd and restart service
sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
sudo systemctl restart $APP_NAME

# Check service status
sudo systemctl status $APP_NAME

echo "Deployment completed successfully!" 