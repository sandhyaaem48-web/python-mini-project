import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

def scrape_books(pages=1, limit=5):
    data = []

    for page in range(1, pages + 1):
        url = f"https://books.toscrape.com/catalogue/page-{page}.html"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        ol = soup.find("ol", class_="row")
        if not ol:
            continue

        articles = ol.find_all("article", class_="product_pod")

        for article in articles:
            title = article.h3.a["title"]

            price_tag = article.find("p", class_="price_color")
            price = price_tag.text if price_tag else "N/A"

            rating_tag = article.find("p", class_="star-rating")
            rating = rating_tag["class"][1] if rating_tag else "N/A"

            data.append({
                "title": title,
                "price": price,
                "rating": rating
            })

            if len(data) == limit:
                return data

    return data


@app.route("/", methods=["GET"])
def index():
    books = scrape_books(pages=2, limit=5)
    return jsonify(books)


if __name__ == "__main__":
    app.run(debug=True, port=5001, use_reloader=False)
