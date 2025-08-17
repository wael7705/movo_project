from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_orders(order_status: str | None = None):
	return []


@router.post("/demo")
async def create_demo_order():
	return {"id": 1, "current_status": "pending"}
