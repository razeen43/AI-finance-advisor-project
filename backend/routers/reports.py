from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os

from database import transactions_col, budgets_col
from dependencies import get_current_user

router = APIRouter()


@router.get("/monthly")
async def generate_monthly_report(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]

    transactions = []
    budgets = []

    async for t in transactions_col.find({"user_id": user_id}):
        transactions.append(t)

    async for b in budgets_col.find({"user_id": user_id}):
        budgets.append(b)

    total_spent = sum(t.get("amount", 0) for t in transactions)

    by_category = {}
    anomalies = []

    for t in transactions:
        category = t.get("category", "Other")
        amount = t.get("amount", 0)

        by_category[category] = by_category.get(category, 0) + amount

        if t.get("is_anomaly") is True:
            anomalies.append(t)

    filename = f"monthly_report_{user_id}.pdf"
    filepath = os.path.join(os.getcwd(), filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    y = height - 50

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "AI Finance Advisor - Monthly Report")

    y -= 30
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Total Spending: Rs. {total_spent}")

    y -= 35
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Category Breakdown")

    c.setFont("Helvetica", 11)
    for category, amount in by_category.items():
        y -= 22
        c.drawString(70, y, f"{category}: Rs. {amount}")

    y -= 35
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Budget Status")

    c.setFont("Helvetica", 11)
    for b in budgets:
        category = b.get("category")
        limit = b.get("monthly_limit", 0)
        spent = by_category.get(category, 0)

        y -= 22
        status = "Over Budget" if spent > limit else "Within Budget"
        c.drawString(70, y, f"{category}: Rs. {spent} / Rs. {limit} - {status}")

    y -= 35
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "ML Anomaly Detection")

    c.setFont("Helvetica", 11)

    if not anomalies:
        y -= 22
        c.drawString(70, y, "No unusual transactions detected.")
    else:
        for a in anomalies[:5]:
            y -= 22
            c.drawString(
                70,
                y,
                f"{a.get('merchant')} - Rs. {a.get('amount')} - {a.get('category')}"
            )

    y -= 35
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "AI Recommendations")

    c.setFont("Helvetica", 11)

    if total_spent == 0:
        recs = ["Add transactions to generate personalized insights."]
    else:
        recs = [
            "Review categories where budgets are exceeded.",
            "Check unusual transactions detected by the ML model.",
            "Track spending weekly to avoid month-end overspending."
        ]

    for rec in recs:
        y -= 22
        c.drawString(70, y, f"- {rec}")

    c.save()

    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename="AI_Finance_Monthly_Report.pdf"
    )