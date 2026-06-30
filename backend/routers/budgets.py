from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
from database import budgets_col, transactions_col
from dependencies import get_current_user

router = APIRouter()


class BudgetCreate(BaseModel):
    category: str
    monthly_limit: float


@router.post("/")
async def create_budget(
    budget: BudgetCreate,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]

    existing = await budgets_col.find_one({
        "user_id": user_id,
        "category": budget.category
    })

    if existing:
        await budgets_col.update_one(
            {
                "user_id": user_id,
                "category": budget.category
            },
            {
                "$set": {
                    "monthly_limit": budget.monthly_limit
                }
            }
        )

        return {"message": "Budget updated successfully"}

    new_budget = {
        "user_id": user_id,
        "category": budget.category,
        "monthly_limit": budget.monthly_limit,
        "created_at": datetime.utcnow()
    }

    await budgets_col.insert_one(new_budget)

    return {"message": "Budget created successfully"}


@router.get("/")
async def get_budgets(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    budgets = []

    cursor = budgets_col.find({"user_id": user_id})

    async for budget in cursor:
        category = budget["category"]
        monthly_limit = budget["monthly_limit"]

        transactions_cursor = transactions_col.find({
            "user_id": user_id,
            "category": category
        })

        current_spend = 0

        async for t in transactions_cursor:
            current_spend += t.get("amount", 0)

        budget["_id"] = str(budget["_id"])
        budget["current_spend"] = current_spend
        budget["remaining"] = monthly_limit - current_spend

        if monthly_limit > 0:
            budget["percent_used"] = round((current_spend / monthly_limit) * 100, 2)
        else:
            budget["percent_used"] = 0

        budgets.append(budget)

    return budgets


@router.get("/alerts")
async def get_budget_alerts(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    alerts = []

    cursor = budgets_col.find({"user_id": user_id})

    async for budget in cursor:
        category = budget["category"]
        monthly_limit = budget["monthly_limit"]

        transactions_cursor = transactions_col.find({
            "user_id": user_id,
            "category": category
        })

        current_spend = 0

        async for t in transactions_cursor:
            current_spend += t.get("amount", 0)

        if current_spend > monthly_limit:
            alerts.append({
                "category": category,
                "monthly_limit": monthly_limit,
                "current_spend": current_spend,
                "over_by": current_spend - monthly_limit,
                "message": f"You exceeded your {category} budget by ₹{current_spend - monthly_limit}."
            })

    return alerts