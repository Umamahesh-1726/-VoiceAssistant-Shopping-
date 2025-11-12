from fastapi import APIRouter, Body
from db import db
from datetime import datetime

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("/{username}")
async def get_cart(username: str):
    """Return user's cart with welcome message for returning users"""
    user_cart = await db.carts.find_one({"username": username})
    
    if not user_cart:
        # New user - create empty cart
        user_cart = {
            "username": username, 
            "items": [],
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        }
        await db.carts.insert_one(user_cart)
        return {
            "username": username,
            "items": [],
            "is_returning_user": False,
            "message": f"Welcome {username}! Start shopping with voice commands."
        }
    
    # Returning user with items
    items = user_cart.get("items", [])
    return {
        "username": username,
        "items": items,
        "is_returning_user": len(items) > 0,
        "message": f"Welcome back {username}! You have {len(items)} item(s) in your cart." if items else f"Welcome back {username}!"
    }

@router.post("/{username}/add")
async def add_to_cart(username: str, data: dict = Body(...)):
    """Add product with full details and quantity support"""
    product_name = data.get("productName")
    product_id = data.get("productId", product_name.lower().replace(" ", "_"))
    qty = int(data.get("qty", 1))
    price = float(data.get("price", 0))
    image = data.get("image", "")
    category = data.get("category", "General")

    cart = await db.carts.find_one({"username": username})
    if not cart:
        cart = {
            "username": username, 
            "items": [],
            "created_at": datetime.utcnow()
        }

    # Check if product already exists
    found = False
    for item in cart["items"]:
        if item["productId"] == product_id:
            item["qty"] += qty
            item["last_updated"] = datetime.utcnow()
            found = True
            break

    if not found:
        cart["items"].append({
            "productId": product_id,
            "productName": product_name,
            "qty": qty,
            "price": price,
            "image": image,
            "category": category,
            "added_at": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        })

    # Update cart in database
    await db.carts.update_one(
        {"username": username},
        {
            "$set": {
                "items": cart["items"],
                "last_updated": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    return {
        "success": True,
        "message": f"Added {qty} x {product_name} to {username}'s cart",
        "cart_count": len(cart["items"])
    }

@router.post("/{username}/remove")
async def remove_from_cart(username: str, data: dict = Body(...)):
    """Remove product by ID or name"""
    product_name = data.get("productName")
    product_id = data.get("productId")
    
    cart = await db.carts.find_one({"username": username})
    if not cart:
        return {"success": False, "message": "Cart not found"}

    # Remove by ID or name
    original_count = len(cart["items"])
    cart["items"] = [
        item for item in cart["items"]
        if not (
            (product_id and item.get("productId") == product_id) or
            (product_name and item["productName"].lower() == product_name.lower())
        )
    ]

    removed_count = original_count - len(cart["items"])
    
    await db.carts.update_one(
        {"username": username}, 
        {
            "$set": {
                "items": cart["items"],
                "last_updated": datetime.utcnow()
            }
        }
    )
    
    return {
        "success": True,
        "message": f"Removed {product_name or product_id} from cart",
        "removed_count": removed_count,
        "cart_count": len(cart["items"])
    }

@router.delete("/{username}/clear")
async def clear_cart(username: str):
    """Clear all items from user's cart"""
    result = await db.carts.update_one(
        {"username": username},
        {
            "$set": {
                "items": [],
                "last_updated": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    return {
        "success": True,
        "message": f"{username}'s cart cleared successfully",
        "cart_count": 0
    }

@router.get("/{username}/recommendations")
async def get_cart_recommendations(username: str):
    """Get personalized recommendations based on cart items"""
    cart = await db.carts.find_one({"username": username})
    
    if not cart or not cart.get("items"):
        return {"recommendations": []}
    
    # Get categories from cart
    cart_categories = list(set([item.get("category") for item in cart["items"] if item.get("category")]))
    
    # Get user activity for better recommendations
    activities = await db.user_activity.find(
        {"user_id": username}
    ).sort("timestamp", -1).limit(50).to_list(50)
    
    # Count category preferences
    category_counts = {}
    for activity in activities:
        cat = activity.get("category")
        if cat:
            category_counts[cat] = category_counts.get(cat, 0) + 1
    
    return {
        "cart_categories": cart_categories,
        "favorite_categories": sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3],
        "total_activities": len(activities)
    }