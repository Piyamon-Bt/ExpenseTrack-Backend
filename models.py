from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from database import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    color = Column(String)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    created_at = Column(Date)
    description = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"))
