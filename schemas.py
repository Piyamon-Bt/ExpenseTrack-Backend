from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class ExpenseCreate(BaseModel):
    amount: Decimal
    category_id: int
    description: str | None = None

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    category_id: Optional[int] = None
    description: Optional[str] = None

class CategoryCreate(BaseModel):
    name: str
    color: str
