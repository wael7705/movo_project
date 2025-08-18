#!/usr/bin/env python3
"""
Script to check database schema and add missing columns directly.
"""

import asyncio
import asyncpg
import os

async def check_and_fix_database():
    """Check database schema and add missing columns."""
    
    # Database connection string
    DATABASE_URL = "postgresql://postgres:movo2025@localhost:5432/movo_system"
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database successfully")
        
        # Check orders table columns
        print("\n🔍 Checking orders table columns...")
        orders_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'orders' 
            ORDER BY ordinal_position
        """)
        
        print("Orders table columns:")
        for col in orders_columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # Check customers table columns
        print("\n🔍 Checking customers table columns...")
        customers_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'customers' 
            ORDER BY ordinal_position
        """)
        
        print("Customers table columns:")
        for col in customers_columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # Add missing columns if they don't exist
        print("\n🔧 Adding missing columns...")
        
        # Check if current_stage_name exists in orders
        current_stage_exists = await conn.fetchval("""
            SELECT EXISTS(
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'orders' AND column_name = 'current_stage_name'
            )
        """)
        
        if not current_stage_exists:
            print("  - Adding current_stage_name to orders table...")
            await conn.execute("""
                ALTER TABLE orders ADD COLUMN current_stage_name VARCHAR(50)
            """)
            print("    ✅ Added current_stage_name")
        else:
            print("  - current_stage_name already exists")
        
        # Check if cancel_count_per_day exists in orders
        cancel_count_exists = await conn.fetchval("""
            SELECT EXISTS(
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'orders' AND column_name = 'cancel_count_per_day'
            )
        """)
        
        if not cancel_count_exists:
            print("  - Adding cancel_count_per_day to orders table...")
            await conn.execute("""
                ALTER TABLE orders ADD COLUMN cancel_count_per_day INTEGER DEFAULT 0
            """)
            print("    ✅ Added cancel_count_per_day")
        else:
            print("  - cancel_count_per_day already exists")
        
        # Check if cancelled_count exists in customers
        cancelled_count_exists = await conn.fetchval("""
            SELECT EXISTS(
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'customers' AND column_name = 'cancelled_count'
            )
        """)
        
        if not cancelled_count_exists:
            print("  - Adding cancelled_count to customers table...")
            await conn.execute("""
                ALTER TABLE customers ADD COLUMN cancelled_count INTEGER DEFAULT 0
            """)
            print("    ✅ Added cancelled_count")
        else:
            print("  - cancelled_count already exists")
        
        # Check if is_deferred exists in orders
        is_deferred_exists = await conn.fetchval("""
            SELECT EXISTS(
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'orders' AND column_name = 'is_deferred'
            )
        """)
        
        if not is_deferred_exists:
            print("  - Adding is_deferred to orders table...")
            await conn.execute("""
                ALTER TABLE orders ADD COLUMN is_deferred BOOLEAN DEFAULT FALSE
            """)
            print("    ✅ Added is_deferred")
        else:
            print("  - is_deferred already exists")
        
        print("\n✅ Database schema check and fix completed!")
        
        # Final check
        print("\n🔍 Final check of orders table columns...")
        final_orders_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'orders' 
            ORDER BY ordinal_position
        """)
        
        print("Final orders table columns:")
        for col in final_orders_columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        await conn.close()
        print("\n🎉 Database connection closed successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_and_fix_database())
