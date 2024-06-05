import requests
import re
import json

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

# Save posts to JSON file (overwrites if exists)
def save_posts(filename, posts):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(posts, file, ensure_ascii=False, indent=4)

# Fetch posts and extract information
def fetch_all_posts():
    current_page = 1
    all_posts = []

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
                all_posts.append(post_data)
                
        # Move to the next page
        current_page += 1
    
    # Save posts to JSON file (overwrite if exists)
    save_posts('posts.json', all_posts)

# Start fetching all posts
fetch_all_posts()
