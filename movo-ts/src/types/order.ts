export type OrderStatus =
    | 'pending'
    | 'captain_assigned'
    | 'processing'
    | 'delayed'
    | 'out_for_delivery'
    | 'delivered'
    | 'cancelled'
    | 'issue';
export interface Order {
    id: string;
    trackId: string;
    customerName: string;
    restaurantName: string;
    paymentMethod: string;
    deliveryMethod: string;
    status: OrderStatus;
    isVip?: boolean;
    isFirstOrder?: boolean;
    pickup?: boolean;
    createdAt: string;
    acceptedAt?: string;
    preparedAt?: string;
    outForDeliveryAt?: string;
    deliveredAt?: string;
    delayedReason?: string;
    issueReason?: string;
    notes?: string;
    rating?: number;      // emoji or number (1-5)
    address?: string;
    captainName?: string;
    captainPhone?: string;
}
export interface OrderSection {
    title: string;
    status: OrderStatus;
    orders: Order[];
}