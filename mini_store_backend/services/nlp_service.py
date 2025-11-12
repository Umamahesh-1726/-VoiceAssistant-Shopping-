import re
import json
import os
import httpx
from pathlib import Path
from rapidfuzz import fuzz, process
from datetime import datetime


# =====================================================
# Load all products from JSON
# =====================================================
def load_products():
    """Load all products from local JSON"""
    current_dir = Path(__file__).parent

    possible_paths = [
        current_dir / "data" / "products.json",
        current_dir.parent / "data" / "products.json",
        current_dir.parent.parent / "frontend" / "src" / "data" / "products.json",
    ]

    json_path = None
    for path in possible_paths:
        if path.exists():
            json_path = path
            print(f"✅ Found products.json at: {path}")
            break

    if not json_path:
        print("❌ products.json not found.")
        return []

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading products.json: {e}")
        return []

    all_products = []
    for category, items in data.items():
        for item in items:
            all_products.append({
                "id": item.get("id"),
                "name": item.get("name", ""),
                "price": item.get("price", 0),
                "image": item.get("image", ""),
                "category": category
            })
    print(f"✅ Loaded {len(all_products)} products from JSON")
    return all_products


# =====================================================
# Enhanced word corrections for voice recognition
# =====================================================
COMMON_VOICE_CORRECTIONS = {
    # Cart variations
    "cut": "cart",
    "kat": "cart",
    "kart": "cart",
    "caught": "cart",
    "cot": "cart",
    "cat": "cart",
    
    # Add variations
    "ad": "add",
    "had": "add",
    "at": "add",
    "ed": "add",
    
    # Remove variations
    "remov": "remove",
    "remove": "remove",
    "delete": "remove",
    
    # Show variations
    "so": "show",
    "sho": "show",
    
    # Product name corrections
    "apples": "apple",
    "aple": "apple",
    "aplle": "apple",
    "milk": "milk",
    "melk": "milk",
    "milke": "milk",
    "bred": "bread",
    "brd": "bread",
    "bananas": "banana",
    "bannana": "banana",
    "banna": "banana",
    "tomatos": "tomato",
    "tomatoes": "tomato",
    "potatos": "potato",
    "potatoes": "potato",
}

def correct_voice_input(text: str) -> str:
    """Apply common voice recognition corrections"""
    words = text.lower().split()
    corrected = []
    
    for word in words:
        # Remove common filler words
        if word in ["the", "my", "to", "a", "an"]:
            continue
        corrected.append(COMMON_VOICE_CORRECTIONS.get(word, word))
    
    return " ".join(corrected)


# =====================================================
# Recommendation + Similarity helpers
# =====================================================
def get_category_recommendations(category: str, exclude_id: str = None, limit: int = 3):
    """Get products from same category"""
    products = load_products()
    category_products = [p for p in products if p["category"] == category and p["id"] != exclude_id]
    return category_products[:limit]


def get_related_recommendations(product_id: str, limit: int = 5):
    """Get related products based on category and price range"""
    products = load_products()
    
    # Find the current product
    current_product = next((p for p in products if p["id"] == product_id), None)
    if not current_product:
        return products[:limit]
    
    # Get products from same category and similar price
    price = current_product["price"]
    category = current_product["category"]
    
    related = []
    for product in products:
        if product["id"] == product_id:
            continue
        
        score = 0
        # Same category gets high score
        if product["category"] == category:
            score += 50
        
        # Similar price (within 30% range)
        price_diff = abs(product["price"] - price) / price
        if price_diff < 0.3:
            score += 30
        elif price_diff < 0.5:
            score += 15
        
        if score > 0:
            related.append({**product, "relevance_score": score})
    
    # Sort by relevance
    related.sort(key=lambda x: x["relevance_score"], reverse=True)
    return related[:limit]


def get_similar_products(search_term: str, limit: int = 5):
    """Get products matching search term"""
    products = load_products()
    results = []
    for product in products:
        name_score = fuzz.partial_ratio(search_term.lower(), product["name"].lower())
        category_score = fuzz.partial_ratio(search_term.lower(), product["category"].lower())
        score = max(name_score, category_score)
        if score > 40:
            results.append({**product, "similarity_score": score})
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results[:limit]


# =====================================================
# NLP helpers
# =====================================================
def extract_quantity(text: str) -> int:
    """Extract quantity from voice command"""
    word_to_num = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20,
        "a": 1, "an": 1, "single": 1, "couple": 2, "few": 3
    }
    
    text_lower = text.lower()
    
    # Check for word numbers
    for word, num in word_to_num.items():
        if word in text_lower:
            return num
    
    # Check for digit numbers
    qty_match = re.search(r'\b(\d+)\b', text)
    if qty_match:
        return int(qty_match.group(1))
    
    return 1


def detect_intent(text: str) -> str:
    """Detect user intent from voice command with improved accuracy"""
    text_lower = text.lower()
    
    # Correct common voice recognition errors
    text_lower = correct_voice_input(text_lower)
    
    # View cart - prioritize this to avoid confusion
    if any(phrase in text_lower for phrase in ["show cart", "view cart", "my cart", "open cart", "check cart", "see cart", "what's in my cart", "cart items"]):
        return "view_cart"
    
    # Clear cart
    if any(phrase in text_lower for phrase in ["clear cart", "empty cart", "remove all", "delete all", "clear my cart", "empty my cart"]):
        return "clear_cart"
    
    # Add to cart - IMPROVED: works without "cart" or "to"
    # Examples: "add apples", "buy milk", "get two bananas"
    if any(word in text_lower for word in ["add", "buy", "get", "purchase", "i want", "i need"]):
        # Don't require "cart" or "to" - just the action word is enough
        return "add_to_cart"
    
    # Remove from cart - IMPROVED: works without "cart"
    # Examples: "remove apple", "delete milk"
    if any(word in text_lower for word in ["remove", "delete", "cancel", "take out", "drop"]):
        return "remove_from_cart"
    
    # Search product
    if any(word in text_lower for word in ["find", "search", "show", "look for", "where is", "do you have", "tell me about"]):
        return "search_product"
    
    # List products
    if any(phrase in text_lower for phrase in ["list", "show all", "available", "what do you have", "all products"]):
        return "list_products"
    
    # Default to search
    return "search_product"


# =====================================================
# Main Command Parser
# =====================================================
async def parse_command(text: str, user_id: str = None):
    """Parse voice command with improved accuracy and recommendations"""
    text = (text or "").lower().strip()
    
    # Apply voice corrections
    text = correct_voice_input(text)
    
    result = {
        "intent": "unknown",
        "slots": {
            "product_name": None,
            "product_id": None,
            "quantity": 1,
            "category": None
        },
        "confidence": 0.0,
        "recommendations": [],
        "message": "",
        "user_id": user_id
    }

    if not text:
        result["message"] = "I didn't hear anything. Please try again."
        return result

    result["intent"] = detect_intent(text)
    print(f"🎯 Detected intent: {result['intent']} for command: '{text}'")

    result["slots"]["quantity"] = extract_quantity(text)
    products = load_products()
    if not products:
        result["message"] = "Sorry, product catalog is not available."
        return result

    # ✅ Handle direct intents
    if result["intent"] == "view_cart":
        async with httpx.AsyncClient() as client:
            r = await client.get(f"http://localhost:8080/cart/{user_id}")
            cart_data = r.json()
        result["slots"]["cart"] = cart_data
        count = len(cart_data.get("items", []))
        result["message"] = cart_data.get("message", f"Your cart contains {count} item{'s' if count != 1 else ''}.")
        result["confidence"] = 1.0
        return result

    if result["intent"] == "clear_cart":
        async with httpx.AsyncClient() as client:
            await client.delete(f"http://localhost:8080/cart/{user_id}/clear")
        result["message"] = "Your cart has been cleared successfully."
        result["confidence"] = 1.0
        return result

    if result["intent"] == "list_products":
        result["message"] = f"We have {len(products)} products available across multiple categories."
        result["recommendations"] = get_similar_products(text, limit=5)
        result["confidence"] = 1.0
        return result

    # ✅ Fuzzy match to identify product
    product_names = [p["name"].lower() for p in products]
    best_match = process.extractOne(text, product_names, scorer=fuzz.token_set_ratio)

    if best_match and best_match[1] >= 60:
        matched_name = best_match[0]
        matched_product = next((p for p in products if p["name"].lower() == matched_name), None)
        if matched_product:
            result["slots"]["product_name"] = matched_product["name"]
            result["slots"]["product_id"] = matched_product["id"]
            result["slots"]["category"] = matched_product["category"]
            result["confidence"] = round(best_match[1] / 100, 2)
            qty = result["slots"]["quantity"]

            print(f"✅ Matched product: {matched_product['name']} ({matched_product['id']}) with confidence {result['confidence']}")

            # ✅ Perform backend actions
            async with httpx.AsyncClient() as client:
                if result["intent"] == "add_to_cart":
                    try:
                        response = await client.post(
                            f"http://localhost:8080/cart/{user_id}/add",
                            json={
                                "productName": matched_product["name"],
                                "productId": matched_product["id"],
                                "qty": qty,
                                "price": matched_product["price"],
                                "image": matched_product["image"],
                                "category": matched_product["category"]
                            },
                            timeout=5.0
                        )
                        response_data = response.json()
                        print(f"✅ Cart add response: {response_data}")
                        result["message"] = f"Added {qty} x {matched_product['name']} to your cart (₹{matched_product['price'] * qty})"
                    except Exception as e:
                        print(f"❌ Failed to add to cart: {e}")
                        result["message"] = f"Added {qty} x {matched_product['name']} (cart sync pending)"

                elif result["intent"] == "remove_from_cart":
                    try:
                        response = await client.post(
                            f"http://localhost:8080/cart/{user_id}/remove",
                            json={
                                "productName": matched_product["name"],
                                "productId": matched_product["id"]
                            },
                            timeout=5.0
                        )
                        result["message"] = f"Removed {matched_product['name']} from your cart"
                    except Exception as e:
                        print(f"❌ Failed to remove from cart: {e}")
                        result["message"] = f"Removed {matched_product['name']} (cart sync pending)"

                elif result["intent"] == "search_product":
                    result["message"] = f"Found {matched_product['name']} - ₹{matched_product['price']} in {matched_product['category']}"

            # ✅ Get related recommendations
            result["recommendations"] = get_related_recommendations(
                matched_product["id"],
                limit=5
            )
            return result

    # No direct match → show similar products
    similar_products = get_similar_products(text, limit=5)
    if similar_products:
        result["recommendations"] = similar_products
        result["message"] = f"I couldn't find an exact match for '{text}'. Here are some similar products you might like."
        result["confidence"] = 0.5
    else:
        result["message"] = f"Sorry, I couldn't find any products matching '{text}'. Try browsing our categories."
        print(f"❌ No products found for '{text}'")

    return result


# =====================================================
# Personalized Recommendations
# =====================================================
def get_personalized_recommendations(user_history: list, limit: int = 5):
    """Get personalized recommendations based on user's purchase history"""
    products = load_products()
    if not user_history:
        # New user - return trending/popular products
        return products[:limit]

    # Extract user preferences
    user_categories = [item.get("category") for item in user_history if item.get("category")]
    purchased_ids = {item.get("product_id") for item in user_history}
    
    # Count category frequency
    category_counts = {}
    for cat in user_categories:
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # Sort categories by frequency
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    
    recommendations = []
    
    # First, recommend from favorite categories
    for category, _ in sorted_categories:
        for product in products:
            if (product["id"] not in purchased_ids and 
                product["category"] == category and 
                product not in recommendations):
                recommendations.append(product)
                if len(recommendations) >= limit:
                    return recommendations[:limit]
    
    # Fill remaining with other products
    for product in products:
        if product["id"] not in purchased_ids and product not in recommendations:
            recommendations.append(product)
            if len(recommendations) >= limit:
                break

    return recommendations[:limit]