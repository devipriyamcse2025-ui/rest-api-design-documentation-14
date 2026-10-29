# Practical REST API Usage Examples
**Project:** REST API Design and Documentation Kit (Capstone 48)  
**Base Server URL:** `http://127.0.0.1:8000`  

This document provides ready-to-run API invocation examples across three popular environments:
1. **cURL** (Cross-platform CLI)
2. **PowerShell** (Windows native CLI)
3. **Python `requests`** (Client programming)

---

## 1. Health & Status Probe

### cURL
```bash
curl -X GET "http://127.0.0.1:8000/health" -H "Accept: application/json"
```

### PowerShell
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
```

### Python
```python
import requests

resp = requests.get("http://127.0.0.1:8000/health")
print(resp.status_code, resp.json())
```

---

## 2. List Books with Pagination & Search

### cURL
```bash
# Get first 5 books matching 'clean'
curl -X GET "http://127.0.0.1:8000/api/v1/books?limit=5&offset=0&search=clean" \
     -H "Accept: application/json"
```

### PowerShell
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/books?limit=5&offset=0&search=clean" -Method Get
```

### Python
```python
import requests

params = {"limit": 5, "offset": 0, "search": "clean"}
resp = requests.get("http://127.0.0.1:8000/api/v1/books", params=params)
data = resp.json()
print(f"Total matching books: {data['total']}")
for book in data["items"]:
    print(f"- [{book['id']}] {book['title']} by {book['author']} (Available: {book['available_copies']}/{book['total_copies']})")
```

---

## 3. Retrieve Single Book by ID

### cURL
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/books/1" -H "Accept: application/json"
```

### PowerShell
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/books/1" -Method Get
```

### Python
```python
import requests

resp = requests.get("http://127.0.0.1:8000/api/v1/books/1")
if resp.status_code == 200:
    print("Book found:", resp.json())
else:
    print("Error:", resp.json())
```

---

## 4. Create a New Book (POST)

### cURL
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/books" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Structure and Interpretation of Computer Programs",
       "author": "Harold Abelson, Gerald Jay Sussman",
       "isbn": "978-0262510875",
       "publication_year": 1996,
       "total_copies": 3
     }'
```

### PowerShell
```powershell
$book = @{
    title = "Structure and Interpretation of Computer Programs"
    author = "Harold Abelson, Gerald Jay Sussman"
    isbn = "978-0262510875"
    publication_year = 1996
    total_copies = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/books" -Method Post -Body $book -ContentType "application/json"
```

### Python
```python
import requests

payload = {
    "title": "Structure and Interpretation of Computer Programs",
    "author": "Harold Abelson, Gerald Jay Sussman",
    "isbn": "978-0262510875",
    "publication_year": 1996,
    "total_copies": 3
}
resp = requests.post("http://127.0.0.1:8000/api/v1/books", json=payload)
print(resp.status_code, resp.json())
```

---

## 5. Replace Book (PUT) vs Partial Update (PATCH)

### PUT (Complete Replacement)
```bash
curl -X PUT "http://127.0.0.1:8000/api/v1/books/1" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Clean Code: A Handbook of Agile Software Craftsmanship (Revised)",
       "author": "Robert C. Martin",
       "isbn": "978-0132350884",
       "publication_year": 2008,
       "total_copies": 5
     }'
```

### PATCH (Partial Modification)
```bash
curl -X PATCH "http://127.0.0.1:8000/api/v1/books/1" \
     -H "Content-Type: application/json" \
     -d '{
       "total_copies": 6
     }'
```

---

## 6. Borrow an Available Book

### cURL
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/books/1/borrow" \
     -H "Content-Type: application/json" \
     -d '{
       "borrower_name": "Sarah Connor (Student ID: CS-402)"
     }'
```

### PowerShell
```powershell
$body = @{ borrower_name = "Sarah Connor (Student ID: CS-402)" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/books/1/borrow" -Method Post -Body $body -ContentType "application/json"
```

### Python
```python
import requests

resp = requests.post(
    "http://127.0.0.1:8000/api/v1/books/1/borrow",
    json={"borrower_name": "Sarah Connor (Student ID: CS-402)"}
)
print("Borrow Status:", resp.status_code)
print(resp.json())
```

---

## 7. Return a Borrowed Book

### cURL
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/books/1/return" \
     -H "Content-Type: application/json" \
     -d '{
       "borrowing_id": 1
     }'
```

### PowerShell
```powershell
$body = @{ borrowing_id = 1 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/books/1/return" -Method Post -Body $body -ContentType "application/json"
```

---

## 8. Delete a Book (DELETE)

### cURL
```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/books/6" -v
# Returns HTTP/1.1 204 No Content
```

### PowerShell
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/books/6" -Method Delete
```

---

## 9. List Borrowing History Records

### cURL
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/borrowings?limit=10&status=BORROWED" \
     -H "Accept: application/json"
```

### PowerShell
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/borrowings?limit=10&status=BORROWED" -Method Get
```
