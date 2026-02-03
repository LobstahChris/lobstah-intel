import os
import json
import subprocess
from datetime import datetime

# SSoT Protocol Version: 1.3.0 (2026-02-03)
# - One file per day (daily roll-up)
# - Highly curated (top 3 most significant items)
# - HTML/MDX tag stripping
VERSION = "1.3.0"

# Config
API_KEY = os.environ.get("MOLTBOOK_API_KEY")
REPO_ROOT = "/home/ubuntu/.openclaw/Desktop/projects/lobstah-fun"
PROJECT_DOMAIN = "moltbook.com"
INTEL_DIR = f"{REPO_ROOT}/web/content/docs/project-spotlights/{PROJECT_DOMAIN}/Research"

def strip_tags(text):
    import re
    return re.sub(r'<[^>]+>', '', text)

def fetch_feed(submolt):
    url = f"https://www.moltbook.com/api/v1/posts?submolt={submolt}&sort=new&limit=20"
    cmd = ["curl", "-s", url, "-H", f"Authorization: Bearer {API_KEY}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        return data.get("posts", [])
    except:
        return []

def generate_report():
    submolts = ["shipping", "openclaw-explorers", "ai-agents", "general"]
    all_posts = []
    for sub in submolts:
        all_posts.extend(fetch_feed(sub))
    
    if not all_posts:
        return

    # Sort by significance/date and take only top 3 to avoid bulk
    all_posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    daily_path = os.path.join(INTEL_DIR, f"{today_str}.mdx")
    os.makedirs(INTEL_DIR, exist_ok=True)
    
    curated_content = ""
    for p in all_posts[:3]: # Only top 3 most recent/relevant
        title = strip_tags(p.get('title', 'No Title'))
        content = strip_tags(p.get('content', ''))[:300] + "..." # Limit length
        curated_content += f"#### {title}\n{content}\n\n"

    file_exists = os.path.isfile(daily_path)
    timestamp = datetime.now().strftime('%H:%M:%S')

    with open(daily_path, "a") as f:
        if not file_exists:
            f.write("---\n")
            f.write(f"title: \"{today_str}\"\n")
            f.write(f"description: Curated intelligence for {PROJECT_DOMAIN}.\n")
            f.write("---\n\n")
        
        f.write(f"### 📥 Update: {timestamp} (EST)\n")
        f.write(f"*Engine: `scanner.py` v{VERSION}*\n\n")
        f.write(curated_content)
        f.write("\n---\n\n")

if __name__ == "__main__":
    generate_report()
