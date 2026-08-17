import requests 
from bs4 import BeautifulSoup
import json

# URL to scrape
url = "https://github.com/prit-nayi"

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    # Send GET request
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    # Parse HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract profile information
    profile_data = {}
    
    # Get username
    username_elem = soup.find('span', class_='p-nickname')
    if username_elem:
        profile_data['username'] = username_elem.text.strip()
    
    # Get full name
    name_elem = soup.find('span', class_='p-name')
    if name_elem:
        profile_data['full_name'] = name_elem.text.strip()
    
    # Get bio/description
    bio_elem = soup.find('div', class_='p-note')
    if bio_elem:
        profile_data['bio'] = bio_elem.text.strip()
    
    # Get location
    location_elem = soup.find('span', class_='p-label')
    if location_elem:
        profile_data['location'] = location_elem.text.strip()
    
    # Get repositories count
    repos_elem = soup.find('a', {'href': '/prit-nayi?tab=repositories'})
    if repos_elem:
        repo_count = repos_elem.find('span', class_='Counter')
        if repo_count:
            profile_data['repositories_count'] = repo_count.text.strip()
    
    # Print extracted data
    print("=" * 60)
    print("GITHUB PROFILE SCRAPING RESULTS")
    print("=" * 60)
    print(json.dumps(profile_data, indent=2, ensure_ascii=False))
    print("=" * 60)
    
    # Save to JSON file
    with open('scraped_data.json', 'a', encoding='utf-8') as f:
        json.dump(profile_data, f, indent=2, ensure_ascii=False)
    print("\nData saved to 'scraped_data.json'")
    
except requests.exceptions.RequestException as e:
    print(f"Error fetching the webpage: {e}")
except Exception as e:
    print(f"Error parsing the content: {e}")
