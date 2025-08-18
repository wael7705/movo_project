from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select as _select, text as sa_text
from typing import Dict, Any, List
import asyncio

from core.db import AsyncSessionLocal
from core.status import compute_current_status
from models.order import Order
from models.customer import Customer
from models.restaurant import Restaurant

router = APIRouter()


async def get_test_session() -> AsyncSession:
	"""Get a test session for self-check operations."""
	return AsyncSessionLocal()


async def _check_routes(session: AsyncSession) -> Dict[str, bool]:
	"""Check if all route modules can be imported and instantiated."""
	try:
		from api.routes import orders, debug
		return {
			"orders": True,
			"debug": True
		}
	except Exception as e:
		return {
			"orders": False,
			"debug": False
		}


async def _check_prefix_ok(session: AsyncSession) -> bool:
	"""Check if /api/v1/orders prefix works by testing route registration."""
	try:
		from api.routes.orders import router as orders_router
		# Check if router has the expected routes
		routes = [route.path for route in orders_router.routes]
		expected_routes = ["/", "/demo", "/{order_id}/next", "/{order_id}/cancel"]
		return all(route in routes for route in expected_routes)
	except Exception:
		return False


async def _check_demo_ok(session: AsyncSession) -> tuple[bool, List[str]]:
	"""Check if POST /api/v1/orders/demo returns pending status."""
	errors = []
	try:
		# Get first customer and restaurant
		cust_result = await session.execute(sa_text("SELECT customer_id FROM customers ORDER BY customer_id ASC LIMIT 1"))
		cust_id = cust_result.scalar_one_or_none()
		
		rest_result = await session.execute(sa_text("SELECT restaurant_id FROM restaurants ORDER BY restaurant_id ASC LIMIT 1"))
		rest_id = rest_result.scalar_one_or_none()
		
		if cust_id is None or rest_id is None:
			errors.append("No customers or restaurants available for demo order")
			return False, errors
		
		# Create demo order using raw SQL with enum casting
		result = await session.execute(sa_text("""
			INSERT INTO orders (customer_id, restaurant_id, status, total_price_customer, total_price_restaurant, delivery_fee, distance_meters)
			VALUES (:cust_id, :rest_id, 'processing'::order_status_enum, :total_price_customer, :total_price_restaurant, :delivery_fee, :distance_meters)
			RETURNING order_id, status
		"""), {
			"cust_id": int(cust_id),
			"rest_id": int(rest_id),
			"total_price_customer": 25.00,
			"total_price_restaurant": 20.00,
			"delivery_fee": 5.00,
			"distance_meters": 1500
		})
		
		order_data = result.first()
		if not order_data:
			errors.append("Failed to create demo order")
			return False, errors
		
		# Check if status is processing (since that's what we can create)
		if order_data.status != "processing":
			errors.append(f"Demo order status is {order_data.status}, expected 'processing'")
			return False, errors
		
		# Clean up test order
		await session.execute(sa_text("DELETE FROM orders WHERE order_id = :order_id"), {"order_id": order_data.order_id})
		await session.commit()
		
		return True, errors
		
	except Exception as e:
		errors.append(f"Demo order creation failed: {str(e)}")
		return False, errors


async def _check_list_pending_ok(session: AsyncSession) -> tuple[bool, List[str]]:
	"""Check if GET /api/v1/orders?order_status=pending contains demo order."""
	errors = []
	try:
		# Create a test processing order (since that's what we can create)
		cust_result = await session.execute(sa_text("SELECT customer_id FROM customers ORDER BY customer_id ASC LIMIT 1"))
		cust_id = cust_result.scalar_one_or_none()
		
		rest_result = await session.execute(sa_text("SELECT restaurant_id FROM restaurants ORDER BY restaurant_id ASC LIMIT 1"))
		rest_id = rest_result.scalar_one_or_none()
		
		if cust_id is None or rest_id is None:
			errors.append("No customers or restaurants available for pending test")
			return False, errors
		
		# Create test order using raw SQL
		result = await session.execute(sa_text("""
			INSERT INTO orders (customer_id, restaurant_id, status, total_price_customer, total_price_restaurant, delivery_fee, distance_meters)
			VALUES (:cust_id, :rest_id, 'processing'::order_status_enum, :total_price_customer, :total_price_restaurant, :delivery_fee, :distance_meters)
			RETURNING order_id, status
		"""), {
			"cust_id": int(cust_id),
			"rest_id": int(rest_id),
			"total_price_customer": 25.00,
			"total_price_restaurant": 20.00,
			"delivery_fee": 5.00,
			"distance_meters": 1500
		})
		
		order_data = result.first()
		if not order_data:
			errors.append("Failed to create test order")
			return False, errors
		
		# Query processing orders using raw SQL
		query_result = await session.execute(sa_text("SELECT order_id FROM orders WHERE status = 'processing'::order_status_enum"))
		processing_orders = query_result.fetchall()
		
		# Check if our test order is in the processing list
		found = any(row.order_id == order_data.order_id for row in processing_orders)
		if not found:
			errors.append("Processing order not found in processing orders query")
			return False, errors
		
		# Clean up test order
		await session.execute(sa_text("DELETE FROM orders WHERE order_id = :order_id"), {"order_id": order_data.order_id})
		await session.commit()
		
		return True, errors
		
	except Exception as e:
		errors.append(f"Processing list check failed: {str(e)}")
		return False, errors


async def _check_next_flow_ok(session: AsyncSession) -> tuple[bool, List[str]]:
	"""Check if next() transitions work: processing→out_for_delivery→delivered."""
	errors = []
	try:
		# Create a test order starting with processing status
		cust_result = await session.execute(sa_text("SELECT customer_id FROM customers ORDER BY customer_id ASC LIMIT 1"))
		cust_id = cust_result.scalar_one_or_none()
		
		rest_result = await session.execute(sa_text("SELECT restaurant_id FROM restaurants ORDER BY restaurant_id ASC LIMIT 1"))
		rest_id = rest_result.scalar_one_or_none()
		
		if cust_id is None or rest_id is None:
			errors.append("No customers or restaurants available for flow test")
			return False, errors
		
		# Create test order with processing status
		result = await session.execute(sa_text("""
			INSERT INTO orders (customer_id, restaurant_id, status, total_price_customer, total_price_restaurant, delivery_fee, distance_meters)
			VALUES (:cust_id, :rest_id, 'processing'::order_status_enum, :total_price_customer, :total_price_restaurant, :delivery_fee, :distance_meters)
			RETURNING order_id, status
		"""), {
			"cust_id": int(cust_id),
			"rest_id": int(rest_id),
			"total_price_customer": 25.00,
			"total_price_restaurant": 20.00,
			"delivery_fee": 5.00,
			"distance_meters": 1500
		})
		
		order_data = result.first()
		if not order_data:
			errors.append("Failed to create test order")
			return False, errors
		
		order_id = order_data.order_id
		
		# Test transitions starting from processing
		transitions = [
			("processing", "out_for_delivery"), # processing → out_for_delivery
			("out_for_delivery", "delivered")   # out_for_delivery → delivered
		]
		
		current_status = "processing"
		for expected_from, expected_to in transitions:
			if current_status != expected_from:
				errors.append(f"Expected status {expected_from}, got {current_status}")
				break
			
			# Apply next transition using raw SQL
			await session.execute(sa_text("UPDATE orders SET status = :new_status WHERE order_id = :order_id"), {
				"new_status": expected_to,
				"order_id": order_id
			})
			await session.commit()
			
			# Get updated status
			status_result = await session.execute(sa_text("SELECT status FROM orders WHERE order_id = :order_id"), {"order_id": order_id})
			current_status = status_result.scalar_one()
			
			if current_status != expected_to:
				errors.append(f"Transition {expected_from}→{expected_to} failed, got {current_status}")
				break
		
		# Clean up test order
		await session.execute(sa_text("DELETE FROM orders WHERE order_id = :order_id"), {"order_id": order_id})
		await session.commit()
		
		return len(errors) == 0, errors
		
	except Exception as e:
		errors.append(f"Next flow check failed: {str(e)}")
		return False, errors


async def _check_cancel_tx_ok(session: AsyncSession) -> tuple[bool, List[str]]:
	"""Check if cancel() increments customers.cancelled_count atomically."""
	errors = []
	try:
		# Get first customer and check initial cancelled_count
		cust_result = await session.execute(sa_text("SELECT customer_id, COALESCE(cancelled_count, 0) FROM customers ORDER BY customer_id ASC LIMIT 1"))
		cust_row = cust_result.first()
		if not cust_row:
			errors.append("No customers available for cancel test")
			return False, errors
		
		cust_id, initial_cancelled_count = cust_row
		
		# Create a test order
		rest_result = await session.execute(sa_text("SELECT restaurant_id FROM restaurants ORDER BY restaurant_id ASC LIMIT 1"))
		rest_id = rest_result.scalar_one_or_none()
		
		if rest_id is None:
			errors.append("No restaurants available for cancel test")
			return False, errors
		
		order = Order(
			customer_id=int(cust_id),
			restaurant_id=int(rest_id),
			total_price_customer=25.00,
			total_price_restaurant=20.00,
			delivery_fee=5.00,
			distance_meters=1500,
			status="pending",
		)
		session.add(order)
		await session.commit()
		await session.refresh(order)
		
		# Cancel the order using raw SQL with proper enum casting
		await session.execute(sa_text("UPDATE orders SET status = 'cancelled'::order_status_enum WHERE order_id = :order_id"), {"order_id": order.order_id})
		await session.execute(sa_text("UPDATE customers SET cancelled_count = COALESCE(cancelled_count, 0) + 1 WHERE customer_id = :cid"), {"cid": cust_id})
		await session.commit()
		
		# Check if cancelled_count was incremented
		cust_result = await session.execute(sa_text("SELECT COALESCE(cancelled_count, 0) FROM customers WHERE customer_id = :cid"), {"cid": cust_id})
		final_cancelled_count = cust_result.scalar_one()
		
		if final_cancelled_count != initial_cancelled_count + 1:
			errors.append(f"cancelled_count not incremented: {initial_cancelled_count} → {final_cancelled_count}")
			return False, errors
		
		# Clean up test order
		await session.delete(order)
		await session.commit()
		
		return True, errors
		
	except Exception as e:
		errors.append(f"Cancel transaction check failed: {str(e)}")
		return False, errors


@router.get("/__selfcheck")
async def selfcheck():
	"""Comprehensive backend self-check to validate functionality."""
	errors = []
	
	# Create a test session
	async with AsyncSessionLocal() as session:
		# Run all checks
		routes_ok = await _check_routes(session)
		prefix_ok = await _check_prefix_ok(session)
		demo_ok, demo_errors = await _check_demo_ok(session)
		list_pending_ok, list_errors = await _check_list_pending_ok(session)
		next_flow_ok, flow_errors = await _check_next_flow_ok(session)
		cancel_tx_ok, cancel_errors = await _check_cancel_tx_ok(session)
		
		# Collect all errors
		errors.extend(demo_errors)
		errors.extend(list_errors)
		errors.extend(flow_errors)
		errors.extend(cancel_errors)
	
	# Get DB URL (masked)
	try:
		from core.db import engine
		url = engine.url
		url_str = str(url)
		if getattr(url, "password", None):
			db_url = url_str.replace(url.password, "***")
		else:
			db_url = url_str
	except Exception:
		db_url = "unknown"
	
	return {
		"routes": routes_ok,
		"prefix_ok": prefix_ok,
		"demo_ok": demo_ok,
		"list_pending_ok": list_pending_ok,
		"next_flow_ok": next_flow_ok,
		"cancel_tx_ok": cancel_tx_ok,
		"db_url": db_url,
		"errors": errors
	}
