from flask import Flask, render_template_string, request, jsonify
import random

app = Flask(__name__)

# --- Mock database ---
portfolio = {
    "balance": 10000.00,
    "holdings": []
}

# --- Mock market data ---
mock_stocks = {
    "AAPL": {"name": "Apple Inc.", "price": 180.25},
    "TSLA": {"name": "Tesla Inc.", "price": 240.50},
    "AMZN": {"name": "Amazon.com Inc.", "price": 135.10},
    "GOOG": {"name": "Alphabet Inc.", "price": 155.80}
}


# --- HTML template (index.html replacement) ---
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Investment Portfolio</title>
    <style>
        body { font-family: Arial; background: #f6f8fa; padding: 20px; }
        h1 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; border-bottom: 1px solid #ddd; text-align: left; }
        button { background: #007bff; color: white; padding: 8px 14px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .balance { margin-top: 10px; font-size: 18px; }
    </style>
</head>
<body>
    <h1>📈 My Investment Portfolio</h1>
    <div class="balance">Available Balance: $<span id="balance">{{ balance }}</span></div>

    <h2>Available Stocks</h2>
    <table>
        <tr><th>Symbol</th><th>Name</th><th>Current Price</th><th>Action</th></tr>
        {% for symbol, info in stocks.items() %}
        <tr>
            <td>{{ symbol }}</td>
            <td>{{ info.name }}</td>
            <td>$<span id="{{ symbol }}-price">{{ info.price }}</span></td>
            <td><button onclick="buyStock('{{ symbol }}')">Buy</button></td>
        </tr>
        {% endfor %}
    </table>

    <h2>Your Holdings</h2>
    <table id="holdingsTable">
        <tr><th>Symbol</th><th>Shares</th><th>Value</th></tr>
        {% for h in holdings %}
        <tr>
            <td>{{ h.symbol }}</td>
            <td>{{ h.shares }}</td>
            <td>${{ "%.2f"|format(h.value) }}</td>
        </tr>
        {% endfor %}
    </table>

    <script>
        async function buyStock(symbol) {
            const res = await fetch('/buy', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({symbol})
            });
            const data = await res.json();
            alert(data.message);
            location.reload();
        }

        // Simulate live price updates
        setInterval(async () => {
            const res = await fetch('/prices');
            const prices = await res.json();
            for (const [symbol, price] of Object.entries(prices)) {
                document.getElementById(symbol + '-price').innerText = price.toFixed(2);
            }
        }, 5000);
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(html_template,
                                  balance=portfolio["balance"],
                                  stocks=mock_stocks,
                                  holdings=portfolio["holdings"])


@app.route('/buy', methods=['POST'])
def buy_stock():
    data = request.get_json()
    symbol = data.get("symbol")
    if symbol not in mock_stocks:
        return jsonify({"message": "Invalid stock symbol."}), 400

    price = mock_stocks[symbol]["price"]
    if portfolio["balance"] < price:
        return jsonify({"message": "Not enough balance."}), 400

    portfolio["balance"] -= price
    # Check if already owned
    for h in portfolio["holdings"]:
        if h["symbol"] == symbol:
            h["shares"] += 1
            h["value"] = h["shares"] * price
            break
    else:
        portfolio["holdings"].append({"symbol": symbol, "shares": 1, "value": price})

    return jsonify({"message": f"Bought 1 share of {symbol} for ${price:.2f}"})


@app.route('/prices')
def get_prices():
    # Randomize prices slightly to simulate live updates
    for s in mock_stocks.values():
        s["price"] += random.uniform(-1, 1)
        s["price"] = round(max(s["price"], 1), 2)
    return jsonify({k: v["price"] for k, v in mock_stocks.items()})


if __name__ == '__main__':
    app.run(debug=True)