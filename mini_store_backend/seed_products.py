# seed_products.py
import asyncio
from db import db

sample_products = [
    {"_id":"p_apple", "name":"Organic Apple", "brand":"LocalFarm", "category":"produce", "tags":["apple","fruit","organic"], "price":50, "stock":100, "seasonMonths":[9,10,11], "substitutes":["p_pear"], "imageUrl":""},
    {"_id":"p_milk", "name":"Full Cream Milk 1L", "brand":"DairyPure", "category":"dairy", "tags":["milk","dairy"], "price":60, "stock":200, "seasonMonths":[], "substitutes":["p_almond_milk"], "imageUrl":""},
    {"_id":"p_bread", "name":"Whole Wheat Bread", "brand":"BakeHouse", "category":"bakery", "tags":["bread","wheat"], "price":40, "stock":150, "seasonMonths":[], "substitutes":[], "imageUrl":""},
    {"_id":"p_almond_milk", "name":"Almond Milk 1L", "brand":"NutriMilk", "category":"dairy", "tags":["milk","almond"], "price":120, "stock":50, "seasonMonths":[], "substitutes":["p_milk"], "imageUrl":""},
    {"_id":"p_pear","name":"Fresh Pear","brand":"LocalFarm","category":"produce","tags":["pear","fruit"],"price":55,"stock":80,"seasonMonths":[8,9,10],"substitutes":["p_apple"],"imageUrl":""}
]

async def seed():
    await db.products.delete_many({})
    await db.products.insert_many(sample_products)
    print("Seeded products.")

if __name__ == "__main__":
    asyncio.run(seed())
