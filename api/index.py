from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder="../templates")

# Web scraping function
def scrape_prices(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception:
        return []
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'id': 'customers'})
    items = []
    if table:
        for row in table.find_all('tr')[1:]:
            cols = row.find_all(['th', 'td'])
            if len(cols) >= 5:
                items.append({
                    'name': cols[0].text.strip(),
                    'unit': cols[1].text.strip(),
                    'marketPrice': cols[2].text.strip(),
                    'retailPriceRange': cols[3].text.strip(),
                    'mallPriceRange': cols[4].text.strip()
                })
    return items

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "").lower()
    
    if "fruit" in user_message and "price" in user_message:
        prices = scrape_prices('https://market.todaypricerates.com/Andhra-Pradesh-fruits-price')
        if prices:
            reply = "🍎 **Fruit Prices Today**:\n" + "\n".join([f"{item['name']} - {item['marketPrice']} ({item['unit']})" for item in prices])
        else:
            reply = "❌ Couldn't fetch fruit prices right now."
        return jsonify({"reply": reply})
    
    if "vegetable" in user_message and "price" in user_message:
        prices = scrape_prices('https://market.todaypricerates.com/Andhra-Pradesh-vegetables-price')
        if prices:
            reply = "🥕 **Vegetable Prices Today**:\n" + "\n".join([f"{item['name']} - {item['marketPrice']} ({item['unit']})" for item in prices])
        else:
            reply = "❌ Couldn't fetch vegetable prices right now."
        return jsonify({"reply": reply})
    
    # Search for individual fruit/vegetable
    all_prices = scrape_prices('https://market.todaypricerates.com/Andhra-Pradesh-fruits-price') + scrape_prices('https://market.todaypricerates.com/Andhra-Pradesh-vegetables-price')
    match = next((item for item in all_prices if item['name'].lower() in user_message), None)
    if match:
        emoji = "🍎" if match['name'].lower() in [p['name'].lower() for p in scrape_prices('https://market.todaypricerates.com/Andhra-Pradesh-fruits-price')] else "🥕"
        return jsonify({"reply": f"{emoji} The price of {match['name']} is {match['marketPrice']} ({match['unit']})."})
    
    return jsonify({"reply": "🤖 I can help with fruit 🍎 and vegetable 🥕 prices. Try asking 'price of tomato' or 'fruit prices'."})

if __name__ == "__main__":
    app.run(debug=True)
