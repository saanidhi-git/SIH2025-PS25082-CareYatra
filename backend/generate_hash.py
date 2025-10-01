import hashlib

def hash_password(password: str) -> str:
    """Return a SHA256 hash of the password."""
    return hashlib.sha256(password.encode()).hexdigest()

# Change 'mysecretpass' to any password you want to use for testing.
plain_text_password = 'testpass'
new_hash = hash_password(plain_text_password)

print(f"Plain text password: {plain_text_password}")
print(f"Generated hash: {new_hash}")
