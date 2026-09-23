import os

# Set fallback environment variables for test execution
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only-32bytes!")
