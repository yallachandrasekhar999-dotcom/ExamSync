import enum
from pydantic import BaseModel

class UserRole(str, enum.Enum):
    student = "student"
    author = "author"
    admin = "admin"

class User(BaseModel):
    role: UserRole

def test_require_role(user_role_str, allowed_roles):
    current_user = User(role=user_role_str)
    
    # Logic from auth.py
    user_role = str(current_user.role.value if hasattr(current_user.role, 'value') else current_user.role).lower()
    allowed_list = [str(r).lower() for r in allowed_roles]
    
    print(f"User Role String: '{user_role_str}'")
    print(f"Extracted Role Object: {current_user.role} (type: {type(current_user.role)})")
    print(f"Processed user_role: '{user_role}'")
    print(f"Allowed list: {allowed_list}")
    
    if user_role not in allowed_list:
        print("FAIL: Permission Denied")
    else:
        print("PASS: Permission Granted")

print("--- Testing 'admin' ---")
test_require_role("admin", ["admin"])

print("\n--- Testing 'author' ---")
test_require_role("author", ["admin"])
