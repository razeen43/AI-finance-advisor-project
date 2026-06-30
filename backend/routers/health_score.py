from fastapi import APIRouter, Depends
from database import transactions_col, budgets_col
from dependencies import get_current_user

router = APIRouter()


@router.get("/")
async def get_financial_health_score(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]

    transactions = []
    budgets = []

    async for t in transactions_col.find({"user_id": user_id}):
        transactions.append(t)

    async for b in budgets_col.find({"user_id": user_id}):
        budgets.append(b)

    total_spent = sum(t.get("amount", 0) for t in transactions)
    anomaly_count = len([t for t in transactions if t.get("is_anomaly") is True])

    score = 100
    reasons = []

    if anomaly_count > 0:
        deduction = min(anomaly_count * 10, 30)
        score -= deduction
        reasons.append(f"{anomaly_count} unusual transactions detected.")

    by_category = {}

    for t in transactions:
        category = t.get("category", "Other")
        by_category[category] = by_category.get(category, 0) + t.get("amount", 0)

    over_budget_count = 0

    for b in budgets:
        category = b.get("category")
        limit = b.get("monthly_limit", 0)
        spent = by_category.get(category, 0)

        if limit > 0 and spent > limit:
            over_budget_count += 1
            over_by = spent - limit
            score -= 20
            reasons.append(f"{category} budget exceeded by ₹{over_by}.")

    if total_spent > 30000:
        score -= 10
        reasons.append("Overall spending is high.")

    score = max(score, 0)

    if score >= 85:
        status = "Excellent"
    elif score >= 70:
        status = "Good"
    elif score >= 50:
        status = "Needs Attention"
    else:
        status = "Poor"

    recommendations = []

    if over_budget_count > 0:
        recommendations.append("Reduce spending in categories where budget is exceeded.")

    if anomaly_count > 0:
        recommendations.append("Review unusual transactions carefully.")

    if total_spent == 0:
        recommendations.append("Add transactions to calculate your financial health score.")

    if not recommendations:
        recommendations.append("Your financial behavior looks stable. Keep tracking regularly.")

    return {
        "score": score,
        "status": status,
        "total_spent": total_spent,
        "anomaly_count": anomaly_count,
        "over_budget_count": over_budget_count,
        "reasons": reasons,
        "recommendations": recommendations
    }