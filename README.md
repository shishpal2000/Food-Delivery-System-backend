# 🍽️ Food Delivery Backend System

This project implements a distributed backend system for a **Food Order Lifecycle**, built using **Django REST Framework**.
It manages orders from **placement to delivery**, with three independent services that interact through asynchronous signals (events).

---

## 🚀 Overview

### 🎯 Product Vision

A **modular, event-driven backend** that manages the food order lifecycle — from **placement by a customer** to **delivery by a partner**, using **loosely coupled Django apps**.

---

## 🏗️ System Architecture

```
                     ┌──────────────────────────┐
                     │        Users App         │
                     │  (Auth & Roles Mgmt)     │
                     └───────────┬──────────────┘
                                 │
             ┌───────────────────┼───────────────────┐
             │                   │                   │
┌────────────┴────────────┐ ┌────┴────────────────┐ ┌──────────────┴────────────┐
│     Order Service       │ │  Restaurant Service │ │     Delivery Service      │
│--------------------------│ │--------------------│ │---------------------------│
│ Handles:                 │ │ Handles:           │ │ Handles:                  │
│ - Place Order            │ │ - Accept Order     │ │ - Pick Up Order           │
│ - Cancel Order           │ │ - Prepare Order    │ │ - Deliver Order           │
│ - View Orders            │ │ - Notify Delivery  │ │ - Update Order Status     │
└────────────┬────────────┘ └──────────┬─────────┘ └──────────────┬────────────┘
             │                         │                         │
             └─────────────── Async Event Bus (Signals) ─────────┘
```

---

## ⚙️ Design Highlights

* **Event-driven communication** via Django signals
* **Role-based permissions** for Customer, Restaurant Owner, Delivery Partner
* **Order lifecycle state machine:**

  ```
  PENDING → ACCEPTED → PREPARED → PICKED_UP → DELIVERED
  ```

---

## 🧭 API Flow & Usage Guide

This section explains the **chronological flow of API calls** — who triggers which endpoint and in what sequence.

### 🔹 Step 1: User Registration (All Roles)

**Endpoint:** `/auth/register/`
Each user (Customer, Restaurant Owner, Delivery Boy) registers first.

**Example:**

```json
{
  "username": "customer1",
  "password": "12345",
  "user_type": "CUSTOMER"
}
```

➡️ *Repeat for restaurant owner and delivery boy.*

---

### 🔹 Step 2: Obtain JWT Tokens

**Endpoint:** `/auth/token/`

```json
{
  "username": "customer1",
  "password": "12345"
}
```

Response:

```json
{
  "access": "eyJhbGciOiJIUzI1...",
  "refresh": "eyJhbGciOiJIUzI1..."
}
```

Use this `access` token for authentication in all requests.

---

### 🔹 Step 3: Restaurant Owner Creates Restaurant

**Endpoint:** `/api/restaurants/`
(Authenticated as a restaurant owner)

```json
{
  "name": "Domino's",
  "address": "Sector 45, Gurugram"
}
```

Response:

```json
{
  "id": 3,
  "owner": "owner1",
  "name": "Domino's",
  "address": "Sector 45, Gurugram"
}
```

---

### 🔹 Step 4: Restaurant Owner Adds Menu Items

**Endpoint:** `/api/items/create/`

```json
{
  "restaurant": 3,
  "name": "Margherita Pizza",
  "price": 250
}
```

Response:

```json
{
  "id": 10,
  "restaurant": "Domino's",
  "name": "Margherita Pizza",
  "price": 250
}
```

---

### 🔹 Step 5: Customer Places an Order

**Endpoint:** `/api/orders/place/`
(Authenticated as `CUSTOMER`)

```json
{
  "restaurant_id": 3,
  "items": [10],
  "total_price": 250
}
```

Response:

```json
{
  "id": 22,
  "status": "PENDING",
  "restaurant": "Domino's",
  "customer": "customer1"
}
```

**Event Triggered:** `order.created`
➡️ Sent to Restaurant service.

---

### 🔹 Step 6: Restaurant Accepts the Order

**Endpoint:** `/api/restaurants/22/accept/`
(Authenticated as the restaurant owner)

```json
{
  "status": "ACCEPTED"
}
```

Response:

```json
{
  "message": "Order accepted successfully.",
  "status": "ACCEPTED"
}
```

**Event Triggered:** `order.accepted`

---

### 🔹 Step 7: Restaurant Prepares the Order

**Endpoint:** `/api/restaurants/22/prepare/`

```json
{
  "status": "PREPARED"
}
```

Response:

```json
{
  "message": "Order prepared successfully and sent to delivery.",
  "status": "PREPARED"
}
```

**Event Triggered:** `order.prepared`
➡️ Delivery service notified.

---

### 🔹 Step 8: Delivery Partner Picks Up the Order

**Endpoint:** `/api/delivery/22/pickup/`
(Authenticated as delivery boy)

Response:

```json
{
  "status": "PICKED_UP",
  "message": "Order picked up successfully."
}
```

**Event Triggered:** `order.picked_up`

---

### 🔹 Step 9: Delivery Partner Delivers the Order

**Endpoint:** `/api/delivery/22/deliver/`

Response:

```json
{
  "status": "DELIVERED",
  "message": "Order delivered successfully."
}
```

**Event Triggered:** `order.delivered`

---

### 🔹 Step 10: Customer Views Their Orders

**Endpoint:** `/api/orders/my-orders/`
(Authenticated as the same customer)

Response:

```json
[
  {
    "id": 22,
    "restaurant": "Domino's",
    "status": "DELIVERED",
    "total_price": 250
  }
]
```

---

## 📚 Endpoint Summary by Role

| Role                 | Endpoints                                                                                                                        | Description                                    |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| **Customer**         | `/api/orders/place/`, `/api/orders/my-orders/`, `/api/orders/<id>/cancel/`                                                       | Create, view, cancel own orders                |
| **Restaurant Owner** | `/api/restaurants/`, `/api/items/create/`, `/api/items/list/`, `/api/restaurants/<id>/accept/`, `/api/restaurants/<id>/prepare/` | Manage restaurant, menu, and order preparation |
| **Delivery Boy**     | `/api/delivery/<id>/pickup/`, `/api/delivery/<id>/deliver/`                                                                      | Manage pickup and delivery                     |
| **Admin**            | `/admin/`                                                                                                                        | Global monitoring                              |

---

## 🧠 Data Flow Summary

| Step | Actor      | API                              | Emits Signal      | Next Step           |
| ---- | ---------- | -------------------------------- | ----------------- | ------------------- |
| 1    | Customer   | `/api/orders/place/`             | `order.created`   | Restaurant notified |
| 2    | Restaurant | `/api/restaurants/<id>/accept/`  | `order.accepted`  | Kitchen preparing   |
| 3    | Restaurant | `/api/restaurants/<id>/prepare/` | `order.prepared`  | Delivery assigned   |
| 4    | Delivery   | `/api/delivery/<id>/pickup/`     | `order.picked_up` | Out for delivery    |
| 5    | Delivery   | `/api/delivery/<id>/deliver/`    | `order.delivered` | Customer notified   |

---

## 🔐 Authentication

All APIs are protected using **JWT Authentication**.

You can generate or refresh tokens from:

* `/auth/token/`
* `/auth/token/refresh/`

---

## 🛠️ Local Setup

```bash
git clone https://github.com/shishpal2000/Food-Delivery-System-backend.git
cd food_delivery
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Access: [http://127.0.0.1:8000](http://127.0.0.1:8000)


