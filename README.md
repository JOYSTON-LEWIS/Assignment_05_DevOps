# 📌 Assignment_05_DevOps: Building CI-CD Pipeline Tool

## 📖 Overview
This project demonstrates a basic Continuous Integration and Continuous Deployment (CI/CD) pipeline using a custom-built toolchain. The objective is to automatically deploy a static HTML website hosted on a GitHub repository to an Nginx web server running on an AWS EC2 or local Linux instance.

The pipeline follows these steps:
1. A static HTML project is created and version-controlled via GitHub.
2. A web server environment is prepared using Nginx on a remote instance.
3. A Python script interacts with the GitHub API to detect new commits.
4. A Bash script handles code deployment by cloning the latest repository version and restarting the Nginx server.
5. A cron job is scheduled to periodically check for updates and trigger deployment.
6. The complete setup is tested by committing changes to the repository and observing the automatic update on the server.

This setup emulates core CI/CD principles and provides a foundational understanding of automating deployments without using third-party CI/CD tools.

## 📌 Task 1: Set Up a Simple HTML Project
Create a simple HTML project and push it to a GitHub repository.

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask To-Do List API</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>

<body>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <div class="container mt-5">
        <div class="card">
            <div class="card-body">
                <h2 class="card-title">CronTab Automation 01</h2>
                <blockquote class="blockquote">
                    <p>Build a Flask API to manage a simple to-do list. Each to-do item is stored as a dictionary in a
                        list.</p>
                    <ol class="list-group list-group-numbered">
                        <strong>Tasks:</strong>
                        <li class="list-group-item">Add a product with id, name, price, and quantity fields (POST
                            /products).</li>
                        <li class="list-group-item">Fetch all products (GET /products).</li>
                        <li class="list-group-item">Fetch products below a certain stock level (GET /products/low-stock/
                            <threshold>).</li>
                        <li class="list-group-item">Update product details (PUT /products/<id>).</li>
                        <li class="list-group-item">Delete a product (DELETE /products/<id>).</li>
                    </ol>
                </blockquote>
            </div>
        </div>
    </div>
</body>

</html>
```

#### 📸 Output Screenshots

![Img_01](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_01.png)
![Img_02](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_02.png)

## 📌 Task 2: Set Up an AWS EC2/Local Linux Instance with Nginx
Set up an AWS EC2 instance or a local Linux instance and install Nginx to serve the HTML content.

#### 📸 Output Screenshots

![Img_03](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_03.png)
![Img_04](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_04.png)
![Img_05](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_05.png)
![Img_06](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_06.png)

## :warning: Create `secret_key.env` File

Follow these steps to create the `secret_key.env` file, which is required in the deployment scripts:

### **Important Note:**
- **Fork the repository** and **generate your own Personal Access Token (PAT)** from GitHub. 
- If you've named your forked repository differently, **update the `REPOSITORY_NAME`** below accordingly.

### Run the following commands to create the `secret_key.env` file:

```bash
nano secret_key.env
```

Then add the following content:
```bash
ACCESS_TOKEN=INPUT_YOUR_CLASSIC_GITHUB_PAT_TOKEN_HERE
REPOSITORY_NAME=JOYSTON-LEWIS/Assignment_05_DevOps
```

Note: Ensure to replace INPUT_YOUR_CLASSIC_GITHUB_PAT_TOKEN_HERE with your actual GitHub PAT token and update the REPOSITORY_NAME if necessary.

## 📌 Task 3: Write a Python Script to Check for New Commits
Create a Python script that uses the GitHub API to check for new commits in the repository.

Copy the File Name for the Python File
```python
CICD_EC2.py
```

Copy the Code for the Python File
```python
#!/usr/bin/env python3

import os
import subprocess
import sys
from datetime import datetime

# Redirect all stdout and stderr to a log file with timestamped sections
LOG_FILE = "CICD_EC2_PYTHON_LOGS"

def start_logging():
    sys.stdout = open(LOG_FILE, "a")
    sys.stderr = sys.stdout
    print("\n-------------------------------")
    print(f"📅 Trigger Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-------------------------------")

start_logging()

# Ensure PyGithub is installed
try:
    from github import Github
except ImportError:
    print("📦 PyGithub not found. Attempting to install...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyGithub"])
        from github import Github
        print("✅ PyGithub installed successfully.")
    except Exception as e:
        print(f"❌ Failed to install PyGithub: {e}")
        sys.exit(1)

# Load environment variables from the .env file
def load_env(filename):
    with open(filename, "r") as file:
        for line in file:
            if "=" in line and not line.startswith("#"):  # Ignore comments
                key, value = line.strip().split("=", 1)
                os.environ[key] = value  # Set as environment variable

# Load values from secret_key.env
load_env("secret_key.env")

# Replace with your Personal Access Token
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REPO_NAME = os.getenv("REPOSITORY_NAME")

# Initialize GitHub instance
g = Github(ACCESS_TOKEN)
repo = g.get_repo(REPO_NAME)

# Fetch the latest commits
commits = repo.get_commits()
latest_commit_shas = [commit.sha[:7] for commit in commits[:5]]  # Get short SHAs of latest 5 commits

# File to store commit IDs
commit_file = "existing_commits.txt"

# Check if this is the first run (file doesn't exist)
if not os.path.exists(commit_file):
    # Create the file with the latest SHAs
    with open(commit_file, "w") as f:
        for sha in latest_commit_shas:
            f.write(sha + "\n")  # Write initial SHAs

    print("First run detected. Commit file created. Triggering deployment...")

    process = subprocess.Popen(["/bin/bash", "/home/ubuntu/CICD_EC2_DEPLOY.sh"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        print(line, end="")  # Stream logs to file
    process.wait()

    print("Deployment script finished.")
else:
    # Read existing commit SHAs from the file
    existing_commits = set()
    with open(commit_file, "r") as f:
        existing_commits = set(line.strip() for line in f)

    # Identify new commits
    new_commits = [sha for sha in latest_commit_shas if sha not in existing_commits]

    # If new commits exist, update the file and trigger CICD_EC2_DEPLOY.sh
    if new_commits:
        with open(commit_file, "w") as f:
            for sha in latest_commit_shas:
                f.write(sha + "\n")  # Write the updated list

        print("New commits detected! Triggering deployment...")

        process = subprocess.Popen(["/bin/bash", "/home/ubuntu/CICD_EC2_DEPLOY.sh"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end="")  # Stream logs to file
        process.wait()

        print("Deployment script finished.")
    else:
        print("No new commits detected. File remains unchanged.")

# Print commit details
for commit in commits[:5]:
    short_sha = commit.sha[:7]  # Short SHA (first 7 characters)
    print(f"Short SHA: {short_sha}")
    print(f"Full SHA: {commit.sha}")
    print(f"Message: {commit.commit.message}")
    print(f"Author: {commit.commit.author.name}")
    print(f"Date: {commit.commit.author.date}\n")
```

#### 📸 Output Screenshots

![Img_08](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_08.png)
![Img_09](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_09.png)

## 📌 Task 4: Write a Bash Script to Deploy the Code
Create a bash script that:
- Clones the latest code from the GitHub repository.
- Restarts Nginx to serve the new version of the site.

Copy the File Name for the Bash Script
```bash
CICD_EC2_DEPLOY.sh
```

Copy the Code for the Bash Script
```bash
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

```

#### 📸 Output Screenshots

![Img_07](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_07.png)

## 📌 Task 5: Set Up a Cron Job to Run the Python Script
Create a cron job that runs the Python script at regular intervals to check for new commits.

## :lock: Ensure Correct Permissions for Scripts

To avoid permission issues while running the deployment scripts, you need to update the file permissions. Run the following commands to grant the necessary access:

### Run the following commands:

```bash
sudo chmod 666 CICD_EC2.py
sudo chmod 666 CICD_EC2_DEPLOY.sh
```

#### 📸 Output Screenshots

![Img_10](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_10.png)
![Img_11](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_11.png)

## 📌 Task 6: Test the Setup
Make a new commit to the GitHub repository and verify that the changes are automatically deployed and served via Nginx.

#### 📸 Output Screenshots

![Img_12](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_12.png)
![Img_13](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_13.png)
![Img_14](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_14.png)
![Img_15](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_15.png)
![Img_16](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_16.png)
![Img_17](https://github.com/JOYSTON-LEWIS/My-Media-Repository/blob/main/Assignment_05_DevOps_Outputs_Images/Img_17.png)

## :sparkles: Enhancements
- Python Script Includes automatic logging into a file called as "CICD_EC2_PYTHON_LOGS" in a presentable manner
- Bash Script Includes automatic logging into a file called as "CICD_EC2_DEPLOY_LOGS" in a presentable manner

## :rocket: Next Version Release
A Single Bash Script which can be put into Advanced Data Section while creating EC2 Instance on Amazon to automate the following:
- Create Python File and its logs with custom name
- Create Bash Script and its logs with custom name
- Assign Permissions to both scripts to be executable
- Create Crontab with a custom CRONJOB

## 📜 License
This project is licensed under the MIT License.

## 🤝 Contributing
Feel free to fork and improve the scripts! ⭐ If you find this project useful, please consider starring the repo—it really helps and supports my work! 😊

## 📧 Contact
For any queries, reach out via GitHub Issues.

---

🎯 **Thank you for reviewing this project! 🚀**
