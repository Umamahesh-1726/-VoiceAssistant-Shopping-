# setup_database.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client.mini_store

async def setup_database():
    """Initialize database with indexes and collections"""
    
    print("🔧 Setting up Mini Store Database...")
    
    # Create indexes for user_activity collection
    print("\n📊 Creating indexes for user_activity...")
    await db.user_activity.create_index("user_id")
    await db.user_activity.create_index("timestamp")
    await db.user_activity.create_index([("user_id", 1), ("timestamp", -1)])
    await db.user_activity.create_index("intent")
    await db.user_activity.create_index("product_id")
    print("✅ user_activity indexes created")
    
    # Create indexes for carts collection
    print("\n📊 Creating indexes for carts...")
    await db.carts.create_index("userId", unique=True)
    print("✅ carts indexes created")
    
    # Create indexes for products collection
    print("\n📊 Creating indexes for products...")
    await db.products.create_index("name")
    await db.products.create_index("category")
    await db.products.create_index("price")
    await db.products.create_index([("name", "text")])  # Text search
    print("✅ products indexes created")
    
    # Create indexes for feedback collection
    print("\n📊 Creating indexes for feedback...")
    await db.feedback.create_index("user_id")
    await db.feedback.create_index("timestamp")
    print("✅ feedback indexes created")
    
    # Show collections
    collections = await db.list_collection_names()
    print(f"\n📂 Available collections: {', '.join(collections)}")
    
    # Show sample stats
    user_activity_count = await db.user_activity.count_documents({})
    carts_count = await db.carts.count_documents({})
    products_count = await db.products.count_documents({})
    
    print(f"\n📈 Database Statistics:")
    print(f"   - User activities: {user_activity_count}")
    print(f"   - Active carts: {carts_count}")
    print(f"   - Products: {products_count}")
    
    print("\n✅ Database setup complete!")
    print("\n💡 Next steps:")
    print("   1. Run: python seed_products.py (to add sample products)")
    print("   2. Start backend: uvicorn main:app --reload --port 8080")
    print("   3. Start frontend: npm start")

if __name__ == "__main__":
    asyncio.run(setup_database())