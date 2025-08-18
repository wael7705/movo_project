# Status System Implementation - Single Active Status Contract

## Overview

This implementation enforces a single active status contract for orders, preventing them from appearing in multiple tabs and ensuring consistent status management throughout the system.

## Key Changes Made

### 1. Database Schema Updates

#### Migration File: `alembic/versions/001_enforce_status_enum_and_normalize.py`

- **Status Normalization**: Converts existing data to lowercase and maps old status values
- **Enum Constraint**: Adds strict CHECK constraint for valid status values
- **Trigger Function**: Creates `trg_orders_normalize_status()` to automatically normalize status on insert/update
- **Helper Field**: Adds `is_deferred` boolean field for pending→processing jumps
- **Indexes**: Creates performance indexes on status and created_at

#### Database Schema: `database.sql`

- **Updated Enum**: Changed `order_status_enum` to use simplified values
- **Added Field**: Added `is_deferred` field to orders table
- **Updated Triggers**: Modified `handle_scheduled_order()` to use new status values

### 2. Backend Code Updates

#### Status Module: `backend/core/status.py`

```python
VALID = {"pending", "choose_captain", "processing", "out_for_delivery", "delivered", "cancelled", "problem"}

ALIASES = {
    "issue": "problem",
    "accepted": "choose_captain",
    "waiting_restaurant_acceptance": "choose_captain", 
    "preparing": "processing",
    "pick_up_ready": "processing",
}
```

#### Order Model: `backend/models/order.py`

- **Simplified Enum**: Uses only the 7 core status values
- **Added Field**: Includes `is_deferred` boolean field

#### Orders API: `backend/api/routes/orders.py`

- **Status Filtering**: Filters exclusively on `current_status` (computed from `status`)
- **Demo Creation**: Always creates orders with `pending` status
- **Status Transitions**: Implements proper next() flow with deferred jump support
- **Cancellation**: Updates customer cancelled count

### 3. Status Flow

```
pending → choose_captain → processing → out_for_delivery → delivered
   ↓           ↓
(deferred)  (captain assigned)
   ↓
processing (jump)
```

## New Status Values

| Status | Description | Tab Display |
|--------|-------------|-------------|
| `pending` | Order created, waiting for processing | Pending Tab |
| `choose_captain` | Captain selection phase | Captain Selection Tab |
| `processing` | Order being prepared | Processing Tab |
| `out_for_delivery` | Order in transit | Delivery Tab |
| `delivered` | Order completed | Delivered Tab |
| `cancelled` | Order cancelled | Cancelled Tab |
| `problem` | Order has issues | Problem Tab |

## Key Features

### 1. Single Active Status
- Each order appears in exactly one tab
- `status` field is the single source of truth
- No duplicate appearances across tabs

### 2. Automatic Normalization
- Trigger automatically normalizes status on insert/update
- Handles legacy status values gracefully
- Prevents invalid status values

### 3. Deferred Order Support
- `is_deferred` flag allows pending→processing jumps
- Useful for orders that don't need captain selection
- Maintains proper status flow

### 4. Consistent Filtering
- All status filtering uses `current_status`
- No dependency on other fields for tab determination
- Clean separation between status and substage

## Migration Steps

### 1. Run the Migration
```bash
alembic upgrade head
```

### 2. Verify Data
```bash
# Check that all orders have valid status values
SELECT DISTINCT status FROM orders;

# Verify no orders appear in multiple tabs
SELECT order_id, status, current_status FROM orders LIMIT 10;
```

### 3. Test API Endpoints
```bash
# Test demo creation
POST /api/v1/orders/demo

# Test status filtering
GET /api/v1/orders?order_status=pending
GET /api/v1/orders?order_status=processing

# Test status transitions
PATCH /api/v1/orders/{id}/next
PATCH /api/v1/orders/{id}/cancel
```

## Testing

### 1. Automated Tests
Run the test script to verify implementation:
```bash
python test_status_system.py
```

### 2. Manual Testing
- Create demo orders and verify they appear only in Pending tab
- Test status transitions and verify tab changes
- Verify no duplicate orders across tabs
- Test deferred order functionality

## Benefits

### 1. Data Consistency
- Single source of truth for order status
- No conflicting status indicators
- Consistent tab behavior

### 2. Performance
- Optimized indexes on status fields
- Efficient filtering and queries
- Reduced complexity in status logic

### 3. Maintainability
- Simplified status system
- Clear status flow
- Easy to extend and modify

### 4. User Experience
- Orders appear in exactly one tab
- Clear status progression
- Consistent interface behavior

## Troubleshooting

### Common Issues

1. **Migration Fails**: Check database connection and permissions
2. **Status Mismatch**: Verify enum values match between model and database
3. **Trigger Errors**: Check PostgreSQL logs for trigger function errors
4. **API Errors**: Verify status values in requests match new enum

### Debug Commands

```sql
-- Check current status distribution
SELECT status, COUNT(*) FROM orders GROUP BY status;

-- Verify trigger function exists
SELECT * FROM information_schema.triggers WHERE trigger_name = 'orders_normalize_status';

-- Check constraint
SELECT * FROM information_schema.check_constraints WHERE constraint_name = 'orders_status_check';
```

## Future Enhancements

1. **Status History**: Track status changes over time
2. **Status Rules**: Configurable status transition rules
3. **Status Notifications**: Real-time status change notifications
4. **Status Analytics**: Performance metrics by status

## Conclusion

This implementation provides a robust, maintainable status system that ensures orders appear in exactly one tab while maintaining flexibility for different order types and workflows. The system is designed to be easily extensible and provides a solid foundation for future enhancements.
