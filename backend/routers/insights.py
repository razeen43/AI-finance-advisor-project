from fastapi import APIRouter, Depends
from database import transactions_col, budgets_col
from dependencies import get_current_user

router = APIRouter()


@router.get("/")
async def get_financial_insights(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]

    transactions = []
    budgets = []

    transaction_cursor = transactions_col.find({"user_id": user_id})
    async for t in transaction_cursor:
        transactions.append(t)

    budget_cursor = budgets_col.find({"user_id": user_id})
    async for b in budget_cursor:
        budgets.append(b)

    total_spent = sum(t.get("amount", 0) for t in transactions)

    by_category = {}
    by_merchant = {}

    for t in transactions:
        category = t.get("category", "Other")
        merchant = t.get("merchant", "Unknown")
        amount = t.get("amount", 0)

        by_category[category] = by_category.get(category, 0) + amount
        by_merchant[merchant] = by_merchant.get(merchant, 0) + amount

    top_category = max(by_category, key=by_category.get) if by_category else None
    top_merchant = max(by_merchant, key=by_merchant.get) if by_merchant else None

    anomalies = [
        {
            "merchant": t.get("merchant"),
            "amount": t.get("amount"),
            "category": t.get("category"),
            "reason": t.get("anomaly_reason")
        }
        for t in transactions
        if t.get("is_anomaly") is True
    ]

    budget_alerts = []

    for b in budgets:
        category = b.get("category")
        limit = b.get("monthly_limit", 0)
        spent = by_category.get(category, 0)

        percent_used = round((spent / limit) * 100, 2) if limit > 0 else 0

        if spent > limit:
            budget_alerts.append({
                "category": category,
                "limit": limit,
                "spent": spent,
                "over_by": spent - limit,
                "percent_used": percent_used
            })

    recommendations = []

    if top_category:
        recommendations.append(
            f"Your highest spending category is {top_category} with ₹{by_category[top_category]}."
        )

    if budget_alerts:
        for alert in budget_alerts:
            recommendations.append(
                f"You exceeded your {alert['category']} budget by ₹{alert['over_by']}. Try reducing this category next month."
            )

    if anomalies:
        recommendations.append(
            f"{len(anomalies)} unusual transactions were detected. Review them to avoid unnecessary spending."
        )

    if total_spent == 0:
        recommendations.append("Add transactions to generate financial insights.")
    elif not recommendations:
        recommendations.append("Your spending looks stable. Continue tracking regularly.")

    return {
        "total_spent": total_spent,
        "top_category": {
            "name": top_category or "None",
            "amount": by_category.get(top_category, 0) if top_category else 0
        },
        "top_merchant": {
            "name": top_merchant or "None",
            "amount": by_merchant.get(top_merchant, 0) if top_merchant else 0
        },
        "category_breakdown": by_category,
        "budget_alerts": budget_alerts,
        "anomalies": anomalies,
        "recommendations": recommendations
    }