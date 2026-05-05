from flask import Flask, render_template, request, jsonify
import database
import scraper
from datetime import datetime

app = Flask(__name__)

# Initialize the database
with app.app_context():
    database.init_db()

@app.route('/')
def index():
    """Render the main homepage."""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Handle product search and scraping."""
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
        
    # Search and scrape prices
    results = scraper.search_product(query)
    
    if not results:
        return jsonify({"error": "Could not fetch data for this product"}), 404
        
    # Find the best deal
    best_deal = None
    lowest_price = float('inf')
    
    for item in results:
        price = item.get('price')
        if price and price < lowest_price:
            lowest_price = price
            best_deal = item
            
        # Save each valid result to the database
        if price:
            database.save_product(item['product_name'], item['website'], price)
            
    # Simulate an email alert for the best deal (optional feature)
    if best_deal:
        scraper.simulate_email_alert(best_deal['product_name'], best_deal['price'], best_deal['website'])
    
    return jsonify({
        "results": results,
        "best_deal": best_deal
    })

@app.route('/data')
def get_data():
    """Return historical price data for the chart."""
    query = request.args.get('query')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
        
    history = database.get_product_history(query)
    
    # Group data by website for Chart.js
    datasets_dict = {}
    labels = set()
    
    for row in history:
        website = row['website']
        ts = row['timestamp'] 
        labels.add(ts)
        
        if website not in datasets_dict:
            datasets_dict[website] = []
            
        datasets_dict[website].append({
            "x": ts,
            "y": row['price']
        })
        
    # Sort labels chronologically based on raw string "YYYY-MM-DD HH:MM:SS"
    sorted_original_labels = sorted(list(labels))
    
    def format_ts(ts_str):
        try:
            dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%H:%M - %d/%m")
        except:
            return ts_str
            
    sorted_labels = [format_ts(l) for l in sorted_original_labels]
    
    # Prepare final datasets
    datasets = []
    # Colors for different websites
    colors = {
        "Amazon": "#FF9900",
        "Flipkart": "#2874F0",
        "Snapdeal": "#E40046",
        "Reliance Digital": "#E21B22",
        "Samsung Store": "#1428A0",
        "Croma": "#00E676"
    }
    
    for website, data_points in datasets_dict.items():
        formatted_data_points = []
        for pt in data_points:
            formatted_data_points.append({
                "x": format_ts(pt["x"]),
                "y": pt["y"]
            })
            
        datasets.append({
            "label": website,
            "data": formatted_data_points,
            "borderColor": colors.get(website, "#" + "".join([str(hex(hash(website) % 16))[2:] for _ in range(6)])[:6]), # Fallback random color
            "fill": False,
            "tension": 0.1
        })

    return jsonify({
        "labels": sorted_labels,
        "datasets": datasets
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
