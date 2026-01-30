import json
import urllib.request
import urllib.error
import sys
import time

API_URL = "http://localhost:8000/api"

def make_request(method, url, data=None, headers={}):
    req = urllib.request.Request(url, method=method)
    for k, v in headers.items():
        req.add_header(k, v)
    
    if data:
        req.add_header('Content-Type', 'application/json')
        req.data = json.dumps(data).encode('utf-8')
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code} for {method} {url}: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# 1. Login to get User IDs
print("Logging in...")
# Try admin123 first (if seed used it) or admin1234 (if changed manually)
admin = make_request("POST", f"{API_URL}/users/login", {"email": "admin@library.com", "password": "admin1234"})
if not admin:
    admin = make_request("POST", f"{API_URL}/users/login", {"email": "admin@library.com", "password": "admin123"})

if not admin:
    print("Admin login failed. Check password or seed.")
    sys.exit(1)

admin_id = admin['user']['user_id']
print(f"Logged in as Admin (ID: {admin_id})")

member_email = f"verify_test_{int(time.time())}@example.com"
member = make_request("POST", f"{API_URL}/users/login", {"email": member_email, "password": "user123"})
if not member:
    print(f"Creating verification member {member_email}...")
    member_user = make_request("POST", f"{API_URL}/users/", {
        "email": member_email, "password": "user123", "name": "Verify User", "role": "MEMBER"
    })
    if not member_user:
        print("Failed to create member")
        sys.exit(1)
    member_id = member_user['user_id']
else:
    member_id = member['user']['user_id']

print(f"Member ID: {member_id}")

# 2. Set Config (Limit 2)
print("\n--- Setting Loan Limit to 2 ---")
res = make_request("PUT", f"{API_URL}/admin/config/max_loan_limit", {"value": "2"}, {"x-user-id": str(admin_id)})
if res:
    print(f"Config updated: {res['value']}")

# 3. Borrow Books
print("\n--- Borrowing Books ---")
# Need Book IDs. Listing books.
books = make_request("GET", f"{API_URL}/books/")
if not books:
    print("Failed to fetch books")
    sys.exit(1)

book_ids = [b['book_id'] for b in books if b['stock_quantity'] > 0]
print(f"Available books: {len(book_ids)}")

if len(book_ids) < 3:
    print("Not enough books to test limit. Need at least 3 available.")
    sys.exit(1)

target_books = book_ids[:3]

# Borrow 1
print(f"Borrowing book {target_books[0]}...")
res1 = make_request("POST", f"{API_URL}/loans/borrow", {"user_id": member_id, "book_id": target_books[0]})
print(f"Result 1: {res1.get('success') if res1 else 'Failed'} - {res1.get('message', '') if res1 else ''}")

# Borrow 2
print(f"Borrowing book {target_books[1]}...")
res2 = make_request("POST", f"{API_URL}/loans/borrow", {"user_id": member_id, "book_id": target_books[1]})
print(f"Result 2: {res2.get('success') if res2 else 'Failed'} - {res2.get('message', '') if res2 else ''}")

# Borrow 3 (Should Fail)
print(f"Borrowing book {target_books[2]} (Should Fail)...")
res3 = make_request("POST", f"{API_URL}/loans/borrow", {"user_id": member_id, "book_id": target_books[2]})
if res3 and not res3.get('success'):
    print(f"✅ Successfully blocked: {res3.get('message')}")
else:
    print(f"❌ Failed to block (Unexpected success): {res3}")

# 4. Set Config (Limit 3)
print("\n--- Setting Loan Limit to 3 ---")
res = make_request("PUT", f"{API_URL}/admin/config/max_loan_limit", {"value": "3"}, {"x-user-id": str(admin_id)})
if res:
    print(f"Config updated: {res['value']}")

# Borrow 3 (Should Succeed)
print(f"Borrowing book {target_books[2]} (Should Succeed)...")
res4 = make_request("POST", f"{API_URL}/loans/borrow", {"user_id": member_id, "book_id": target_books[2]})
if res4 and res4.get('success'):
    print("✅ Successfully borrowed (Limit increased)")
else:
    print(f"❌ Failed to borrow (Limit increase issue): {res4.get('message')}")
