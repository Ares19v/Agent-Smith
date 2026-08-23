"""
knowledge_base.py
=================
Comprehensive Computer Science, Data Structures, Algorithms, and Software Engineering
Knowledge Base for Agent Smith. Provides deep, formatted explanations with code examples
and complexity analysis for developer queries.
"""

import re

# Comprehensive Data Structures & Algorithms Catalog
CS_KNOWLEDGE = {
    # ─── DATA STRUCTURES ───────────────────────────────────────────────────────
    "hash table": {
        "title": "Hash Table (Hash Map / Associative Array / Dictionary)",
        "summary": "A Hash Table is an associative data structure that stores key-value pairs. It uses a **Hash Function** to compute an index (hash code) into an array of buckets, from which the desired value can be found in average **$O(1)$ constant time**.",
        "how_it_works": [
            "**Key Hashing:** The key (e.g., `'username'`) is passed to a hash function to generate a large numerical hash code.",
            "**Index Mapping:** The hash code is mapped to an array bucket index via `index = hash_code % array_size`.",
            "**Collision Resolution:** When two keys hash to the same bucket index, collisions are resolved via **Separate Chaining** (linked lists in each bucket) or **Open Addressing** (Linear Probing, Quadratic Probing)."
        ],
        "complexity": {
            "Average Insert": "$O(1)$",
            "Average Lookup": "$O(1)$",
            "Average Delete": "$O(1)$",
            "Worst-case (all collide)": "$O(n)$",
            "Space Complexity": "$O(n)$"
        },
        "python_code": """# Python Dictionary (built-in high-performance Hash Table)
# Uses open addressing with perturbation for collision resolution

user_scores = {}

# 1. Insert (O(1))
user_scores["Neo"] = 99
user_scores["Trinity"] = 95
user_scores["Morpheus"] = 92

# 2. Lookup (O(1))
score = user_scores.get("Neo", 0)
print(f"Neo's Score: {score}")

# 3. Check existence in O(1)
if "Trinity" in user_scores:
    print("Trinity exists in hash table")

# 4. Deletion (O(1))
del user_scores["Morpheus"]
""",
        "ts_code": """// JavaScript / TypeScript Map (Hash Table implementation)
const cache = new Map<string, number>();

// Insert & Retrieve (O(1))
cache.set("session_token_99", 404);
console.log(cache.get("session_token_99")); // 404
console.log(cache.has("session_token_99")); // true
"""
    },

    "linked list": {
        "title": "Linked List (Singly & Doubly Linked)",
        "summary": "A Linked List is a linear data structure where elements (nodes) are not stored at contiguous memory locations. Instead, each node contains data and a **pointer / reference** to the next node.",
        "how_it_works": [
            "**Singly Linked List:** Each node points forward to the `next` node.",
            "**Doubly Linked List:** Each node maintains pointers to both `next` and `prev` nodes.",
            "**Advantage:** Dynamic size and $O(1)$ constant time insertion/deletion at the head, without memory reallocation."
        ],
        "complexity": {
            "Access / Search": "$O(n)$",
            "Insert at Head": "$O(1)$",
            "Insert at Tail": "$O(1)$ (with tail pointer)",
            "Delete Node": "$O(1)$ (with pointer to node)",
            "Space Complexity": "$O(n)$"
        },
        "python_code": """class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def insert_at_head(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def display(self):
        curr = self.head
        elements = []
        while curr:
            elements.append(str(curr.value))
            curr = curr.next
        print(" -> ".join(elements) + " -> None")

ll = LinkedList()
ll.insert_at_head(30)
ll.insert_at_head(20)
ll.insert_at_head(10)
ll.display() # Output: 10 -> 20 -> 30 -> None
""",
        "ts_code": ""
    },

    "binary search tree": {
        "title": "Binary Search Tree (BST) & Self-Balancing Trees (AVL / Red-Black)",
        "summary": "A Binary Search Tree is a hierarchical node-based tree data structure where each node has at most two children. For any given node: all keys in the **left subtree are smaller**, and all keys in the **right subtree are greater**.",
        "how_it_works": [
            "**Binary Search Property:** Left Child < Parent < Right Child.",
            "**In-Order Traversal:** Visiting `Left -> Root -> Right` yields keys in strictly sorted ascending order.",
            "**Self-Balancing (AVL / Red-Black):** Automatically rotates subtrees to prevent degeneration into an $O(n)$ linked list."
        ],
        "complexity": {
            "Average Search": "$O(\\log n)$",
            "Average Insert": "$O(\\log n)$",
            "Average Delete": "$O(\\log n)$",
            "Worst-case (unbalanced)": "$O(n)$",
            "Space Complexity": "$O(n)$"
        },
        "python_code": """class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def insert_bst(root, val):
    if not root:
        return TreeNode(val)
    if val < root.val:
        root.left = insert_bst(root.left, val)
    else:
        root.right = insert_bst(root.right, val)
    return root

# Search in O(log n)
def search_bst(root, target):
    if not root or root.val == target:
        return root is not None
    if target < root.val:
        return search_bst(root.left, target)
    return search_bst(root.right, target)
""",
        "ts_code": ""
    },

    "stack": {
        "title": "Stack (Last-In, First-Out — LIFO)",
        "summary": "A Stack is a linear data structure following the **LIFO (Last In, First Out)** principle. The last element added is the first element to be removed (e.g. browser back button, function call execution stack, undo/redo).",
        "how_it_works": [
            "**Push:** Inserts an element on top of the stack ($O(1)$).",
            "**Pop:** Removes the topmost element ($O(1)$).",
            "**Peek / Top:** Inspects the top element without removing it ($O(1)$)."
        ],
        "complexity": {
            "Push": "$O(1)$",
            "Pop": "$O(1)$",
            "Peek": "$O(1)$",
            "Search": "$O(n)$",
            "Space Complexity": "$O(n)$"
        },
        "python_code": """stack = []

# Push
stack.append("page_1")
stack.append("page_2")
stack.append("page_3")

# Pop (LIFO)
top_item = stack.pop()
print(f"Popped: {top_item}") # Output: page_3
print(f"Current Top: {stack[-1]}") # Output: page_2
""",
        "ts_code": ""
    },

    "queue": {
        "title": "Queue (First-In, First-Out — FIFO)",
        "summary": "A Queue is a linear data structure following the **FIFO (First In, First Out)** principle. Elements are inserted at the rear (enqueue) and removed from the front (dequeue). Used in async task queues, print buffers, and BFS graph traversals.",
        "how_it_works": [
            "**Enqueue:** Adds an item to the end of the queue ($O(1)$).",
            "**Dequeue:** Removes the oldest item from the front of the queue ($O(1)$ with `collections.deque`)."
        ],
        "complexity": {
            "Enqueue": "$O(1)$",
            "Dequeue": "$O(1)$",
            "Front / Peek": "$O(1)$",
            "Space Complexity": "$O(n)$"
        },
        "python_code": """from collections import deque

task_queue = deque()

# Enqueue
task_queue.append("task_A")
task_queue.append("task_B")

# Dequeue (FIFO)
executed = task_queue.popleft()
print(f"Processed: {executed}") # task_A
""",
        "ts_code": ""
    },

    # ─── CORE CONCEPTS ────────────────────────────────────────────────────────
    "recursion": {
        "title": "Recursion & Base Cases",
        "summary": "Recursion is a programming technique where a function calls itself to break down complex problems into smaller, self-similar sub-problems. Every recursive function **must have a Base Case** to terminate execution and prevent a Stack Overflow error.",
        "how_it_works": [
            "**Base Case:** The condition under which the function stops calling itself and returns a direct value.",
            "**Recursive Step:** Reducing the problem and calling the function with updated parameters.",
            "**Call Stack:** Each call adds a frame to the execution call stack until base case is met, after which results unwind."
        ],
        "complexity": {
            "Call Stack Memory": "$O(\\text{depth})$",
            "Optimization": "Tail Call Optimization (TCO) or Iteration / Memoization"
        },
        "python_code": """def factorial(n: int) -> int:
    # 1. Base Case
    if n <= 1:
        return 1
    # 2. Recursive Case
    return n * factorial(n - 1)

print(factorial(5)) # 5 * 4 * 3 * 2 * 1 = 120
""",
        "ts_code": ""
    },

    "big o notation": {
        "title": "Big-O Notation & Algorithmic Complexity",
        "summary": "Big-O Notation mathematically describes the **worst-case asymptotic upper bound** of an algorithm's runtime or memory consumption as the input size ($n$) approaches infinity.",
        "how_it_works": [
            "**$O(1)$ Constant Time:** Execution time is independent of input size (e.g. Hash Map lookup, array index access).",
            "**$O(\\log n)$ Logarithmic Time:** Problem size is halved at each step (e.g. Binary Search).",
            "**$O(n)$ Linear Time:** Work scales proportionally with input items (e.g. single loop).",
            "**$O(n \\log n)$ Linearithmic:** Optimal comparison-based sorting (e.g. QuickSort, MergeSort, Timsort).",
            "**$O(n^2)$ Quadratic Time:** Nested loops over inputs (e.g. Bubble Sort, naive comparisons).",
            "**$O(2^n)$ Exponential Time:** Recursive branching without memoization (e.g. naive Fibonacci)."
        ],
        "complexity": {},
        "python_code": "",
        "ts_code": ""
    },

    "rest api": {
        "title": "REST API Architecture (Representational State Transfer)",
        "summary": "REST is a standard architectural design style for network communication between clients and servers using stateless HTTP requests.",
        "how_it_works": [
            "**Stateless:** Every HTTP request contains all context needed to process it; the server stores no client session context.",
            "**HTTP Methods:** `GET` (retrieve), `POST` (create), `PUT`/`PATCH` (update), `DELETE` (remove).",
            "**Status Codes:** `200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `500 Server Error`."
        ],
        "complexity": {},
        "python_code": """# FastAPI REST Endpoint
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/api/items/{item_id}")
async def read_item(item_id: int):
    if item_id == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "status": "active"}
""",
        "ts_code": ""
    },

    "jwt": {
        "title": "JWT (JSON Web Token Authentication)",
        "summary": "A JSON Web Token (JWT) is an open standard (RFC 7519) compact, URL-safe means of securely transmitting claims between parties as a JSON object, signed using a cryptographic secret (HMAC-SHA256) or public/private key pair (RSA/ECDSA).",
        "how_it_works": [
            "**Header:** Contains algorithm and token type (`{\"alg\": \"HS256\", \"typ\": \"JWT\"}`).",
            "**Payload (Claims):** User identity and permissions (`{\"sub\": \"user_123\", \"exp\": 1718000000}`).",
            "**Signature:** `HMACSHA256(base64UrlEncode(header) + \".\" + base64UrlEncode(payload), secret)`"
        ],
        "complexity": {},
        "python_code": """import hmac, hashlib, base64, json, time

# Concept representation of signing payload:
header = {"alg": "HS256", "typ": "JWT"}
payload = {"user_id": 42, "exp": int(time.time()) + 3600}
""",
        "ts_code": ""
    }
}


def lookup_cs_knowledge(query: str) -> str | None:
    """
    Scans the query against the knowledge base and generates a comprehensive technical explanation.
    """
    q = query.lower().strip()

    # Search for matching keys
    matched_key = None
    for key in CS_KNOWLEDGE:
        # Match "hash table", "hash map", "hashtable", "hashmap", "dictionary"
        if key in q or (key == "hash table" and any(w in q for w in ["hashtable", "hashmap", "hash table", "hash map", "hash function", "hash", "dict", "dictionary"])):
            matched_key = "hash table"
            break
        elif key == "linked list" and ("linked list" in q or "linkedlist" in q or "singly linked" in q or "doubly linked" in q):
            matched_key = "linked list"
            break
        elif key == "binary search tree" and ("binary search tree" in q or "bst" in q or "binary tree" in q or "avl tree" in q or "red black tree" in q):
            matched_key = "binary search tree"
            break
        elif key == "stack" and ("stack" in q and ("lifo" in q or "data structure" in q or "what is a stack" in q or "pop" in q or "push" in q)):
            matched_key = "stack"
            break
        elif key == "queue" and ("queue" in q and ("fifo" in q or "data structure" in q or "what is a queue" in q or "enqueue" in q or "dequeue" in q)):
            matched_key = "queue"
            break
        elif key == "recursion" and ("recursion" in q or "recursive" in q or "base case" in q):
            matched_key = "recursion"
            break
        elif key == "big o notation" and ("big o" in q or "time complexity" in q or "space complexity" in q or "asymptotic" in q):
            matched_key = "big o notation"
            break
        elif key == "rest api" and ("rest api" in q or "restful" in q or "what is rest" in q or "http methods" in q):
            matched_key = "rest api"
            break
        elif key == "jwt" and ("jwt" in q or "json web token" in q or "token auth" in q):
            matched_key = "jwt"
            break

    if not matched_key:
        return None

    data = CS_KNOWLEDGE[matched_key]

    output = f"### 💡 {data['title']}\n\n"
    output += f"{data['summary']}\n\n"

    if data.get("how_it_works"):
        output += "#### ⚙️ How It Works:\n"
        for point in data["how_it_works"]:
            output += f"* {point}\n"
        output += "\n"

    if data.get("complexity"):
        output += "#### 📊 Complexity Analysis:\n"
        for op, comp in data["complexity"].items():
            output += f"* **{op}:** {comp}\n"
        output += "\n"

    if data.get("python_code"):
        output += "#### 💻 Code Implementation:\n"
        output += f"```python\n{data['python_code'].strip()}\n```\n\n"

    if data.get("ts_code"):
        output += f"```typescript\n{data['ts_code'].strip()}\n```\n\n"

    return output.strip()
