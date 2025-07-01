import webbrowser
import urllib.parse

def search_amazon(product_name: str):
    """Open Amazon search page for the product."""
    if not product_name:
        print("No product specified for Amazon search.")
        return
    query = urllib.parse.quote_plus(product_name)
    url = f"https://www.amazon.com/s?k={query}"
    print(f"🔍 Searching Amazon for: {product_name}")
    webbrowser.open(url)
