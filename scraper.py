import requests
from bs4 import BeautifulSoup
import random
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock data generation based on search queries
MOCK_PRODUCTS = {
    "iphone 15": [
        {"website": "Amazon", "price": 72900, "rating": "4.5", "reviews": "10,234"},
        {"website": "Flipkart", "price": 71999, "rating": "4.6", "reviews": "15,000"},
        {"website": "Snapdeal", "price": 73500, "rating": "4.4", "reviews": "1,200"}
    ],
    "samsung s24": [
        {"website": "Amazon", "price": 79999, "rating": "4.3", "reviews": "8,500"},
        {"website": "Flipkart", "price": 80500, "rating": "4.5", "reviews": "11,000"},
        {"website": "Snapdeal", "price": 79999, "rating": "4.2", "reviews": "900"}
    ],
    "macbook air m3": [
        {"website": "Amazon", "price": 104900, "rating": "4.7", "reviews": "5,000"},
        {"website": "Flipkart", "price": 102990, "rating": "4.8", "reviews": "6,500"},
        {"website": "Snapdeal", "price": 105500, "rating": "4.6", "reviews": "800"}
    ]
}

def clean_price(price_str):
    """Clean the price string and convert it to a float."""
    try:
        # Remove currency symbols, commas, and whitespace
        clean_str = price_str.replace('₹', '').replace(',', '').replace('Rs.', '').strip()
        return float(clean_str)
    except (ValueError, AttributeError):
        return None

def scrape_amazon(query):
    """Attempt to scrape Amazon India for the given query."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept-Language': 'en-IN,en;q=0.9',
    }
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # This selector often changes
        results = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        if not results:
            return None
            
        first_result = results[0]
        title_elem = first_result.find('span', {'class': 'a-size-medium'})
        if not title_elem:
             title_elem = first_result.find('span', {'class': 'a-size-base-plus'})
             
        price_elem = first_result.find('span', {'class': 'a-price-whole'})
        
        if title_elem and price_elem:
            rating_elem = first_result.find('span', {'class': 'a-icon-alt'})
            rating = rating_elem.text.split(' ')[0] if rating_elem else "N/A"
            review_elem = first_result.find('span', {'class': 'a-size-base s-underline-text'})
            if not review_elem:
                # Fallback for some layouts
                review_elem = first_result.find('span', {'class': 'a-size-base'})
            reviews = review_elem.text.strip() if review_elem else "N/A"

            return {
                "website": "Amazon",
                "product_name": title_elem.text.strip(),
                "price": clean_price(price_elem.text.strip()),
                "rating": rating,
                "reviews": reviews
            }
    except Exception as e:
        logger.error(f"Amazon scraping failed: {e}")
    
    return None

def scrape_flipkart(query):
    """Attempt to scrape Flipkart for the given query."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Flipkart changes selectors frequently
        # Titles are often in div class _4rR01T or similar
        title_elem = soup.find('div', {'class': '_4rR01T'}) 
        if not title_elem:
            title_elem = soup.find('a', {'class': 's1Q9rs'}) # Alternative selector

        price_elem = soup.find('div', {'class': '_30jeq3'})
        
        if title_elem and price_elem:
            rating_elem = soup.find('div', {'class': '_3LWZlK'})
            if not rating_elem:
                rating_elem = soup.find('div', {'class': 'XQDdHH'})
            rating = rating_elem.text.strip() if rating_elem else "N/A"
            
            review_elem = soup.find('span', {'class': '_2_R_DZ'})
            if not review_elem:
                review_elem = soup.find('span', {'class': 'Wphh3N'})
            reviews = review_elem.text.split('\xa0')[0].replace('Ratings', '').replace('&', '').strip() if review_elem else "N/A"

            return {
                "website": "Flipkart",
                "product_name": title_elem.text.strip() if title_elem.text else title_elem.get('title'),
                "price": clean_price(price_elem.text.strip()),
                "rating": rating,
                "reviews": reviews
            }
    except Exception as e:
        logger.error(f"Flipkart scraping failed: {e}")
        
    return None

def scrape_snapdeal(query):
    """Attempt to scrape Snapdeal for the given query."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }
    url = f"https://www.snapdeal.com/search?keyword={query.replace(' ', '+')}"
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        first_result = soup.find('div', {'class': 'product-tuple-listing'})
        if not first_result:
            return None
            
        title_elem = first_result.find('p', {'class': 'product-title'})
        price_elem = first_result.find('span', {'class': 'lfloat product-price'})
        rating_elem = first_result.find('div', {'class': 'filled-stars'})
        
        if title_elem and price_elem:
            rating = "N/A"
            if rating_elem and rating_elem.has_attr('style'):
                # width: 80% -> 4 stars
                style = rating_elem['style']
                if 'width' in style:
                    pct_str = style.split(':')[1].replace('%', '').strip()
                    try:
                        rating = str(round(float(pct_str) / 20, 1))
                    except:
                        pass
            
            review_elem = first_result.find('p', {'class': 'product-rating-count'})
            reviews = review_elem.text.replace('(', '').replace(')', '').strip() if review_elem else "N/A"

            return {
                "website": "Snapdeal",
                "product_name": title_elem.text.strip(),
                "price": clean_price(price_elem.text.strip()),
                "rating": rating,
                "reviews": reviews
            }
    except Exception as e:
        logger.error(f"Snapdeal scraping failed: {e}")
        
    return None

def get_mock_data(query):
    """Provide realistic mock data if scraping fails or is blocked."""
    query_lower = query.lower()
    
    # Try to find a match in our predefined mock data
    for key, data in MOCK_PRODUCTS.items():
        if key in query_lower or query_lower in key:
            results = []
            for item in data:
                # Add a small random variation to simulate live prices
                variation = random.uniform(-0.02, 0.02) # +/- 2%
                mock_price = item["price"] * (1 + variation)
                
                results.append({
                    "website": item["website"],
                    "product_name": key.title(),
                    "price": round(mock_price, 2),
                    "rating": item.get("rating", "4.0"),
                    "reviews": item.get("reviews", "1,000")
                })
            return results
            
    # Default fallback for unknown products
    base_price = random.randint(1000, 50000)
    return [
        {"website": "Amazon", "product_name": query.title(), "price": round(base_price * random.uniform(0.95, 1.05), 2), "rating": "4.2", "reviews": "500"},
        {"website": "Flipkart", "product_name": query.title(), "price": round(base_price * random.uniform(0.95, 1.05), 2), "rating": "4.3", "reviews": "600"},
        {"website": "Snapdeal", "product_name": query.title(), "price": round(base_price * random.uniform(0.95, 1.05), 2), "rating": "4.1", "reviews": "400"}
    ]

def simulate_email_alert(product_name, price, website):
    """Simulate sending an email alert for a price drop."""
    print("="*50)
    print("[EMAIL] EMAIL ALERT SIMULATION")
    print(f"To: user@example.com")
    print(f"Subject: Price Drop Alert: {product_name}")
    print(f"Good news! The price of {product_name} has dropped to Rs. {price} on {website}.")
    print("="*50)

def search_product(query):
    """
    Main function to search for a product.
    Tries actual scraping first, falls back to mock data if blocked/failed.
    """
    results = []
    
    # Attempt actual scraping (may be blocked by captcha)
    amazon_result = scrape_amazon(query)
    if amazon_result and amazon_result['price']:
        results.append(amazon_result)
        
    flipkart_result = scrape_flipkart(query)
    if flipkart_result and flipkart_result['price']:
        results.append(flipkart_result)
        
    snapdeal_result = scrape_snapdeal(query)
    if snapdeal_result and snapdeal_result['price']:
        results.append(snapdeal_result)
        
    # If we got no results (likely blocked), use mock data
    if not results:
        logger.info("Scraping returned no valid results (likely blocked). Using mock data fallback.")
        results = get_mock_data(query)
        
    return results
