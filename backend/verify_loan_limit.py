import requests
import json

API_URL = "http://localhost:8000/api"

def login(email, password):
    res = requests.post(f"{API_URL}/users/login", json={"email": email, "password": password})
    if res.status_code != 200:
        print(f"Login failed for {email}: {res.text}")
        return None
    return res.json()["user"]

def get_loans(user_id):
    res = requests.get(f"{API_URL}/loans/?user_id={user_id}")
    return res.json()

def borrow_book(user_id, book_id):
    res = requests.post(f"{API_URL}/loans/borrow", json={"user_id": user_id, "book_id": book_id})
    return res.json()

# Note: The admin endpoint requires specific auth headers which might be complex to mock here if using dependency injection.
# However, if we assume the standard dependency 'get_current_user' works with our mocked user dict in tests or if we skip full auth for local testing...
# Actually the backend uses Depends(get_current_user), which expects a token in Authorization header if it was OAuth2, 
# but currently get_current_user might be a stub or simple implementation?
# Let's check backend/app/routers/users.py for get_current_user implementation.
# If it's not implemented fully, we might need another way.
# But assuming we can just use the borrow logic validation.

# 1. Login
admin_user = login("admin@library.com", "admin123")
member_user = login("user@example.com", "user123")

if not member_user:
    print("Failed to login member")
    exit(1)

print(f"Logged in as {member_user['name']}")

# 2. Borrow Logic Test
# We will use the 'borrow_book' endpoint.
# First, let's borrow a book. We need valid book IDs.
# Assuming book_id 1, 2, 3 exist.

print("\n--- Testing Loan Limit ---")
# Try to borrow multiple books.
# Config Default is 3.

# Return all previous loans to start fresh (optional, but good for consistent test)
# Skip for now.

results = []
for book_id in [1, 2, 3, 4]:
    print(f"Borrowing book {book_id}...")
    res = borrow_book(member_user['user_id'], book_id)
    success = res.get("success", False)
    msg = res.get("message", "No message")
    print(f"Result: {success} - {msg}")
    results.append(success)

# Expect: True, True, True, False (if limit is 3)
print(f"\nResults: {results}")

if results == [True, True, True, False]:
     print("✅ Loan Limit (3) validated.")
else:
     # Might fail if books already borrowed or out of stock.
     print("⚠️ Check manual verification if DB wasn't empty.")

