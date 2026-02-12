#!/usr/bin/env python3
"""Create GitHub repository for DAVID project."""
import json
import os
import sys
import requests

# Load PAT from AutoLeads keys (same user)
keys_path = '../autoleads/config/keys.json'
try:
    with open(keys_path) as f:
        keys = json.load(f)
        token = keys['GITHUB_PAT']
except Exception as e:
    print(f"Failed to load PAT: {e}")
    sys.exit(1)

repo_name = "david-version-1"
description = "DAVID: Design Assistant for Vehicle Innovation & Development - Engineering assistant for generative design, simulation, and CAD"
private = False  # Public repo

url = "https://api.github.com/user/repos"
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}
data = {
    "name": repo_name,
    "description": description,
    "private": private,
    "auto_init": False,
    "has_issues": True,
    "has_projects": False,
    "has_wiki": False
}

print(f"Creating repository '{repo_name}'...")
resp = requests.post(url, headers=headers, json=data)

if resp.status_code == 201:
    repo_info = resp.json()
    clone_url = repo_info['clone_url']
    print(f"✅ Repository created: {clone_url}")
    
    # Set remote and push
    os.system('git add .')
    os.system('git commit -m "Initial commit: project structure, README, memory logs"')
    os.system(f'git remote add origin {clone_url}')
    os.system('git push -u origin main')
    print("✅ Initial commit pushed to GitHub.")
else:
    print(f"❌ Failed to create repo: {resp.status_code}")
    print(resp.text)
    sys.exit(1)