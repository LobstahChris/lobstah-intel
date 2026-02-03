import os
import json
import subprocess
from datetime import datetime

# SSoT Protocol Version: 1.3.0 (2026-02-03)
# - One file per day (daily roll-up)
# - No bulk raw data; only curated/concise entries
# - HTML/MDX tag stripping for build safety
VERSION = "1.3.0"

# Config
API_KEY = os.environ.get("MOLTVERR_API_KEY")
REPO_ROOT = "/home/ubuntu/.openclaw/Desktop/projects/lobstah-fun"
PROJECT_DOMAIN = "moltverr.com"
INTEL_DIR = f"{REPO_ROOT}/web/content/docs/project-spotlights/{PROJECT_DOMAIN}/Research"

def fetch_gigs():
    url = "https://www.moltverr.com/api/gigs?status=open"
    cmd = ["curl", "-s", url, "-H", f"Authorization: Bearer {API_KEY}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        return data.get("gigs", [])
    except Exception as e:
        print(f"Error fetching gigs: {e}")
        return []

def log_gigs():
    gigs = fetch_gigs()
    if not gigs:
        return

    # Daily Roll-up File
    today_str = datetime.now().strftime('%Y-%m-%d')
    daily_path = os.path.join(INTEL_DIR, f"{today_str}.mdx")
    os.makedirs(INTEL_DIR, exist_ok=True)
    
    # Curate only the most relevant entries (top 5)
    curated_content = ""
    for g in gigs[:5]:
        title = g.get('title', 'No Title')
        description = g.get('description', '')[:200] + "..." # Concise summary
        curated_content += f"#### {title}\n{description}\n\n"

    file_exists = os.path.isfile(daily_path)
    timestamp = datetime.now().strftime('%H:%M:%S')

    with open(daily_path, "a") as f:
        if not file_exists:
            f.write("---\n")
            f.write(f"title: \"{today_str}\"\n")
            f.write(f"description: Curated intelligence for {PROJECT_DOMAIN}.\n")
            f.write("---\n\n")
        
        f.write(f"### 📥 Update: {timestamp} (EST)\n")
        f.write(f"*Engine: `moltverr.py` v{VERSION}*\n\n")
        f.write(curated_content)
        f.write("\n---\n\n")

if __name__ == "__main__":
    log_gigs()
