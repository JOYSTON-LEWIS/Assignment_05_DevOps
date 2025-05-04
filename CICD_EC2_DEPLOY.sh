#!/bin/bash

set -e  # Exit on errors

LOG_FILE="CICD_EC2_DEPLOY_LOGS"
DATE_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# Load secrets from env file
if [ -f secret_key.env ]; then
  export $(grep -v '^#' secret_key.env | xargs)
else
  echo "❌ secret_key.env file not found!" >> "$LOG_FILE"
  exit 1
fi

ACCESS_TOKEN=${ACCESS_TOKEN}
REPOSITORY_NAME=${REPOSITORY_NAME}
DEST_DIR="/var/www/html"

# Determine if repo is private using GitHub API
echo "🌐 Checking repository visibility..." >> "$LOG_FILE"

IS_PRIVATE=$(curl -s -H "Authorization: token ${ACCESS_TOKEN}" \
  "https://api.github.com/repos/${REPOSITORY_NAME}" | grep '"private":' | awk '{print $2}' | tr -d ',')

if [ "$IS_PRIVATE" == "true" ]; then
  echo "🔒 Repo is private. Using token-authenticated clone..." >> "$LOG_FILE"
  REPO_URL="https://${ACCESS_TOKEN}@github.com/${REPOSITORY_NAME}.git"
else
  echo "🔓 Repo is public. Using standard HTTPS clone..." >> "$LOG_FILE"
  REPO_URL="https://github.com/${REPOSITORY_NAME}.git"
fi

# Begin logging
{
echo "----------------------------"
echo "📅 Trigger Time: $DATE_TIME"
echo "----------------------------"

echo "📦 Updating package list..."
sudo apt update -y

# Function to check and install a package
install_if_missing() {
  if ! dpkg -s "$1" >/dev/null 2>&1; then
    echo "🔧 Installing $1..."
    sudo apt install -y "$1"
  else
    echo "✅ $1 is already installed."
  fi
}

# Upgrade system packages
echo "⬆️ Upgrading system packages..."
sudo apt upgrade -y

# Install required packages if not present
install_if_missing git
install_if_missing python3
install_if_missing python3-pip
install_if_missing nginx
install_if_missing curl  # Needed for visibility check

# Ensure nginx is running
echo "🚀 Ensuring nginx is enabled and started..."
sudo systemctl enable nginx
sudo systemctl start nginx

# Clone and deploy static site
echo "📁 Cloning repo: $REPO_URL"
git clone "$REPO_URL" temp_site

if [ -f temp_site/index.html ]; then
  echo "📂 Deploying index.html to Nginx root..."
  sudo cp temp_site/index.html "$DEST_DIR/index.html"
else
  echo "⚠️ index.html not found in repo root. Skipping deployment."
fi

echo "🧹 Cleaning up..."
rm -rf temp_site

echo "✅ Done. Visit the EC2 public IP in your browser."
echo "----------------------------"
echo ""

} >> "$LOG_FILE" 2>&1
