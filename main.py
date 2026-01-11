from fastapi import FastAPI
from supabase import create_client
from dotenv import load_dotenv
import os
from schemas import ExpenseUpdate, ExpenseCreate, CategoryCreate
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# ================== CORS ==================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://expense-track-frontend-ten.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== Supabase ==================
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

# ================== Root ==================
@app.get("/")
def root():
    return {"status": "Expense Tracker API is running"}

# ================== Expense CRUD ==================
@app.post("/expenses")
def create_expense(expense: ExpenseCreate):
    data = {
        "amount": float(expense.amount),
        "category_id": expense.category_id,
        "description": expense.description
    }
    res = supabase.table("Expense").insert(data).execute()
    return res.data


@app.get("/expenses")
def get_expenses():
    res = supabase.table("Expense").select("*").order("created_at", desc=True).execute()
    return res.data


@app.get("/expenses/{expense_id}")
def get_expense(expense_id: int):
    res = (
        supabase
        .table("Expense")
        .select("*")
        .eq("id", expense_id)
        .execute()
    )
    return res.data


@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: ExpenseUpdate):
    data = expense.dict(exclude_unset=True)
    res = (
        supabase
        .table("Expense")
        .update(data)
        .eq("id", expense_id)
        .execute()
    )
    return res.data


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    supabase.table("Expense").delete().eq("id", expense_id).execute()
    return {"deleted": expense_id}

# ================== Filter ==================
@app.get("/expenses/filter")
def filter_expenses(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category_id: Optional[int] = None
):
    query = supabase.table("Expense").select("*")

    if start_date:
        query = query.gte("created_at", start_date)

    if end_date:
        end = datetime.fromisoformat(end_date) + timedelta(days=1)
        query = query.lt("created_at", end.isoformat())

    if category_id:
        query = query.eq("category_id", category_id)

    res = query.order("created_at", desc=True).execute()
    return res.data

# ================== Dashboard ==================
@app.get("/dashboard/total")
def dashboard_total():
    res = supabase.table("Expense").select("amount").execute()
    total = sum(item["amount"] for item in res.data)
    return {"total": total}


@app.get("/dashboard/by-category")
def dashboard_by_category():
    res = (
        supabase
        .table("Expense")
        .select("amount, Category(name)")
        .execute()
    )

    summary = {}
    for item in res.data:
        name = item["Category"]["name"]
        summary[name] = summary.get(name, 0) + item["amount"]

    return summary


@app.get("/dashboard/by-date")
def dashboard_by_date():
    res = supabase.table("Expense").select("amount, created_at").execute()

    summary = {}
    for item in res.data:
        date = item["created_at"][:10]
        summary[date] = summary.get(date, 0) + item["amount"]

    return summary

# =====================================================
# 🔥 CHART API (สำหรับกราฟ)
# =====================================================

# ---------- Daily Chart ----------
@app.get("/dashboard/chart/daily")
def chart_daily(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category_id: Optional[int] = None
):
    query = supabase.table("Expense").select("amount, created_at")

    if start_date:
        query = query.gte("created_at", start_date)

    if end_date:
        end = datetime.fromisoformat(end_date) + timedelta(days=1)
        query = query.lt("created_at", end.isoformat())

    if category_id:
        query = query.eq("category_id", category_id)

    res = query.execute()

    summary = defaultdict(float)
    for item in res.data:
        date = item["created_at"][:10]
        summary[date] += item["amount"]

    return [
        {"date": date, "total": total}
        for date, total in sorted(summary.items())
    ]


# ---------- Monthly Chart ----------
@app.get("/dashboard/chart/monthly")
def chart_monthly(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category_id: Optional[int] = None
):
    query = supabase.table("Expense").select("amount, created_at")

    if start_date:
        query = query.gte("created_at", start_date)

    if end_date:
        end = datetime.fromisoformat(end_date) + timedelta(days=1)
        query = query.lt("created_at", end.isoformat())

    if category_id:
        query = query.eq("category_id", category_id)

    res = query.execute()

    summary = defaultdict(float)
    for item in res.data:
        month = item["created_at"][:7]
        summary[month] += item["amount"]

    return [
        {"month": month, "total": total}
        for month, total in sorted(summary.items())
    ]


# ---------- Pie Chart (Category) ----------
@app.get("/dashboard/chart/by-category")
def chart_by_category(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    query = supabase.table("Expense").select("amount, Category(name)")

    if start_date:
        query = query.gte("created_at", start_date)

    if end_date:
        end = datetime.fromisoformat(end_date) + timedelta(days=1)
        query = query.lt("created_at", end.isoformat())

    res = query.execute()

    summary = defaultdict(float)
    for item in res.data:
        name = item["Category"]["name"]
        summary[name] += item["amount"]

    return [
        {"category": name, "total": total}
        for name, total in summary.items()
    ]

# ================== Category ==================
@app.get("/categories")
def get_categories():
    res = supabase.table("Category").select("*").execute()
    return res.data


@app.post("/categories")
def create_category(category: CategoryCreate):
    res = supabase.table("Category").insert({
        "name": category.name.strip().lower(),
        "color": category.color
    }).execute()
    return res.data
