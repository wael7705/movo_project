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
	"waiting_restaurant_acceptance": "choose_captain",
	"preparing": "processing",
	"pick_up_ready": "processing",
}

VALID: set[str] = {
	"pending", "choose_captain", "processing", "out_for_delivery", "delivered", 
	"cancelled", "problem"
}


def normalize(value: str | None) -> str | None:
	if not value:
		return None
	v = value.strip().lower()
	return ALIASES.get(v, v)
