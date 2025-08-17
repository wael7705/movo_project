from enum import Enum


class OrderStatus(str, Enum):
    pending = "pending"
    choose_captain = "choose_captain"
    processing = "processing"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"
    problem = "problem"


LIFECYCLE: list[str] = [
    OrderStatus.pending,
    OrderStatus.choose_captain,
    OrderStatus.processing,
    OrderStatus.out_for_delivery,
    OrderStatus.delivered,
]


ALIASES: dict[str, str] = {
    "issue": "problem",
    "accepted": "choose_captain",
    "captain_assigned": "choose_captain",
}


VALID: set[str] = set(s.value if isinstance(s, OrderStatus) else s for s in OrderStatus)


def normalize(value: str | None) -> str | None:
    if not value:
        return None
    v = value.strip().lower()
    return ALIASES.get(v, v)


