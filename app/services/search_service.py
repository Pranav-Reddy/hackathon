import requests
from vertexai.generative_models import GenerativeModel

SERP_API_KEY = "4c0acee73671a7108789793ca05c906a6cc215974d137a27257bbe31d26e2b14"  # use env var or config
def search_product_links(product_name, serpapi_key):
    import requests
    import vertexai

    # Initialize Vertex AI (if not already initialized)
    vertexai.init(project="hackathon-470421", location="us-east1")
    model = GenerativeModel("gemini-1.5-flash")

    # Search shopping links using SerpAPI
    params = {
        "engine": "google",
        "q": product_name,
        "tbm": "shop",
        "api_key": serpapi_key
    }
    resp = requests.get("https://serpapi.com/search", params=params).json()
    shopping_results = resp.get("shopping_results", [])

    results = []
    for item in shopping_results:
        title = item.get("title")
        price = item.get("price")
        link = item.get("product_link") or ""
        source = item.get("source")

        # Skip if no link
        if not link:
            continue

        # Ask Gemini to score the link
        prompt = f"""
Rate the trustworthiness of this shopping link from 1 to 10 (where 10 is most trustworthy).
Link: {link}
Title: {title}
Source: {source}
Return only the number as response.
"""
        try:
            gemini_response = model.generate_content(prompt)
            score_str = gemini_response.text.strip()
            score = int(score_str) if score_str.isdigit() else None
        except Exception:
            score = None

        results.append({
            "title": title,
            "price": price,
            "link": link,
            "source": source,
            "trust_score": score
        })

    return results
