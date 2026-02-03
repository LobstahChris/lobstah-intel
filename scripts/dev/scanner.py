import os
import json
import subprocess
from datetime import datetime

# Config
API_KEY = os.environ.get("MOLTBOOK_API_KEY")
INTEL_DIR = "/home/ubuntu/.openclaw/Desktop/projects/lobstah-fun/web/content/docs/library"

def fetch_active_submolts():
    """Discover all active submolts on the platform."""
    url = "https://www.moltbook.com/api/v1/submolts?limit=50"
    cmd = ["curl", "-s", url, "-H", f"Authorization: Bearer {API_KEY}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        # Return names of all discovered submolts
        return [s.get("name") for s in data.get("submolts", []) if s.get("name")]
    except Exception as e:
        print(f"Error discovering submolts: {e}")
        return ["shipping", "openclaw-explorers", "ai-agents", "general"] # Fallback

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
    submolts = fetch_active_submolts()
    print(f"Discovered {len(submolts)} active submolts. Scanning...")
    
    all_posts = []
    for sub in submolts:
        posts = fetch_feed(sub)
        all_posts.extend(posts)
    
    # Sort by date
    all_posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    # Filter unique IDs
    seen = set()
    unique_posts = []
    for p in all_posts:
        if p['id'] not in seen:
            unique_posts.append(p)
            seen.add(p['id'])

    # Build Markdown
    md = ""
    md += f"### Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} EST\n\n"
    
    for p in unique_posts[:25]:
        title = p.get('title', 'No Title')
        content = p.get('content', '')
        author = p.get('author_id', 'Unknown')
        sub = p.get('submolt', {}).get('name', 'unknown')
        date = p.get('created_at', '')[:19].replace('T', ' ')
        
        md += f"#### {title}\n"
        md += f"**Submolt:** `m/{sub}` | **Date:** {date}\n\n"
        md += f"{content}\n\n"
        md += "---\n\n"

    # Write to daily research log (Persistent history)
    daily_path = os.path.join(INTEL_DIR, "platforms", "moltbook.com", "research", f"{datetime.now().strftime('%Y-%m-%d')}.mdx")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(daily_path), exist_ok=True)
    
    with open(daily_path, "a") as f:
        f.write(f"\n\n## Update: {datetime.now().strftime('%H:%M:%S')}\n")
        f.write(md)

    # NEW: Also update the project spotlight index if relevant projects are found
    # This is a stub for future auto-curation logic
    print("Injected intelligence into daily research logs.")

if __name__ == "__main__":
    generate_report()
