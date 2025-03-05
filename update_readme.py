import requests
import re

# GitHub username
USERNAME = "fawez9"
README_PATH = "README.md"

# Themes based on streak level
THEMES = {
    "low": "red-dark",    # Streak < 3 days
    "medium": "green-dark", # Streak 3-7 days
    "high": "gold-dark"   # Streak > 7 days
}

# Fetch GitHub Streak data
def get_streak_days():
    url = f"https://github-readme-streak-stats.herokuapp.com/?user={USERNAME}&theme=dark"
    response = requests.get(url)
    if response.status_code == 200:
        match = re.search(r'data-count="(\d+)"', response.text)  # Extract streak count
        if match:
            return int(match.group(1))
    return 0  # Default if failed

# Select the theme based on the streak count
def select_theme(streak_days):
    if streak_days < 3:
        return THEMES["low"]
    elif 3 <= streak_days <= 7:
        return THEMES["medium"]
    else:
        return THEMES["high"]

# Update README with new theme
def update_readme(theme):
    with open(README_PATH, "r") as file:
        content = file.read()

    # Replace theme in streak and stats URLs
    new_content = re.sub(
        r'(github-readme-streak-stats\.herokuapp\.com/\?user=fawez9&theme=)[^"]+',
        rf'\1{theme}',
        content
    )
    new_content = re.sub(
        r'(github-readme-stats\.vercel\.app/api\?username=fawez9&show_icons=true&theme=)[^"]+',
        rf'\1{theme}',
        new_content
    )
    new_content = re.sub(
        r'(github-readme-stats\.vercel\.app/api/top-langs/\?username=fawez9&layout=compact&theme=)[^"]+',
        rf'\1{theme}',
        new_content
    )

    with open(README_PATH, "w") as file:
        file.write(new_content)

# Run the update process
streak_days = get_streak_days()
theme = select_theme(streak_days)
update_readme(theme)
