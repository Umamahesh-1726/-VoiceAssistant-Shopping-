from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import product_routes, cart_routes, voice_routes

app = FastAPI(
    title="Mini Store Voice E-Commerce API",
    description="Voice-enabled shopping with recommendations and user memory",
    version="2.0.0"
)

# ✅ Enable CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include all route modules
app.include_router(product_routes.router, prefix="/products", tags=["Products"])
app.include_router(cart_routes.router, prefix="/cart", tags=["Cart"])
app.include_router(voice_routes.router, prefix="/voice", tags=["Voice & NLP"])

@app.get("/")
def root():
    return {
        "message": "Mini Store Backend running 🛒",
        "version": "2.0.0",
        "features": [
            "Voice commands (add, remove, search, view cart)",
            "Smart product recommendations",
            "User activity tracking",
            "Personalized suggestions",
            "Multi-language support"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "mini-store-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)