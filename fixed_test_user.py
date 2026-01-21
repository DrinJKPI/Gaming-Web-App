from app import create_app, db, bcrypt
from app.models import User

app = create_app()

with app.app_context():
    # Delete old test user
    old_user = User.query.filter_by(email='test@test.com').first()
    if old_user:
        db.session.delete(old_user)
        db.session.commit()
        print("Deleted old test user")

    # Create new test user with proper hash
    password = "mypassword"
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')

    print(f"Generated hash: {hashed}")
    print(f"Hash length: {len(hashed)}")

    new_user = User(
        username='testuser',
        email='test@test.com',
        password_hash=hashed,
        is_active=True
    )

    db.session.add(new_user)
    db.session.commit()

    print(f"Created user: {new_user.username} (ID: {new_user.user_id})")

    # Verify it was saved correctly
    verify_user = User.query.filter_by(email='test@test.com').first()
    print(f"\nVerification:")
    print(f"  Email: {verify_user.email}")
    print(f"  Hash from DB: {verify_user.password_hash}")
    print(f"  Hash length from DB: {len(verify_user.password_hash)}")

    # Test password check
    print(f"\n  Testing password check...")
    try:
        result = bcrypt.check_password_hash(verify_user.password_hash, password)
        print(f"  Password check result: {result}")
    except Exception as e:
        print(f"  Password check failed: {e}")