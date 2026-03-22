from flask_bcrypt import Bcrypt

# Utility script for generating bcrypt password hashes
# Use this to generate hashed passwords for manual SQL INSERT statements
# Run directly: python generate_hash.py

bcrypt = Bcrypt()

# Change this to the password you want to hash
password = "mypassword"

# Generate the bcrypt hash and decode to UTF-8 string
hashed = bcrypt.generate_password_hash(password).decode('utf-8')

print(f"\nYour bcrypt hash for '{password}':")
print(hashed)
print("\nUse this in your SQL INSERT statement")