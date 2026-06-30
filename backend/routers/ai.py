from fastapi import APIRouter, Depends
from pydantic import BaseModel

from dependencies import get_current_user
from services.vector_service import search_transactions
from services.gemini_service import model

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


def fallback_finance_answer(question, transactions):
    q = question.lower()

    total = sum(t.get("amount", 0) for t in transactions)

    by_category = {}
    by_merchant = {}

    for t in transactions:
        category = t.get("category", "Other")
        merchant = t.get("merchant", "Unknown")
        amount = t.get("amount", 0)

        by_category[category] = by_category.get(category, 0) + amount
        by_merchant[merchant] = by_merchant.get(merchant, 0) + amount

    if "food" in q or "restaurant" in q or "zomato" in q or "swiggy" in q:
        return f"You spent ₹{by_category.get('Food', 0)} on food-related transactions."

    if "shopping" in q or "amazon" in q:
        return f"You spent ₹{by_category.get('Shopping', 0)} on shopping-related transactions."

    if "transport" in q or "uber" in q:
        return f"You spent ₹{by_category.get('Transport', 0)} on transport-related transactions."

    if "highest" in q or "most" in q:
        if by_category:
            top_category = max(by_category, key=by_category.get)
            return f"Your highest spending category is {top_category} with ₹{by_category[top_category]}."

    return f"Based on the retrieved transactions, the total amount is ₹{total}."


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]

    results = search_transactions(request.question, user_id=user_id, top_k=5)

    if len(results) == 0:
        return {
            "answer": "No relevant transactions found for your account.",
            "retrieved_transactions": []
        }

    prompt = f"""
You are an AI financial advisor.

Use ONLY this user's retrieved transaction data to answer.

Transactions:
{results}

Question:
{request.question}

Give a short answer in Indian Rupees.
"""

    try:
        response = model.generate_content(prompt)

        return {
            "answer": response.text,
            "retrieved_transactions": results
        }

    except Exception:
        return {
            "answer": fallback_finance_answer(request.question, results),
            "retrieved_transactions": results,
            "note": "Gemini quota unavailable, used user-specific RAG fallback."
        }