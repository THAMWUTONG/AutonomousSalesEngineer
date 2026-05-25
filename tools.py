from tavily import TavilyClient
import os
from google import genai
from dotenv import load_dotenv
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def searchProducts(query: str, budgetRM: float = None) -> str:
    """Search for relevant products online and return structured results."""
    searchQuery = f"{query} price buy online Malaysia RM"

    if budgetRM:
        searchQuery += f" under RM{budgetRM}"

    results = tavily.search(
        query=searchQuery,
        search_depth="advanced",
        max_results=5,
        include_answer=True
    )

    formatted = []
    for r in results["results"]:
        formatted.append(f"""
Product Source: {r['title']}
URL: {r['url']}
Details: {r['content'][:300]}
        """)

    return "\n---\n".join(formatted)


def calculateTotal(items: list, location: str = "Kuala Lumpur") -> dict:
    """Calculate total cost including shipping and tax."""
    subtotal = sum(item["priceRM"] for item in items)

    shippingRules = {
        "Kuala Lumpur": 0,
        "Selangor": 15,
        "Penang": 25,
        "Johor": 25,
        "Sabah": 60,
        "Sarawak": 60,
    }

    shipping = shippingRules.get(location, 30)
    tax = round(subtotal * 0.06, 2)
    total = subtotal + shipping + tax

    return {
        "items": items,
        "subtotalRM": subtotal,
        "shippingRM": shipping,
        "taxRM": tax,
        "totalRM": round(total, 2),
        "location": location,
    }


def checkCompatibility(items: list, requirements: str) -> str:
    """Use Gemini to verify items match predefined requirements."""
    from agent import callGeminiWithRetry

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    items_text = "\n".join([
        f"- {i['name']}: {i.get('specs', 'no specs')}" for i in items
    ])

    response = callGeminiWithRetry(
        client=client,
        model="gemini-3.1-flash-lite",
        contents=f"""You are a furniture and tech compatibility checker.

User requirements: {requirements}

Proposed items:
{items_text}

Check:
1. Do all items physically fit together? (e.g., desk size vs room size)
2. Are there any missing items? (e.g., chair but no desk)
3. Any style or aesthetic mismatches?

Respond in this exact JSON format only, no extra text:
{{"compatible": true, "issues": ["issue1"], "missing": ["item1"], "verdict": "one sentence summary"}}"""
    )

    return response.text


# Quick test — run: python tools.py
if __name__ == "__main__":
    print("Testing search_products...")
    print(searchProducts("ergonomic office chair", budgetRM=500))