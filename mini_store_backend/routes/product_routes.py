# routes/product_routes.py
from fastapi import APIRouter, Query
from db import db

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/")
async def get_products(q: str = None, category: str = None, min_price: float = 0, max_price: float = 999999):
    query = {}
    if q:
        query["name"] = {"$regex": q, "$options": "i"}
    if category:
        query["category"] = category
    query["price"] = {"$gte": min_price, "$lte": max_price}
    products = await db.products.find(query).to_list(200)
    return products

@router.get("/{id}")
async def get_product(id: str):
    product = await db.products.find_one({"_id": id})
    if not product:
        return {"error": "Product not found"}
    return product
