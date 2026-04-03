"""
Create admin user for Legal Tech Platform
Run this script to create the first admin user
"""

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from datetime import datetime

def create_admin():
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@legaltech.com").first()
        
        if existing_admin:
            print("❌ Admin user already exists!")
            print(f"   Email: {existing_admin.email}")
            return
        
        # Create admin user
        admin = User(
            email="admin@legaltech.com",
            full_name="System Administrator",
            full_name_ar="مدير النظام",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=True,
            created_at=datetime.utcnow()
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("✅ Admin user created successfully!")
        print(f"\n📧 Email: admin@legaltech.com")
        print(f"🔑 Password: admin123")
        print(f"\n⚠️  IMPORTANT: Change this password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Creating admin user for Legal Tech Platform...")
    print("=" * 50)
    create_admin()
    print("=" * 50)
