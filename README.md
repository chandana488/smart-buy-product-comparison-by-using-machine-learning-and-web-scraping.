# smart-buy product price comparison by using machine learning and web-scraping.
A Flask-based web application that helps users compare product prices across multiple e-commerce websites. The system scrapes product prices, stores historical data in a database, and displays price trends using interactive charts.

# Features
Search products from multiple online shopping websites
Compare prices instantly
Find the best available deal automatically
Store product price history in a database
Display historical price trends using Chart.js
Simulated email alerts for best deals
REST API support using Flask routes

# Technologies Used
Python
Flask
HTML, CSS, JavaScript
SQLite Database
Chart.js
Web Scraping

# Project Workflow
User enters a product name in the search bar
Flask backend receives the request
Scraper module collects product prices from different websites
Data is stored in the database
Best deal is identified and displayed
Historical price data is shown in graph format
Main Functionalities
/

Displays the homepage of the application.

/search
Accepts product search queries
Fetches product prices from multiple websites
Saves price data into the database
Returns the best deal and product list
/data
Retrieves historical product price data
Formats data for Chart.js visualization
Displays price trends for each website

# Advantages
Saves time while comparing prices
Helps users find the lowest product price
Tracks price changes over time
Easy-to-use interface
Useful for online shoppers

# How to Run the Project
Install Required Packages
pip install flask
Run the Application
python app.py
Open in Browser
http://127.0.0.1:5000
