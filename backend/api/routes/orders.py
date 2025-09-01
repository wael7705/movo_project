from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy import select, func
from sqlalchemy import text as sa_text, literal_column
from sqlalchemy import text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import logging

from core.status import compute_current_status, compute_substage, normalize_status, VALID
from core.db import get_session
from models.order import Order
from models.note import Note
from models.rating import Rating
from realtime.ws_notifications import notify_tab
from realtime.sio import notify_tab as notify_tab2
from models.customer import Customer
from models.restaurant import Restaurant

router = APIRouter()

# خريطة الحالات القديمة إلى الجديدة
ALIASES = {"issue": "problem"}

def _norm(v: str | None) -> str | None:
    """Normalize status value: lowercase, strip, apply aliases."""
    if not v:
        return None
    v = v.strip().lower()
    return ALIASES.get(v, v)

def _extract_status(status=None, order_status=None, tab=None):
    """Extract and validate status from any of the three parameters."""
    q = _norm(status) or _norm(order_status) or _norm(tab)
    return q if q in VALID else None

def serialize(o: Order) -> dict:
    """Serialize order with current_status and substage."""
    d = {
        "order_id": o.order_id,
        "customer_id": o.customer_id,
        "restaurant_id": o.restaurant_id,
        "captain_id": o.captain_id,
        "status": o.status,
        "total_price_customer": o.total_price_customer,
        "delivery_fee": o.delivery_fee,
        "created_at": o.created_at.isoformat() if o.created_at else None,
        "payment_method": o.payment_method,
        "delivery_method": o.delivery_method,
        "distance_meters": o.distance_meters,
    }
    
    d["current_status"] = compute_current_status(o)
    d["substage"] = compute_substage(o) if d["current_status"] == "processing" else None
    
    # إضافة معلومات إضافية للعرض
    d["customer_name"] = f"عميل #{o.customer_id}"
    d["restaurant_name"] = f"مطعم #{o.restaurant_id}"
    
    return d

@router.get("", response_model=List[Dict[str, Any]])
async def list_orders(
    status: str | None = Query(default=None),
    order_status: str | None = Query(default=None),
    tab: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    """List orders with filtering by status, order_status, or tab."""
    q = _extract_status(status, order_status, tab)
    
    # Get orders with pagination
    result = await session.execute(
        select(Order).order_by(Order.created_at.desc()).limit(limit).offset(offset)
    )
    orders = result.scalars().all()
    
    # Serialize orders
    rows = [serialize(o) for o in orders]
    
    # Apply status filtering if requested - الفلترة تعتمد حصرياً على current_status
    if q:
        rows = [r for r in rows if r.get("current_status") == q]
    
    return rows


@router.get("/counts", response_model=Dict[str, int])
async def counts(session: AsyncSession = Depends(get_session)) -> Dict[str, int]:
    """Return counts per tab (using current_status logic to match UI).
    This aligns counters with what the dashboard renders under each tab.
    """
    result = await session.execute(select(Order))
    orders = result.scalars().all()

    counts_map: Dict[str, int] = {k: 0 for k in VALID}
    for order in orders:
        current = compute_current_status(order)
        if current in counts_map:
            counts_map[current] += 1

    return counts_map

@router.post("/demo", response_model=Dict[str, Any])
async def create_demo_order(session: AsyncSession = Depends(get_session)):
    """Create a demo order with pending status."""
    # Get first customer and restaurant
    cust_result = await session.execute(
        select(Customer).order_by(Customer.customer_id.asc()).limit(1)
    )
    cust = cust_result.scalars().first()
    
    rest_result = await session.execute(
        select(Restaurant).order_by(Restaurant.restaurant_id.asc()).limit(1)
    )
    rest = rest_result.scalars().first()
    
    if not cust or not rest:
        raise HTTPException(status_code=422, detail="No customer/restaurant available")
    
    # Create order - دائمًا pending
    o = Order(
        customer_id=cust.customer_id,
        restaurant_id=rest.restaurant_id,
        status="pending",  # هذا سيتم تطبيعه تلقائياً بواسطة التريغر
        total_price_customer=25.00,
        total_price_restaurant=20.00,
        delivery_fee=5.00,
        distance_meters=1500,
        payment_method="cash",
        delivery_method="standard"
    )
    session.add(o)
    await session.flush()
    await session.refresh(o)
    
    await session.commit()
    
    return serialize(o)

@router.post("/demo/processing", response_model=Dict[str, Any])
async def create_demo_processing_order(session: AsyncSession = Depends(get_session)):
    """Create a demo order in processing status with substage."""
    # Get first customer and restaurant
    cust_result = await session.execute(
        select(Customer).order_by(Customer.customer_id.asc()).limit(1)
    )
    cust = cust_result.scalars().first()
    
    rest_result = await session.execute(
        select(Restaurant).order_by(Restaurant.restaurant_id.asc()).limit(1)
    )
    rest = rest_result.scalars().first()
    
    if not cust or not rest:
        raise HTTPException(status_code=422, detail="No customer/restaurant available")
    
    # Create order in processing status
    o = Order(
        customer_id=cust.customer_id,
        restaurant_id=rest.restaurant_id,
        status="processing",
        current_stage_name="waiting_approval",  # للحصول على substage
        total_price_customer=30.00,
        total_price_restaurant=25.00,
        delivery_fee=5.00,
        distance_meters=2000,
        payment_method="card",
        delivery_method="express"
    )
    session.add(o)
    await session.flush()
    await session.refresh(o)
    
    await session.commit()
    
    return serialize(o)

@router.patch("/{order_id}/next", response_model=Dict[str, Any])
async def advance_order(order_id: int, session: AsyncSession = Depends(get_session)):
    """Advance order to next status."""
    result = await session.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    current = compute_current_status(order)
    
    # Check if order is in a valid state for transition
    if current in ['delivered', 'cancelled', 'problem', 'deferred', 'pickup']:
        raise HTTPException(status_code=400, detail="Invalid transition")
    
    # Apply next transition - منع ازدواج "حالات نشطة"
    if current == 'pending':
        # إذا كان الطلب deferred، اقفز مباشرة إلى processing
        if getattr(order, 'is_deferred', False):
            order.status = 'processing'
            order.current_stage_name = 'waiting_approval'
        else:
            # Normal orders go to choose_captain
            order.status = 'choose_captain'
    elif current == 'choose_captain':
        order.status = 'processing'
        order.current_stage_name = 'waiting_approval'
    elif current == 'processing':
        # تحديث substage داخل processing
        substage = compute_substage(order)
        if substage == 'waiting_approval':
            order.current_stage_name = 'preparing'
        elif substage == 'preparing':
            order.current_stage_name = 'captain_received'
        elif substage == 'captain_received':
            order.status = 'out_for_delivery'
    elif current == 'out_for_delivery':
        order.status = 'delivered'
    elif current == 'deferred':
        # الطلبات المؤجلة تنتقل إلى processing
        order.status = 'processing'
        order.current_stage_name = 'waiting_approval'
    elif current == 'pickup':
        # الطلبات الاستلام الشخصي تنتقل إلى processing
        order.status = 'processing'
        order.current_stage_name = 'waiting_approval'
    
    await session.commit()
    await session.refresh(order)
    
    return serialize(order)

@router.patch("/{order_id}/cancel", response_model=Dict[str, Any])
async def cancel_order(order_id: int, session: AsyncSession = Depends(get_session)):
    """Cancel order and increment customer cancelled count."""
    result = await session.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Cancel the order
    order.status = 'cancelled'
    
    # Increment customer cancelled count
    if order.customer_id:
        try:
            await session.execute(
                sa_text(
                    "UPDATE customers SET cancelled_count = COALESCE(cancelled_count, 0) + 1 WHERE customer_id = :cid"
                ),
                {"cid": order.customer_id},
            )
        except Exception as e:
            # إذا كان العمود غير موجود أو حدث خطأ، نسجل فقط ولا نفشل العملية
            logging.getLogger(__name__).warning("cancelled_count update failed: %s", e)
    
    await session.commit()
    await session.refresh(order)
    
    return serialize(order)


@router.patch("/{order_id}/problem", response_model=Dict[str, Any])
async def mark_order_problem(order_id: int, session: AsyncSession = Depends(get_session)):
    """Mark order as problem (moves to 'problem' tab)."""
    result = await session.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Set status to problem
    order.status = 'problem'

    await session.commit()
    await session.refresh(order)

    return serialize(order)


@router.patch("/{order_id}", response_model=Dict[str, Any])
async def update_order_status(order_id: int, payload: Dict[str, Any] = Body(None), session: AsyncSession = Depends(get_session)):
    """Generic status update endpoint: expects {"status": "..."}."""
    result = await session.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    requested = normalize_status(payload.get("status")) if payload else None
    if not requested or requested not in VALID:
        raise HTTPException(status_code=422, detail="Invalid status")

    # Apply status
    order.status = requested

    # Initialize processing substage when moving into processing with no substage
    if requested == "processing" and not getattr(order, "current_stage_name", None):
        order.current_stage_name = "waiting_approval"

    await session.commit()
    await session.refresh(order)

    return serialize(order)


# Notes endpoints (order-scoped)
@router.get("/{order_id}/notes", response_model=List[Dict[str, Any]])
async def list_order_notes(order_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Note)
        .where(
            (Note.reference_id == order_id)
            & (Note.target_type == literal_column("'order'::note_target_enum"))
        )
        .order_by(Note.created_at.desc())
    )
    notes = result.scalars().all()
    return [
        {
            "note_id": n.note_id,
            "target_type": n.target_type,
            "reference_id": n.reference_id,
            "note_text": n.note_text,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "source": getattr(n, 'source', 'employee'),
        }
        for n in notes
    ]


@router.post("/{order_id}/notes", response_model=Dict[str, Any])
async def add_order_note(order_id: int, payload: Dict[str, Any] = Body(...), session: AsyncSession = Depends(get_session)):
    text = (payload or {}).get("note_text")
    source = (payload or {}).get("source") or 'employee'
    if not text or not isinstance(text, str) or not text.strip():
        raise HTTPException(status_code=422, detail="note_text is required")
    # Ensure order exists
    result = await session.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Insert with explicit cast to avoid enum/varchar mismatch
    ins = sa_text(
        """
        INSERT INTO notes(note_type, target_type, reference_id, note_text, source)
        VALUES (CAST(:nt AS note_type_enum), CAST(:t AS note_target_enum), :rid, :txt, :src)
        RETURNING note_id, created_at
        """
    )
    row = (await session.execute(ins, {"nt": "order", "t": "order", "rid": order_id, "txt": text.strip(), "src": source})).first()
    await session.commit()
    note_id, created_at = row[0], row[1]

    # إشعار تبويب مطابق لحالة الطلب الحالية
    try:
        result = await session.execute(select(Order).where(Order.order_id == order_id))
        ord2 = result.scalar_one_or_none()
        if ord2:
            tab = compute_current_status(ord2)
            payload = {"title": "تم حفظ الملاحظة", "message": f"تم حفظ الملاحظة للطلب #{order_id}", "order_id": order_id, "level": "success"}
            await notify_tab(tab, payload)
            try:
                await notify_tab2(tab, payload)
            except Exception:
                pass
    except Exception:
        pass
    return {
        "note_id": int(note_id),
        "target_type": "order",
        "reference_id": order_id,
        "note_text": text.strip(),
        "created_at": created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at),
        "source": source,
    }


@router.get("/notes/flags", response_model=Dict[int, bool])
async def notes_flags(ids: str = Query(default=""), session: AsyncSession = Depends(get_session)):
    """Return mapping of order_id -> has_notes for given comma-separated ids."""
    try:
        order_ids = [int(x) for x in ids.split(',') if x.strip().isdigit()]
    except Exception:
        order_ids = []
    if not order_ids:
        return {}
    q = (
        select(Note.reference_id, func.count().label('cnt'))
        .where(
            (Note.reference_id.in_(order_ids))
            & (Note.target_type == literal_column("'order'::note_target_enum"))
        )
        .group_by(Note.reference_id)
    )
    rows = (await session.execute(q)).all()
    flags: Dict[int, bool] = {oid: False for oid in order_ids}
    for ref_id, cnt in rows:
        flags[int(ref_id)] = int(cnt) > 0
    return flags


# Rating endpoints (order-scoped)
@router.get("/{order_id}/rating", response_model=Dict[str, Any])
async def get_order_rating(order_id: int, session: AsyncSession = Depends(get_session)):
    """Get rating for a specific order."""
    result = await session.execute(
        select(Rating)
        .where(Rating.order_id == order_id)
        .order_by(Rating.timestamp.desc())
        .limit(1)
    )
    rating = result.scalar_one_or_none()
    
    if not rating:
        return {"order_id": order_id, "rating": None}
    
    return {
        "order_id": order_id,
        "rating_id": rating.rating_id,
        "order_emoji_score": rating.order_emoji_score,
        "order_comment": rating.order_comment,
        "timestamp": rating.timestamp.isoformat() if rating.timestamp else None,
    }


@router.post("/{order_id}/rating", response_model=Dict[str, Any])
async def add_order_rating(order_id: int, payload: Dict[str, Any] = Body(...), session: AsyncSession = Depends(get_session)):
    """Add rating for a specific order."""
    rating_score = (payload or {}).get("rating")
    comment = (payload or {}).get("comment", "")
    
    if not rating_score or not isinstance(rating_score, int) or rating_score < 1 or rating_score > 5:
        raise HTTPException(status_code=422, detail="rating must be an integer between 1 and 5")
    
    # Ensure order exists
    result = await session.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if rating already exists for this order
    existing_result = await session.execute(
        select(Rating).where(Rating.order_id == order_id)
    )
    existing_rating = existing_result.scalar_one_or_none()
    
    if existing_rating:
        # Update existing rating
        existing_rating.order_emoji_score = rating_score
        existing_rating.order_comment = comment
        await session.commit()
        await session.refresh(existing_rating)
        
        rating_data = {
            "order_id": order_id,
            "rating_id": existing_rating.rating_id,
            "order_emoji_score": existing_rating.order_emoji_score,
            "order_comment": existing_rating.order_comment,
            "timestamp": existing_rating.timestamp.isoformat() if existing_rating.timestamp else None,
        }
    else:
        # Create new rating
        new_rating = Rating(
            order_id=order_id,
            order_emoji_score=rating_score,
            order_comment=comment
        )
        session.add(new_rating)
        await session.commit()
        await session.refresh(new_rating)
        
        rating_data = {
            "order_id": order_id,
            "rating_id": new_rating.rating_id,
            "order_emoji_score": new_rating.order_emoji_score,
            "order_comment": new_rating.order_comment,
            "timestamp": new_rating.timestamp.isoformat() if new_rating.timestamp else None,
        }
    
    # إشعار تبويب مطابق لحالة الطلب الحالية
    try:
        tab = compute_current_status(order)
        payload = {"title": "تم التقييم", "message": f"تم تقييم الطلب #{order_id} بـ {rating_score} نجوم", "order_id": order_id, "level": "success"}
        await notify_tab(tab, payload)
        try:
            await notify_tab2(tab, payload)
        except Exception:
            pass
    except Exception:
        pass
    
    return rating_data
