from fastapi import APIRouter, UploadFile, File, Depends
from pydantic import BaseModel
from datetime import datetime
from database import transactions_col
from dependencies import get_current_user
from services.vector_service import add_transaction_to_index
from services.gemini_service import categorize_transaction
from services.anomaly_service import detect_anomaly_ml
from services.prediction_service import predict_next_spend

import pandas as pd
from io import StringIO

router = APIRouter()


class TransactionCreate(BaseModel):
    merchant: str
    amount: float
    category: str
    date: str | None = None


def parse_transaction_date(date_value):
    if not date_value:
        return datetime.utcnow()

    try:
        return datetime.strptime(str(date_value), "%Y-%m-%d")
    except Exception:
        return datetime.utcnow()


async def get_category_amounts(category: str, user_id: str):
    amounts = []

    cursor = transactions_col.find({
        "category": category,
        "user_id": user_id
    })

    async for transaction in cursor:
        amounts.append(transaction.get("amount", 0))

    return amounts


@router.post("/")
async def add_transaction(
    transaction: TransactionCreate,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]

    historical_amounts = await get_category_amounts(transaction.category, user_id)

    is_anomaly, anomaly_reason = detect_anomaly_ml(
        transaction.amount,
        transaction.category,
        historical_amounts
    )

    transaction_date = parse_transaction_date(transaction.date)

    new_transaction = {
        "user_id": user_id,
        "merchant": transaction.merchant,
        "amount": transaction.amount,
        "category": transaction.category,
        "date": transaction_date,
        "is_anomaly": is_anomaly,
        "anomaly_reason": anomaly_reason,
        "created_at": datetime.utcnow()
    }

    result = await transactions_col.insert_one(new_transaction)

    new_transaction["_id"] = str(result.inserted_id)
    add_transaction_to_index(new_transaction)

    return {
        "message": "Transaction added successfully",
        "id": str(result.inserted_id),
        "is_anomaly": is_anomaly,
        "anomaly_reason": anomaly_reason
    }


@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]

    contents = await file.read()
    csv_text = contents.decode("utf-8")

    df = pd.read_csv(StringIO(csv_text))

    saved_count = 0

    for _, row in df.iterrows():
        merchant = str(row.get("description", row.get("merchant", "Unknown")))
        debit = float(row.get("debit", 0) or 0)

        if debit <= 0:
            continue

        category = categorize_transaction(merchant)
        historical_amounts = await get_category_amounts(category, user_id)

        is_anomaly, anomaly_reason = detect_anomaly_ml(
            debit,
            category,
            historical_amounts
        )

        transaction_date = parse_transaction_date(row.get("date"))

        transaction = {
            "user_id": user_id,
            "merchant": merchant,
            "amount": debit,
            "category": category,
            "date": transaction_date,
            "is_anomaly": is_anomaly,
            "anomaly_reason": anomaly_reason,
            "created_at": datetime.utcnow()
        }

        result = await transactions_col.insert_one(transaction)

        transaction["_id"] = str(result.inserted_id)
        add_transaction_to_index(transaction)

        saved_count += 1

    return {
        "message": "CSV uploaded successfully",
        "saved_transactions": saved_count
    }


@router.get("/")
async def get_transactions(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    transactions = []

    cursor = transactions_col.find({"user_id": user_id}).sort("date", -1)

    async for transaction in cursor:
        transaction["_id"] = str(transaction["_id"])
        transactions.append(transaction)

    return transactions


@router.get("/summary")
async def transaction_summary(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]

    transactions = []

    cursor = transactions_col.find({"user_id": user_id})

    async for transaction in cursor:
        transactions.append(transaction)

    total_spent = sum(t.get("amount", 0) for t in transactions)

    by_category = {}

    for t in transactions:
        category = t.get("category", "Other")
        by_category[category] = by_category.get(category, 0) + t.get("amount", 0)

    anomalies = [t for t in transactions if t.get("is_anomaly") is True]

    return {
        "total_spent": total_spent,
        "by_category": by_category,
        "count": len(transactions),
        "anomalies_count": len(anomalies)
    }


@router.get("/anomalies")
async def get_anomalies(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    anomalies = []

    cursor = transactions_col.find({
        "user_id": user_id,
        "is_anomaly": True
    }).sort("date", -1)

    async for transaction in cursor:
        transaction["_id"] = str(transaction["_id"])
        anomalies.append(transaction)

    return anomalies


@router.get("/predict")
async def predict_spending(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]

    transactions = []

    cursor = transactions_col.find({"user_id": user_id})

    async for transaction in cursor:
        transactions.append(transaction)

    by_category = {}

    for t in transactions:
        category = t.get("category", "Other")
        amount = t.get("amount", 0)

        date = t.get("date") or t.get("created_at")

        if date is None:
            continue

        month_key = f"{date.year}-{date.month:02d}"

        if category not in by_category:
            by_category[category] = {}

        by_category[category][month_key] = (
            by_category[category].get(month_key, 0) + amount
        )

    predictions = {}

    for category, monthly_data in by_category.items():
        monthly_amounts = [
            monthly_data[month]
            for month in sorted(monthly_data.keys())
        ]

        prediction = predict_next_spend(monthly_amounts)

        if prediction is not None:
            predictions[category] = prediction

    return {
        "message": "Predicted spending for next month",
        "predictions": predictions
    }