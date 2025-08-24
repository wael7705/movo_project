from typing import Optional

# status هو مصدر الحقيقة الوحيد للحالة
VALID = {"pending", "choose_captain", "processing", "out_for_delivery", "delivered", "cancelled", "problem", "deferred", "pickup"}

# خريطة الحالات القديمة إلى الجديدة
ALIASES = {
    "issue": "problem",
    "accepted": "choose_captain",
    "waiting_restaurant_acceptance": "choose_captain",
    "preparing": "processing",
    "pick_up_ready": "processing",
}

def normalize_status(status: str | None) -> str:
    """تطبيع الحالة: lowercase, trim, apply aliases."""
    if not status:
        return "pending"
    s = status.strip().lower()
    return ALIASES.get(s, s)

def compute_current_status(o) -> str:
    """Compute the normalized current_status from the raw status."""
    s = (getattr(o, "status", "") or "").strip().lower()
    normalized = normalize_status(s)
    return normalized if normalized in VALID else "pending"

def compute_substage(o) -> Optional[str]:
    """Compute substage for processing orders. Returns None for non-processing orders."""
    if compute_current_status(o) != "processing":
        return None
    
    # للطلبات في حالة processing، نرجع substage بناءً على current_stage_name
    stage_name = getattr(o, "current_stage_name", "").strip().lower()
    
    # إذا لم يكن هناك current_stage_name، نرجع waiting_approval كافتراضي
    if not stage_name:
        return "waiting_approval"
    
    # تحديد substage بناءً على current_stage_name
    if stage_name in ["waiting_approval", "waiting_restaurant_acceptance", "accepted"]:
        return "waiting_approval"
    elif stage_name in ["preparing", "preparation", "in_preparation"]:
        return "preparing"
    elif stage_name in ["captain_received", "ready_for_pickup", "ready_for_captain"]:
        return "captain_received"
    else:
        # افتراضي: انتظار الموافقة
        return "waiting_approval"
