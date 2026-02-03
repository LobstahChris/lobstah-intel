import os
import json
import subprocess
from datetime import datetime

# SSoT Protocol Version: 1.3.1 (2026-02-03)
# - Daily roll-up with accordion (details) support
# - Atomic entry per update block
# - No redundant H1 headers
VERSION = "1.3.1"

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

    today_str = datetime.now().strftime('%Y-%m-%d')
    daily_path = os.path.join(INTEL_DIR, f"{today_str}.mdx")
    os.makedirs(INTEL_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime('%H:%M:%S')
    md_block = f"### 📥 Update: {timestamp} (EST)\n"
    md_block += f"*Engine: `moltverr.py` v{VERSION}*\n\n"

    for g in gigs[:5]:
        title = g.get('title', 'No Title')
        description = g.get('description', '')
        md_block += f"#### {title}\n"
        md_block += f"<details>\n<summary>View Gig Details</summary>\n"
        md_block += f"{description}\n"
        md_block += f"</details>\n\n"
        md_block += f"> **LobstahLead 🦞 Comment:** [DRAFT] Automated marketplace intake.\n\n---\n\n"

    file_exists = os.path.isfile(daily_path)
    with open(daily_path, "a") as f:
        if not file_exists:
            f.write("---\n")
            f.write(f"title: \"{today_str}\"\n")
            f.write(f"description: Curated intelligence for {PROJECT_DOMAIN}.\n")
            f.write("---\n\n")
        
        f.write(md_block)

if __name__ == "__main__":
    log_gigs()
