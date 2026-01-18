from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pymongo

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        searchString = request.form["content"]

        # MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["crawlerDB"]
        collection = db[searchString]
        collection.delete_many({})

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        try:
            driver.get(f"https://www.flipkart.com/search?q={searchString}")
            time.sleep(3)

            # Click first product
            product = driver.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
            product.click()
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(4)

            # Scroll to reviews
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            reviews = []
            review_elements = driver.find_elements(By.CSS_SELECTOR, "div._27M-vq")[:5]

            for r in review_elements:
                try:
                    rating = r.find_element(By.CSS_SELECTOR, "div._3LWZlK").text
                except:
                    rating = "No Rating"

                try:
                    comment = r.find_element(By.CSS_SELECTOR, "div.t-ZTKy").text
                except:
                    comment = "No Comment"

                review = {
                    "Product": searchString,
                    "Name": "Anonymous",
                    "Rating": rating,
                    "CommentHead": "Review",
                    "Comment": comment
                }

                collection.insert_one(review)
                reviews.append(review)

            return render_template("results.html", reviews=reviews)

        finally:
            driver.quit()

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001, use_reloader=False)
