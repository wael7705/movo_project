"""
Simple FastAPI app for testing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MOVO Simple API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "MOVO API is running!"}

@app.get("/api/v1/db_ping")
async def db_ping():
    return {"ok": True, "message": "API is working"}

@app.get("/api/v1/orders")
async def get_orders():
    return [
        {
            "order_id": 1,
            "customer_name": "أحمد محمد",
            "restaurant_name": "مطعم الشام",
            "status": "pending",
            "total_price_customer": 25.00,
            "created_at": "2025-01-15T10:00:00"
        }
    ]

@app.post("/api/v1/orders/demo")
async def create_demo_order():
    return {
        "order_id": 999,
        "status": "pending",
        "message": "Demo order created successfully"
    }

@app.patch("/api/v1/orders/{order_id}")
async def update_order_status(order_id: int, status_update: dict):
    return {
        "order_id": order_id,
        "status": status_update.get("status", "updated"),
        "message": "Order status updated"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simple_app:app", host="0.0.0.0", port=8000, reload=True)
