import json
import os

users_file = r"c:\Users\HP\OneDrive\Desktop\New folder\backend\data\users.json"

if not os.path.exists(users_file):
    print("File not found")
    exit()

with open(users_file, "r") as f:
    users = json.load(f)

emails = {}
duplicates = []

for u in users:
    email = u.get("email", "").lower()
    if email in emails:
        duplicates.append((email, u.get("role"), emails[email]))
    emails[email] = u.get("role")

if duplicates:
    print("Found duplicate emails:")
    for email, role1, role2 in duplicates:
        print(f"Email: {email} | Role 1: {role1} | Role 2: {role2}")
else:
    print("No duplicate emails found")
