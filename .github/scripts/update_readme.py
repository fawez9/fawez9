#!/usr/bin/env python3
import os
import re
import requests
from bs4 import BeautifulSoup

# Get GitHub username from environment variable
USERNAME = os.environ.get('USERNAME', 'fawez9')

def get_streak_count():
    """Fetch the current GitHub streak count using web scraping."""
    url = f"https://github-readme-streak-stats.herokuapp.com/?user={USERNAME}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the HTML and extract the current streak
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find the current streak text - this might need adjustment based on actual HTML structure
        current_streak_element = soup.find('text', {'class': 'current-streak'})
        
        if current_streak_element:
            streak_text = current_streak_element.text
            # Extract the number from text like "5 days"
            streak_count = int(re.search(r'(\d+)', streak_text).group(1))
            return streak_count
        
        # Alternative approach if the above method doesn't work
        # Look for SVG text elements that might contain the streak information
        text_elements = soup.find_all('text')
        for element in text_elements:
            if 'Current Streak' in element.text:
                # The next element should contain the streak number
                streak_text = element.find_next('text').text
                streak_count = int(re.search(r'(\d+)', streak_text).group(1))
                return streak_count
                
        # If we couldn't find the streak count, use the GitHub API as fallback
        return get_streak_from_api()
        
    except Exception as e:
        print(f"Error fetching streak count: {e}")
        # Fallback to API method
        return get_streak_from_api()

def get_streak_from_api():
    """Alternative method using GitHub API to estimate streak based on recent commits."""
    token = os.environ.get('GITHUB_TOKEN')
    headers = {'Authorization': f'token {token}'} if token else {}
    
    # Get recent commit activity
    url = f"https://api.github.com/users/{USERNAME}/events"
    response = requests.get(url, headers=headers)
    data = response.json()
    
    # Count consecutive days with commits
    # This is a simplified version and might not match GitHub's actual streak calculation
    # but serves as a fallback method
    days_with_commits = set()
    for event in data:
        if event['type'] == 'PushEvent':
            date = event['created_at'].split('T')[0]
            days_with_commits.add(date)
    
    # Simple approximation - count the number of unique days
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
    
    # Update the theme in streak stats URL - preserve all other parameters
    content = re.sub(
        r'github-readme-streak-stats\.herokuapp\.com/\?user=fawez9&theme=[a-zA-Z0-9]+',
        f'github-readme-streak-stats.herokuapp.com/?user=fawez9&theme={theme}',
        content
    )
    
    # Handle case where there might be additional parameters
    content = re.sub(
        r'github-readme-streak-stats\.herokuapp\.com/\?user=fawez9(&[^"]+&)theme=[a-zA-Z0-9]+',
        f'github-readme-streak-stats.herokuapp.com/?user=fawez9\\1theme={theme}',
        content
    )
    
    # Handle potential URL format with more complex parameter structure
    streak_pattern = r'(github-readme-streak-stats\.herokuapp\.com/\?)([^"]+)'
    
    def update_theme_param(match):
        base_url = match.group(1)
        params_str = match.group(2)
        
        # Parse the parameters
        params = {}
        for param in params_str.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value
        
        # Update the theme parameter
        params['theme'] = theme
        
        # Reconstruct the URL
        new_params = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}{new_params}"
    
    content = re.sub(streak_pattern, update_theme_param, content)
    
    # Update the theme in GitHub stats URLs using the same pattern-based approach
    stats_pattern = r'(github-readme-stats\.vercel\.app/api\?)([^"]+)'
    content = re.sub(stats_pattern, update_theme_param, content)
    
    # Update the theme in top languages URL
    langs_pattern = r'(github-readme-stats\.vercel\.app/api/top-langs/\?)([^"]+)'
    content = re.sub(langs_pattern, update_theme_param, content)
    
    # Write the updated content back to README.md
    with open('README.md', 'w') as file:
        file.write(content)
    
    print("README.md updated successfully.")

if __name__ == "__main__":
    streak_count = get_streak_count()
    update_readme_theme(streak_count)
