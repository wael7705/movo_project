from .constants import OrderStatus


def compute_current_status(order) -> str:
    raw = getattr(order, "status", None)
    if hasattr(raw, "value"):
        raw = raw.value
    value = str(raw or "").strip().lower()
    if value in {"accepted", "captain_assigned", "choose_captain"}:
        return OrderStatus.choose_captain
    if value in {"waiting_approval", "preparing", "captain_received", "processing"}:
        return OrderStatus.processing
    if value == "out_for_delivery":
        return OrderStatus.out_for_delivery
    if value == "delivered":
        return OrderStatus.delivered
    if value == "cancelled":
        return OrderStatus.cancelled
    if value == "problem":
        return OrderStatus.problem
    return OrderStatus.pending


