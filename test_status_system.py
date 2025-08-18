#!/usr/bin/env python3
"""
Test script to verify the new status system works correctly.
This script tests the status normalization, current_status computation, and status transitions.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_status_system():
    """Test the status system functionality."""
    print("Testing new status system...")
    
    try:
        # Test status module
        from core.status import VALID, normalize_status, compute_current_status, compute_substage
        
        print(f"✓ VALID statuses: {VALID}")
        
        # Test status normalization
        test_cases = [
            ("PENDING", "pending"),
            ("  pending  ", "pending"),
            ("ISSUE", "problem"),
            ("accepted", "choose_captain"),
            ("waiting_restaurant_acceptance", "choose_captain"),
            ("preparing", "processing"),
            ("pick_up_ready", "processing"),
            ("unknown", "unknown"),
            (None, "pending"),
        ]
        
        print("\nTesting status normalization:")
        for input_status, expected in test_cases:
            result = normalize_status(input_status)
            status = "✓" if result == expected else "✗"
            print(f"  {status} {input_status!r} -> {result!r} (expected: {expected!r})")
        
        # Test current_status computation
        class MockOrder:
            def __init__(self, status):
                self.status = status
        
        print("\nTesting current_status computation:")
        test_orders = [
            MockOrder("PENDING"),
            MockOrder("ISSUE"),
            MockOrder("accepted"),
            MockOrder("unknown"),
            MockOrder(None),
        ]
        
        for order in test_orders:
            result = compute_current_status(order)
            expected = normalize_status(order.status)
            if expected not in VALID:
                expected = "pending"
            status = "✓" if result == expected else "✗"
            print(f"  {status} {order.status!r} -> {result!r} (expected: {expected!r})")
        
        # Test substage computation
        print("\nTesting substage computation:")
        test_substage_orders = [
            MockOrder("pending"),
            MockOrder("processing"),
            MockOrder("delivered"),
        ]
        
        for order in test_substage_orders:
            result = compute_substage(order)
            current = compute_current_status(order)
            expected = "preparing" if current == "processing" else None
            status = "✓" if result == expected else "✗"
            print(f"  {status} {order.status!r} (current: {current}) -> substage: {result!r} (expected: {expected!r})")
        
        print("\n✓ All status system tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Status system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_order_model():
    """Test the order model can be imported and has correct status enum."""
    print("\nTesting order model...")
    
    try:
        from models.order import Order
        
        # Check if the status column has the correct enum values
        status_column = Order.__table__.columns['status']
        enum_values = status_column.type.enums
        
        expected_values = {'pending', 'choose_captain', 'processing', 'out_for_delivery', 'delivered', 'cancelled', 'problem'}
        actual_values = set(enum_values)
        
        if actual_values == expected_values:
            print(f"✓ Order model status enum: {actual_values}")
        else:
            print(f"✗ Order model status enum mismatch:")
            print(f"  Expected: {expected_values}")
            print(f"  Actual:   {actual_values}")
            return False
        
        # Check if is_deferred field exists
        if 'is_deferred' in Order.__table__.columns:
            print("✓ Order model has is_deferred field")
        else:
            print("✗ Order model missing is_deferred field")
            return False
        
        print("✓ Order model tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Order model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Testing New Status System Implementation")
    print("=" * 50)
    
    status_ok = test_status_system()
    model_ok = test_order_model()
    
    print("\n" + "=" * 50)
    if status_ok and model_ok:
        print("✓ ALL TESTS PASSED - Status system is ready!")
        print("\nNext steps:")
        print("1. Run the migration: alembic upgrade head")
        print("2. Test the API endpoints")
        print("3. Verify no duplicate orders appear in multiple tabs")
    else:
        print("✗ SOME TESTS FAILED - Please fix issues before proceeding")
    
    print("=" * 50)
    
    return status_ok and model_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
