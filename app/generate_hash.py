from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
password = "mypassword"
hashed = bcrypt.generate_password_hash(password).decode('utf-8')
print(f"\nYour bcrypt hash for '{password}':")
print(hashed)
print("\nUse this in your SQL INSERT statement")