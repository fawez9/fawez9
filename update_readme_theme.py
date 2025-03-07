import os
import re
from pathlib import Path
import requests

# Configuration
USERNAME = "fawez9"
README_PATH = Path("README.md")

# Themes based on streak level
THEMES = {
    "low": "radical",
    "medium": "merko",
    "high": "onedark"
}

def get_streak_days():
    """Fetch current GitHub streak count"""
    url = f"https://github-readme-streak-stats.herokuapp.com/?user={USERNAME}&theme=dark"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        match = re.search(r'data-count="(\d+)"', response.text)
        return int(match.group(1)) if match else 0
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
    print(f"::set-output name=changed::{str(updated).lower()}")
