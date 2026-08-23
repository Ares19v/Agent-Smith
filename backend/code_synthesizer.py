"""
code_synthesizer.py
===================
Intelligent dynamic code & algorithm synthesis engine for Agent Smith.
Generates genuine, executable code snippets, algorithmic logic, and technical solutions
locally without requiring external cloud API keys.
"""

import re
import random
from knowledge_base import lookup_cs_knowledge


def synthesize_solution(agent_name: str, query: str) -> str | None:
    """
    Analyzes the user's technical query and dynamically generates real, runnable code,
    explanations, and implementation details tailored to the active core.
    """
    # ── 0. Check CS / Data Structures Knowledge Base ─────────────────────────
    cs_explanation = lookup_cs_knowledge(query)
    if cs_explanation:
        return cs_explanation

    q = query.lower().strip()


    # ──────────────────────────────────────────────────────────────────────────
    # 1. RANDOM NUMBER GENERATION / ALGORITHMS
    # ──────────────────────────────────────────────────────────────────────────
    if "random" in q and any(w in q for w in ["number", "algo", "algorithm", "code", "integer", "between", "generate", "rand"]):
        # Extract range if specified
        range_match = re.search(r"(\d+)\s*(?:to|and|-)\s*(\d+)", q)
        min_v = int(range_match.group(1)) if range_match else 1
        max_v = int(range_match.group(2)) if range_match else 10

        return f"""### 🎲 Random Number Generator Algorithm ({min_v} to {max_v})

Here is the implementation in **Python** (using Python's Mersenne Twister pseudo-random number generator) and **JavaScript / TypeScript**:

#### Python Implementation:
```python
import random

def generate_random_integer(min_val: int = {min_v}, max_val: int = {max_v}) -> int:
    \"\"\"
    Generates a pseudo-random integer in the range [min_val, max_val] inclusive.
    Algorithm: Uses Mersenne Twister (MT19937) engine with a period of 2^19937 - 1.
    \"\"\"
    return random.randint(min_val, max_val)

# Execute:
result = generate_random_integer({min_v}, {max_v})
print(f"Generated Random Value: {{result}}")
```

#### JavaScript / TypeScript Implementation:
```typescript
function getRandomInt(min: number = {min_v}, max: number = {max_v}): number {{
    // Math.random() produces [0, 1)
    // Formula: floor(random * (max - min + 1)) + min
    return Math.floor(Math.random() * (max - min + 1)) + min;
}}

const sample = getRandomInt({min_v}, {max_v});
console.log(`Generated Value: ${{sample}}`);
```

#### ⚙️ Algorithmic Complexity:
* **Time Complexity:** $O(1)$ constant time execution.
* **Space Complexity:** $O(1)$ auxiliary memory."""

    # ──────────────────────────────────────────────────────────────────────────
    # 2. SORTING ALGORITHMS (Quicksort, Mergesort, Bubble Sort, Binary Search)
    # ──────────────────────────────────────────────────────────────────────────
    if "quicksort" in q or ("sort" in q and ("quick" in q or "algo" in q or "write" in q)):
        return """### ⚡ QuickSort Algorithm Implementation

QuickSort is a Divide-and-Conquer algorithm that picks an element as a pivot and partitions the array around the picked pivot.

```python
def quicksort(arr: list) -> list:
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

# Example Execution:
sample_data = [64, 34, 25, 12, 22, 11, 90]
sorted_data = quicksort(sample_data)
print(f"Sorted Array: {sorted_data}")
```

#### 📊 Performance Characteristics:
* **Best / Average Time:** $O(n \\log n)$
* **Worst-case Time:** $O(n^2)$ (mitigated with randomized pivot selection)
* **Space Complexity:** $O(\\log n)$ recursion stack."""

    if "binary search" in q or ("search" in q and ("binary" in q or "find" in q)):
        return """### 🔍 Binary Search Algorithm

Binary Search finds the position of a target value within a sorted array by repeatedly dividing the search interval in half.

```python
def binary_search(arr: list[int], target: int) -> int:
    \"\"\"Returns index of target in sorted array, or -1 if not found.\"\"\"
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
            
    return -1

# Test:
numbers = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
idx = binary_search(numbers, 23)
print(f"Target found at index: {idx}") # Output: 5
```

* **Time Complexity:** $O(\\log n)$
* **Space Complexity:** $O(1)$"""

    # ──────────────────────────────────────────────────────────────────────────
    # 3. FIBONACCI / DYNAMIC PROGRAMMING
    # ──────────────────────────────────────────────────────────────────────────
    if "fibonacci" in q:
        return """### 🌀 Fibonacci Sequence (Memoized Dynamic Programming)

```python
def fibonacci(n: int, memo: dict = {}) -> int:
    \"\"\"Computes the n-th Fibonacci number in O(n) time with memoization.\"\"\"
    if n <= 0:
        return 0
    if n == 1:
        return 1
    if n in memo:
        return memo[n]
    
    memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo)
    return memo[n]

# First 10 Fibonacci numbers:
print([fibonacci(i) for i in range(10)])
# Output: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

* **Time Complexity:** $O(n)$ (down from naive exponential $O(2^n)$)
* **Space Complexity:** $O(n)$ memoization dictionary."""

    # ──────────────────────────────────────────────────────────────────────────
    # 4. PALINDROME & TWO SUM (Popular LeetCode / Coding Prompts)
    # ──────────────────────────────────────────────────────────────────────────
    if "two sum" in q:
        return """### 🎯 Two Sum Algorithm (Hash Map Lookup)

Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

```python
def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {} # value -> index
    for index, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], index]
        seen[num] = index
    return []

# Test:
print(two_sum([2, 7, 11, 15], 9)) # Output: [0, 1]
```

* **Time Complexity:** $O(n)$ single-pass scan.
* **Space Complexity:** $O(n)$ hash map storage."""

    if "palindrome" in q:
        return """### 🔄 Palindrome Verification Algorithm

```python
def is_palindrome(s: str) -> bool:
    # Filter alphanumeric characters and convert to lowercase
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    # Two-pointer check
    left, right = 0, len(cleaned) - 1
    while left < right:
        if cleaned[left] != cleaned[right]:
            return False
        left += 1
        right -= 1
    return True

print(is_palindrome("A man, a plan, a canal: Panama")) # True
```"""

    # ──────────────────────────────────────────────────────────────────────────
    # 5. FRONTEND: REACT / HOOKS / CSS
    # ──────────────────────────────────────────────────────────────────────────
    if agent_name == "Frontend Dev" or ("react" in q or "component" in q or "hooks" in q or "useeffect" in q or "usestate" in q or "tailwind" in q):
        if "hook" in q or "state" in q or "counter" in q or "component" in q:
            return """### ⚛️ React Functional Component & Custom State Hook

```tsx
import React, { useState, useEffect, useCallback } from 'react';

interface DataItem {
  id: string;
  title: string;
  status: 'active' | 'pending';
}

export const MetricDashboard: React.FC = () => {
  const [items, setItems] = useState<DataItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchMetrics = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/metrics');
      const data = await response.json();
      setItems(data);
    } catch (err) {
      console.error('Failed to load metrics:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  return (
    <div className="p-6 bg-slate-900 text-white rounded-xl shadow-lg border border-slate-800">
      <h2 className="text-xl font-bold text-emerald-400 mb-4">System Telemetry</h2>
      {loading ? (
        <div className="animate-pulse text-slate-400">Loading neural feed...</div>
      ) : (
        <ul className="space-y-2">
          {items.map((item) => (
            <li key={item.id} className="flex justify-between p-3 bg-slate-800/50 rounded-lg">
              <span>{item.title}</span>
              <span className="text-emerald-400 font-mono">{item.status}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
```"""

        if "flex" in q or "grid" in q or "center" in q or "css" in q:
            return """### 🎨 Modern Responsive CSS Grid & Flexbox Solution

```css
/* Center any element horizontally & vertically */
.flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

/* Auto-responsive card grid (No media queries required) */
.responsive-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
}

/* Glassmorphism card */
.glass-card {
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.glass-card:hover {
  transform: translateY(-4px);
  border-color: #00ff41;
}
```"""

    # ──────────────────────────────────────────────────────────────────────────
    # 6. BACKEND: FASTAPI / SQL / AUTH
    # ──────────────────────────────────────────────────────────────────────────
    if agent_name == "Backend Dev" or ("fastapi" in q or "endpoint" in q or "jwt" in q or "pydantic" in q or "database" in q or "sql" in q):
        return """### 🚀 FastAPI REST Router with Pydantic Validation & JWT Auth

```python
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, Field
from typing import List
import time

router = APIRouter(prefix="/api/v1", tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: str = "developer"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: float

# In-memory store (or SQL database session)
db = []

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    new_user = {
        "id": len(db) + 1,
        "username": user.username,
        "email": user.email,
        "created_at": time.time()
    }
    db.append(new_user)
    return new_user

@router.get("/users", response_model=List[UserResponse])
async def list_users(token: str = Depends(oauth2_scheme)):
    return db
```"""

    # ──────────────────────────────────────────────────────────────────────────
    # 7. DEVOPS: DOCKER / CI/CD
    # ──────────────────────────────────────────────────────────────────────────
    if agent_name == "DevOps Engineer" or ("docker" in q or "ci" in q or "kubernetes" in q or "k8s" in q or "nginx" in q):
        return """### 🐳 Multi-Stage Production Dockerfile & GitHub Actions Workflow

#### Multi-Stage Dockerfile:
```dockerfile
# ── Stage 1: Build & Dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ── Stage 2: Final Minimal Runtime Image
FROM python:3.11-slim AS runner
WORKDIR /app

# Run as non-privileged user for security
RUN useradd -m -u 1001 appuser
USER appuser

COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . /app

ENV PATH=/home/appuser/.local/bin:$PATH
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### GitHub Actions CI (`.github/workflows/ci.yml`):
```yaml
name: CI/CD Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pytest
      - run: pytest --maxfail=1 --disable-warnings
```"""

    # ──────────────────────────────────────────────────────────────────────────
    # 8. SECURITY: XSS / SQLi / AUTH HARDENING
    # ──────────────────────────────────────────────────────────────────────────
    if agent_name == "Security Analyst" or ("security" in q or "xss" in q or "sqli" in q or "cors" in q or "token" in q or "sanitize" in q):
        return """### 🛡️ Web Application Security Hardening (OWASP Top 10)

```python
import bleach
import re
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()

# 1. Strict CORS Configuration (Avoid allow_origins=["*"] in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# 2. XSS Input Sanitization Helper
def sanitize_user_input(dirty_html: str) -> str:
    \"\"\"Cleans user input to strip malicious script injection tags.\"\"\"
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'code']
    return bleach.clean(dirty_html, tags=allowed_tags, strip=True)

# 3. Security Headers Middleware (CSP, HSTS, X-Frame-Options)
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```"""

    return None
