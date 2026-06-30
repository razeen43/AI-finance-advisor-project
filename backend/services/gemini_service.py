import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")


def categorize_transaction(text: str) -> str:
    prompt = f"""
    Categorize this bank transaction into only one category:
    Food, Transport, Shopping, Entertainment, Utilities, Health, Education, Income, Other.

    Transaction: {text}

    Return only the category name.
    """

    try:
        response = model.generate_content(prompt)
        category = response.text.strip()

        allowed = [
            "Food", "Transport", "Shopping", "Entertainment",
            "Utilities", "Health", "Education", "Income", "Other"
        ]

        if category in allowed:
            return category

        return "Other"

    except Exception:
        return "Other"