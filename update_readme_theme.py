import os
import re
from pathlib import Path
import requests
from datetime import datetime, timedelta

# Configuration
USERNAME = "fawez9"
README_PATH = Path("README.md")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Optional but recommended

# Themes based on streak level
THEMES = {
    "low": "radical",
    "medium": "merko",
    "high": "onedark"
}

def get_streak_days():
    """Fetch GitHub streak using GitHub API"""
    url = f"https://api.github.com/users/{USERNAME}/events"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else ""
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        events = response.json()
        
        # Find the longest consecutive streak
        current_streak = 0
        last_date = None
        
        for event in events:
            if 'created_at' not in event:
                continue
                
            date = datetime.strptime(
                event['created_at'], 
                "%Y-%m-%dT%H:%M:%SZ"
            ).date()
            
            if last_date is None or date == last_date - timedelta(days=1):
                current_streak += 1
            else:
                break  # Exit on first break in streak
            last_date = date
        
        return current_streak
    except Exception as e:
        print(f"⚠️ Error fetching streak: {e}")
        return 0

def select_theme(streak_days):
    """Choose theme based on streak duration"""
    if streak_days < 3:
        return THEMES["low"]
    if 3 <= streak_days <= 7:
        return THEMES["medium"]
    return THEMES["high"]

def update_readme(theme):
    """Update GitHub stats URLs with new theme"""
    try:
        with open(README_PATH, "r", encoding="utf-8") as file:
            content = file.read()

        patterns = [
            r'(github-readme-streak-stats\.herokuapp\.com/\?user=fawez9&theme=)([^&"]+)',
            r'(github-readme-stats\.vercel\.app/api\?username=fawez9&show_icons=true&theme=)([^&"]+)',
            r'(github-readme-stats\.vercel\.app/api/top-langs/\?username=fawez9&layout=compact&theme=)([^&"]+)'
        ]

        new_content = content
        for pattern in patterns:
            new_content = re.sub(pattern, rf'\1{theme}', new_content)

        if new_content != content:
            with open(README_PATH, "w", encoding="utf-8") as file:
                file.write(new_content)
            return True
        return False
    except Exception as e:
        print(f"❌ Error updating README: {e}")
        return False

if __name__ == "__main__":
    streak = get_streak_days()
    print(f"GitHub Streak: {streak} days")
    new_theme = select_theme(streak)
    updated = update_readme(new_theme)
    
    # Updated output method (GHES 2022+)
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        print(f"changed={str(updated).lower()}", file=f)
