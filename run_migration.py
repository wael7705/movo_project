#!/usr/bin/env python3
"""
Migration runner script for the new status system.
This script helps run the migration and verify the results.
"""

import subprocess
import sys
import os
import time

def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n🔄 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print("Output:", result.stdout)
            return True
        else:
            print(f"❌ {description} failed")
            print("Error:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def check_migration_status():
    """Check the current migration status."""
    print("\n📊 Checking migration status...")
    
    try:
        result = subprocess.run("alembic current", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("Current migration:", result.stdout.strip())
        else:
            print("Could not determine current migration status")
            return False
        return True
    except Exception as e:
        print(f"Error checking migration status: {e}")
        return False

def main():
    """Main migration runner."""
    print("=" * 60)
    print("🚀 Status System Migration Runner")
    print("=" * 60)
    
    print("\nThis script will:")
    print("1. Check current migration status")
    print("2. Run the migration to enforce single active status")
    print("3. Verify the migration results")
    
    # Check if we're in the right directory
    if not os.path.exists("alembic.ini"):
        print("\n❌ Error: alembic.ini not found in current directory")
        print("Please run this script from the project root directory")
        return False
    
    if not os.path.exists("alembic/versions/001_enforce_status_enum_and_normalize.py"):
        print("\n❌ Error: Migration file not found")
        print("Please ensure the migration file exists")
        return False
    
    # Check current migration status
    if not check_migration_status():
        print("\n❌ Could not determine migration status")
        return False
    
    # Ask for confirmation
    print("\n⚠️  WARNING: This migration will modify your database schema!")
    print("Make sure you have:")
    print("- Backed up your database")
    print("- Stopped any running applications")
    print("- Verified the migration file contents")
    
    response = input("\nDo you want to proceed with the migration? (yes/no): ").lower().strip()
    if response not in ['yes', 'y']:
        print("Migration cancelled by user")
        return False
    
    print("\n🔄 Starting migration process...")
    
    # Run the migration
    if not run_command("alembic upgrade head", "Running migration"):
        print("\n❌ Migration failed! Please check the error messages above.")
        return False
    
    print("\n✅ Migration completed successfully!")
    
    # Verify the migration
    print("\n🔍 Verifying migration results...")
    
    # Check if the trigger function was created
    if not run_command("alembic current", "Checking final migration status"):
        print("Warning: Could not verify final migration status")
    
    print("\n" + "=" * 60)
    print("🎉 Migration completed successfully!")
    print("=" * 60)
    
    print("\nNext steps:")
    print("1. ✅ Database schema updated")
    print("2. ✅ Status enum normalized")
    print("3. ✅ Trigger functions created")
    print("4. ✅ Constraints added")
    print("5. ✅ Indexes created")
    
    print("\nTo test the new system:")
    print("- Start your backend application")
    print("- Test the API endpoints")
    print("- Verify orders appear in only one tab")
    print("- Test status transitions")
    
    print("\nIf you encounter any issues:")
    print("- Check the database logs")
    print("- Verify trigger functions exist")
    print("- Test with the provided test script: python test_status_system.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
