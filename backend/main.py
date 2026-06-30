from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import db, transactions_col
from routers import auth, transactions, ai, budgets, insights,health_score,reports
from services.vector_service import add_transaction_to_index, clear_index

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(ai.router, prefix="/ai", tags=["AI Advisor"])
app.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])
app.include_router(insights.router, prefix="/insights", tags=["AI Insights"])
app.include_router(health_score.router, prefix="/health-score", tags=["Financial Health Score"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])

@app.on_event("startup")
async def load_transactions_into_faiss():
    clear_index()

    cursor = transactions_col.find()

    async for transaction in cursor:
        transaction["_id"] = str(transaction["_id"])
        add_transaction_to_index(transaction)

    print("FAISS index loaded from MongoDB")


@app.get("/")
async def root():
    return {"message": "AI Finance Advisor API Running"}


@app.get("/test-db")
async def test_db():
    collections = await db.list_collection_names()
    return {
        "status": "MongoDB Connected",
        "collections": collections
    }