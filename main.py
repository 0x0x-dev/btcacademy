import requests
import re
import json
import os

# Define a function to fetch and parse JSON data
def fetch_posts(page):
    url = f"https://btcacademy.online/wp-json/wp/v2/posts?categories=3181&per_page=10&order=asc&page={page}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json(), None
    else:
        return None, response.status_code

# Function to extract currency and halal status
def extract_currency_and_halal_status(title, content):
    currency = None
    is_halal = None
    
    # Extract the currency using a regular expression
    currency_match = re.search(r"([A-Z0-9]+)", title)
    if currency_match:
        currency = currency_match.group(1)
    
    # Check if the content mentions the currency is halal
    if currency:
        if f"فإن عملة {currency} حلال" in content or "والله أعلم" in content:
            is_halal = True
        elif f"فإن عملة {currency} حرام" in content or "لا ننصح بالاستثمار بها" in content:
            is_halal = False
    
    return currency, is_halal

# Load existing posts from JSON file
def load_existing_posts(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

# Save posts to JSON file
def save_posts(filename, posts):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(posts, file, ensure_ascii=False, indent=4)

# Fetch posts and extract information
def fetch_all_posts():
    current_page = 1
    existing_posts = load_existing_posts('posts.json')
    updated_posts = existing_posts[:]

    while True:
        posts, error = fetch_posts(current_page)
        if error:
            print(f"Error fetching posts: {error}")
            break
        
        # Stop pagination if no posts are returned
        if not posts:
            print("Reached end of pages.")
            break
        
        # Process posts
        for post in posts:
            guid = post['guid']['rendered']
            title = post['title']['rendered']
            content = post['content']['rendered']
            currency, is_halal = extract_currency_and_halal_status(title, content)
            
            # Only add post if currency is not None
            if currency is not None:
                post_data = {
                    'guid': guid,
                    'currency': currency,
                    'is_halal': is_halal
                }
                
                # Check if the post already exists and if it has changed
                if post_data not in existing_posts:
                    updated_posts.append(post_data)
        
        # Move to the next page
        current_page += 1
    
    # Save updated posts to JSON file
    save_posts('posts.json', updated_posts)

# Start fetching all posts
fetch_all_posts()
