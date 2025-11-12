from fastapi import APIRouter, Body, HTTPException
from services import nlp_service
from db import db
from datetime import datetime

router = APIRouter()

@router.post("/parse")
async def parse_voice_command(payload: dict = Body(...)):
    """Parse voice command with user context"""
    text = payload.get("text", "")
    user_id = payload.get("user_id", "guest")
    
    # Parse command using enhanced NLP
    result = await nlp_service.parse_command(text, user_id)
    
    # Log user activity
    await log_user_activity(user_id, text, result)
    
    return result


@router.get("/recommendations/{user_id}")
async def get_user_recommendations(user_id: str):
    """Get personalized recommendations for returning users"""
    
    # Get user's purchase history
    user_activity = await db.user_activity.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(20).to_list(20)
    
    # Extract purchase history
    purchase_history = []
    for activity in user_activity:
        if activity.get("intent") == "add_to_cart" and activity.get("product_id"):
            purchase_history.append({
                "product_id": activity.get("product_id"),
                "product_name": activity.get("product_name"),
                "category": activity.get("category"),
                "timestamp": activity.get("timestamp")
            })
    
    # Get personalized recommendations
    recommendations = nlp_service.get_personalized_recommendations(
        purchase_history, 
        limit=5
    )
    
    return {
        "user_id": user_id,
        "total_activities": len(user_activity),
        "recent_purchases": len(purchase_history),
        "recommendations": recommendations
    }


@router.get("/user/{user_id}/history")
async def get_user_history(user_id: str, limit: int = 20):
    """Get user's voice command history"""
    
    activities = await db.user_activity.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    # Calculate statistics
    total_commands = len(activities)
    successful_commands = len([a for a in activities if a.get("confidence", 0) > 0.7])
    
    return {
        "user_id": user_id,
        "total_commands": total_commands,
        "successful_commands": successful_commands,
        "success_rate": round((successful_commands / total_commands * 100), 2) if total_commands > 0 else 0,
        "activities": activities
    }


@router.get("/user/{user_id}/profile")
async def get_user_profile(user_id: str):
    """Get user profile with preferences and statistics"""
    
    # Get user's activity
    activities = await db.user_activity.find(
        {"user_id": user_id}
    ).to_list(100)
    
    if not activities:
        return {
            "user_id": user_id,
            "is_new_user": True,
            "message": "Welcome! This is your first visit."
        }
    
    # Calculate preferences
    category_count = {}
    total_spent = 0
    favorite_products = {}
    
    for activity in activities:
        if activity.get("intent") == "add_to_cart":
            # Count categories
            category = activity.get("category")
            if category:
                category_count[category] = category_count.get(category, 0) + 1
            
            # Count favorite products
            product_id = activity.get("product_id")
            if product_id:
                favorite_products[product_id] = favorite_products.get(product_id, 0) + 1
    
    # Find favorite category
    favorite_category = max(category_count.items(), key=lambda x: x[1])[0] if category_count else None
    
    # Find most purchased product
    most_purchased = max(favorite_products.items(), key=lambda x: x[1])[0] if favorite_products else None
    
    # Get last visit
    last_visit = activities[-1].get("timestamp") if activities else None
    
    return {
        "user_id": user_id,
        "is_new_user": False,
        "total_interactions": len(activities),
        "favorite_category": favorite_category,
        "most_purchased_product": most_purchased,
        "last_visit": last_visit,
        "preferences": category_count
    }


async def log_user_activity(user_id: str, command_text: str, result: dict):
    """Log user voice command activity"""
    
    activity_log = {
        "user_id": user_id,
        "command_text": command_text,
        "intent": result.get("intent"),
        "product_id": result.get("slots", {}).get("product_id"),
        "product_name": result.get("slots", {}).get("product_name"),
        "category": result.get("slots", {}).get("category"),
        "quantity": result.get("slots", {}).get("quantity", 1),
        "confidence": result.get("confidence", 0),
        "timestamp": datetime.utcnow(),
        "success": result.get("confidence", 0) > 0.7
    }
    
    await db.user_activity.insert_one(activity_log)


@router.post("/feedback")
async def submit_feedback(payload: dict = Body(...)):
    """Allow users to provide feedback on voice recognition"""
    
    user_id = payload.get("user_id", "guest")
    command_text = payload.get("command_text", "")
    was_correct = payload.get("was_correct", False)
    actual_product = payload.get("actual_product", None)
    
    feedback = {
        "user_id": user_id,
        "command_text": command_text,
        "was_correct": was_correct,
        "actual_product": actual_product,
        "timestamp": datetime.utcnow()
    }
    
    await db.feedback.insert_one(feedback)
    
    return {"message": "Thank you for your feedback!"}


@router.delete("/user/{user_id}/history")
async def clear_user_history(user_id: str):
    """Clear user's activity history"""
    
    result = await db.user_activity.delete_many({"user_id": user_id})
    
    return {
        "user_id": user_id,
        "deleted_count": result.deleted_count,
        "message": "History cleared successfully"
    }