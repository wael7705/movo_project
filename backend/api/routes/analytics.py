from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import List, Dict, Any

from core.db import get_session
from models.order import Order
from models.customer import Customer

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/forecast", response_model=Dict[str, Any])
async def forecast(
    hours: int = Query(default=24, ge=1, le=168),
    session: AsyncSession = Depends(get_session),
):
    # توقع بسيط: تجميع عدد الطلبات في كل ساعة خلال آخر N ساعات
    bucket = func.date_trunc('hour', Order.created_at).label('bucket')
    q = (
        select(bucket, func.count().label('cnt'))
        .where(Order.created_at >= func.now() - text(f"INTERVAL '{hours} hours'"))
        .group_by(bucket)
        .order_by(bucket)
    )
    rows = (await session.execute(q)).all()
    series = [{"ts": r[0].isoformat() if hasattr(r[0], 'isoformat') else str(r[0]), "count": int(r[1])} for r in rows]

    # متوسط متحرك بسيط لتنعيم السلسلة (نافذة 3)
    smooth: List[Dict[str, Any]] = []
    for i in range(len(series)):
        vals = [series[j]["count"] for j in range(max(0, i - 1), min(len(series), i + 2))]
        smooth.append({"ts": series[i]["ts"], "count": series[i]["count"], "ma3": round(sum(vals) / len(vals), 2)})

    return {"hours": hours, "series": smooth}


@router.get("/anomalies", response_model=Dict[str, Any])
async def anomalies(session: AsyncSession = Depends(get_session)):
    # كشف مبسط: 
    # 1) إذا كان عدد الطلبات في آخر ساعة أعلى من متوسط آخر 24 ساعة + 2*الانحراف المعياري
    bucket = func.date_trunc('hour', Order.created_at).label('bucket')
    last24 = (
        select(bucket, func.count().label('cnt'))
        .where(Order.created_at >= func.now() - text("INTERVAL '24 hours'"))
        .group_by(bucket)
        .order_by(bucket)
    )
    rows = (await session.execute(last24)).all()
    counts = [int(r[1]) for r in rows]
    latest = counts[-1] if counts else 0
    mean = (sum(counts) / len(counts)) if counts else 0
    var = (sum((c - mean) ** 2 for c in counts) / len(counts)) if counts else 0
    std = var ** 0.5
    traffic_spike = latest > (mean + 2 * std) if counts else False

    # 2) الطلبات العالقة في processing لأكثر من ساعتين
    stuck_q = select(func.count()).where(
        (Order.status == 'processing') & (Order.created_at < func.now() - text("INTERVAL '2 hours'"))
    )
    stuck = int((await session.execute(stuck_q)).scalar() or 0)

    return {
        "latest_hour": latest,
        "mean_24h": round(mean, 2),
        "std_24h": round(std, 2),
        "traffic_spike": traffic_spike,
        "stuck_processing_gt2h": stuck,
    }


@router.get("/insights/order/{order_id}", response_model=Dict[str, Any])
async def order_insights(order_id: int, session: AsyncSession = Depends(get_session)):
    """تحليلات مبسطة لعرض ملاحظات/تنبيهات AI حول الطلب."""
    result = await session.execute(select(Order).where(Order.order_id == order_id))
    order: Order | None = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    cust: Customer | None = None
    if order.customer_id:
        cres = await session.execute(select(Customer).where(Customer.customer_id == order.customer_id))
        cust = cres.scalar_one_or_none()

    insights: List[str] = []

    # قواعد مبسطة كمؤشرات أولية
    if cust and getattr(cust, "cancelled_count", 0) >= 3:
        insights.append("العميل لديه سجل إلغاءات مرتفع؛ راقب سبب الإلغاء وتواصل مبكرًا.")
    if getattr(order, "distance_meters", 0) and getattr(order, "delivery_fee", 0):
        km = float(order.distance_meters or 0) / 1000.0
        fee = float(order.delivery_fee or 0)
        if km > 5 and fee < 6:
            insights.append("المسافة طويلة والرسوم منخفضة نسبيًا؛ قد يتأخر التسليم أو يرفضه الكابتن.")
    if getattr(order, "status", "") == "processing":
        insights.append("الطلب في المعالجة؛ تحقق من زمن كل مرحلة لتجنّب التأخير.")
    if getattr(order, "status", "") == "problem":
        insights.append("الطلب مُصنّف مشكلة؛ وثّق السبب واتخذ إجراءً تصحيحيًا.")

    # fallback إذا لم تُستنتج أي ملاحظة
    if not insights:
        insights.append("لا توجد ملاحظات حرجة حسب القواعد الحالية.")

    return {"order_id": order_id, "insights": insights}
