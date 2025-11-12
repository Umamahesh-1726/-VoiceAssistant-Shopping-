from motor.motor_asyncio import AsyncIOMotorClient
import os

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URI)
db = client.mini_store

# Collections
# db.products - Product catalog
# db.carts - User shopping carts
# db.user_activity - User voice command history
# db.feedback - User feedback on voice recognition