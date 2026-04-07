import secrets
import string

# Generate secure secret key
secret_key = secrets.token_urlsafe(32)
print(f"SECRET_KEY={secret_key}")

# Generate additional secure keys
print(f"\nAdditional security keys:")
for i in range(3):
    print(f"SECRET_KEY_{i+1}={secrets.token_urlsafe(32)}")
