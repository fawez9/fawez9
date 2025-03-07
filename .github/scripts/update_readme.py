#!/usr/bin/env python3
import os
import re
import requests
from bs4 import BeautifulSoup

# Get GitHub username from environment variable
USERNAME = os.environ.get('USERNAME', 'fawez9')

def get_streak_count():
    """Fetch the current GitHub streak count using web scraping or GitHub API."""
    try:
        # Try GitHub API method first (more reliable)
        return get_streak_from_api()
    except Exception as e:
        print(f"Error fetching streak from API: {e}")
        # Fallback to scraping method
        return get_streak_from_scraping()

def get_streak_from_scraping():
    """Attempt to get streak count from streak-stats service."""
    url = f"https://github-readme-streak-stats.herokuapp.com/?user={USERNAME}&theme=radical"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_elements = soup.find_all('text')
        
        for element in text_elements:
            if 'Current Streak' in element.text:
                # The next element should contain the streak number
                streak_text = element.find_next('text').text
                streak_count = int(re.search(r'(\d+)', streak_text).group(1))
                return streak_count
                
        print("Couldn't find streak information in the response")
        return 0
        
    except Exception as e:
        print(f"Error in scraping method: {e}")
        return 0

def get_streak_from_api():
    """Estimate streak based on recent commits using GitHub API."""
    token = os.environ.get('GITHUB_TOKEN')
    headers = {'Authorization': f'token {token}'} if token else {}
    
    # Get recent commit activity
    url = f"https://api.github.com/users/{USERNAME}/events"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"API request failed: {response.status_code}")
        return 0
        
    data = response.json()
    
    # Count consecutive days with commits
    days_with_commits = set()
    for event in data:
        if event['type'] == 'PushEvent':
            date = event['created_at'].split('T')[0]
            days_with_commits.add(date)
    
    return len(days_with_commits)

def update_readme_theme(streak_count):
    """Update the README.md file with the appropriate theme based on streak count."""
    
    # Define themes based on streak count
    theme = "radical"  # Default theme
    if streak_count >= 5:
        theme = "onedark"
    elif streak_count >= 3:
        theme = "merko"
    
    print(f"Current streak: {streak_count}, Setting theme to: {theme}")
    
    # Read the current README content
    with open('README.md', 'r') as file:
        content = file.read()
    
    # Define the exact replacement patterns with complete URLs
    
    # 1. Streak Stats URL
    streak_pattern = r'<img src="https://github-readme-streak-stats\.herokuapp\.com/\?user=fawez9(?:&[^"]*)" alt="GitHub Streak" />'
    streak_replacement = f'<img src="https://github-readme-streak-stats.herokuapp.com/?user=fawez9&theme={theme}" alt="GitHub Streak" />'
    
    # 2. GitHub Stats URL
    stats_pattern = r'<img src="https://github-readme-stats\.vercel\.app/api\?username=fawez9(?:&[^"]*)" height="195" alt="GitHub Stats" />'
    stats_replacement = f'<img src="https://github-readme-stats.vercel.app/api?username=fawez9&show_icons=true&theme={theme}" height="195" alt="GitHub Stats" />'
    
    # 3. Top Languages URL
    langs_pattern = r'<img src="https://github-readme-stats\.vercel\.app/api/top-langs/\?username=fawez9(?:&[^"]*)" height="195" alt="Top Langs" />'
    langs_replacement = f'<img src="https://github-readme-stats.vercel.app/api/top-langs/?username=fawez9&layout=compact&theme={theme}" height="195" alt="Top Langs" />'
    
    # Apply the replacements
    content = re.sub(streak_pattern, streak_replacement, content)
    content = re.sub(stats_pattern, stats_replacement, content)
    content = re.sub(langs_pattern, langs_replacement, content)
    
    # Write the updated content back to README.md
    with open('README.md', 'w') as file:
        file.write(content)
    
    print("README.md updated successfully.")

if __name__ == "__main__":
    streak_count = get_streak_count()
    update_readme_theme(streak_count)
