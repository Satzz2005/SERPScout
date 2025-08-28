from flask import Flask, render_template, request
from .seo3 import HybridSEOSystem
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file

app = Flask(__name__)
hybrid_seo = HybridSEOSystem()

@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    error = None

    if request.method == 'POST':
        keyword = request.form.get('keywords', '').strip()
        if not os.getenv("SERPAPI_KEY"):
            error = "API key is missing! Please add SERPAPI_KEY in your .env file."
        elif keyword:
            results = hybrid_seo.search_webpages(keyword)
            if not results:
                error = "No results found or API quota reached."
        else:
            error = "Please enter a keyword to search."

    return render_template('index.html', results=results, error=error)

if __name__ == '__main__':
    app.run(debug=True)
