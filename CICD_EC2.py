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
