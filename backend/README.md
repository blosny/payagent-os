# PayAgent OS — Backend Architecture & Service Guide

> **Autonomous AI Agent Financial Infrastructure & PayPal Orchestration Layer**

[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg)](https://fastapi.tiangolo.com/)
[![PayPal: REST API v2](https://img.shields.io/badge/PayPal-REST%20API%20v2-003087.svg)](https://developer.paypal.com/)

---

## 1. Overview & Architectural Principles

The **PayAgent OS Backend** acts as an intelligent, guardrail-governed financial gateway that allows autonomous AI agents (DevOps bots, data harvesters, LLM agents) to programmatically procure services using **PayPal REST API v2**.

### Core Pillars
1. **Asynchronous Non-Blocking I/O:** Built with Python 3.11+, FastAPI, and HTTPX for high-throughput concurrency.
2. **Policy Guardrail Enforcement:** Agents are never given unrestricted funds. Every transaction is strictly evaluated against per-transaction thresholds, rolling daily caps, and vendor allowlists.
3. **Dual Execution Engine (Live Sandbox & Simulation):** If PayPal Sandbox credentials are not yet defined in `.env`, the system automatically shifts into a realistic simulation mode, ensuring demos and tests never crash.

---

## 2. Directory Structure

```text
backend/
├── app/
│   ├── __init__.py           # Package marker and version
│   ├── main.py               # FastAPI entry point, CORS, routers & static UI server
│   ├── config.py             # Pydantic Settings reading .env
│   ├── models/               # Pydantic v2 data schemas
│   │   ├── __init__.py
│   │   ├── agent.py          # Agent identity, budget caps & policy definitions
│   │   └── transaction.py    # Payment intents, approval states & audit records
│   ├── services/             # Core business logic
│   │   ├── __init__.py
│   │   ├── paypal_service.py # Async PayPal REST client (OAuth2, Orders, Payouts)
│   │   └── policy_engine.py  # Guardrail evaluation & Human-in-the-Loop engine
│   └── api/                  # REST API routes
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py   # Router aggregator (/api/v1)
│           ├── agents.py     # Agent wallet management endpoints
│           ├── payments.py   # Autonomous execution & HITL approval endpoints
│           └── stats.py      # Real-time metrics & financial volume aggregates
└── requirements.txt          # Python dependencies
```

---

## 3. Services & Function Walkthrough

### 3.1 `PayPalService` (`app/services/paypal_service.py`)
Handles all communications with the PayPal REST API v2:

- **`get_access_token()`:**
  - Authenticates via OAuth 2.0 Client Credentials (`POST /v1/oauth2/token`).
  - Caches the Bearer token with expiration tracking.
  - Automatically falls back to `simulated_sandbox_token` in local development when keys are omitted.

- **`create_order(amount, currency, description, reference_id)`:**
  - Dispatches an order creation request to `POST /v2/checkout/orders` with `intent: CAPTURE`.
  - Attaches unique `PayPal-Request-Id` headers to prevent double charges.

- **`capture_order(order_id)`:**
  - Captures authorized payment funds (`POST /v2/checkout/orders/{order_id}/capture`).
  - Returns permanent `capture_id` on settlement.

- **`create_payout(recipient_email, amount, currency, note)`:**
  - Disburses funds directly to contractor/agent PayPal accounts via `POST /v1/payments/payouts`.

---

### 3.2 `PolicyEngine` (`app/services/policy_engine.py`)
The autonomous risk and safety brain:

- **`evaluate_policy(agent, intent)`:**
  - Evaluates intents against 5 guardrails:
    1. Is the agent active?
    2. Does the agent have sufficient balance?
    3. Is `auto_approval_enabled` true?
    4. Is the vendor in the agent's `allowed_vendors` allowlist?
    5. Does the amount stay within `max_per_transaction` and rolling `daily_budget`?
  - Returns `(True, "Within all autonomous policy limits.")` or `(False, "Violation Reason")`.

- **`submit_intent(intent)`:**
  - If policy checks pass: Autonomously executes PayPal order/payout, settles funds, and marks status as `APPROVED_AUTONOMOUS`.
  - If policy limits are exceeded: Pauses the transaction and routes it to `PENDING_APPROVAL` (Human-in-the-Loop queue).

- **`resolve_pending_transaction(tx_id, decision, reviewer_notes)`:**
  - Processes supervisor decisions (`APPROVE` or `REJECT`) from the dashboard.
  - On approval: Settles funds via PayPal and marks status as `APPROVED_BY_HUMAN`.

---

## 4. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status & PayPal connection indicator |
| `GET` | `/api/v1/agents` | List all registered AI agents and wallet policies |
| `POST` | `/api/v1/agents` | Register a new agent with custom policy limits |
| `GET` | `/api/v1/payments` | Retrieve immutable transaction audit log |
| `POST` | `/api/v1/payments/intent` | **Primary Agent Endpoint:** Submit autonomous payment intent |
| `POST` | `/api/v1/payments/{tx_id}/resolve` | **HITL:** Supervisor approves or rejects paused intent |
| `GET` | `/api/v1/stats/summary` | Real-time aggregated statistics for dashboard |

---

## 5. Testing

Run the test suite:
```bash
pytest -v
```

---

<details>
<summary><strong>🇹🇷 Türkçe Özet & Hızlı Notlar</strong></summary>

### Backend Özeti:
PayAgent OS backend'i, FastAPI ve PayPal REST API v2 kullanarak yapay zeka ajanlarının güvenli harcama yapmasını sağlayan bir orkestrasyon motorudur. 
- **`paypal_service.py`:** PayPal OAuth 2.0, Orders ve Payouts API'lerini asenkron yönetir.
- **`policy_engine.py`:** Ajanların harcama limitlerini, günlük bütçelerini ve onaylı satıcı listelerini denetler. Güvenlik sınırını aşan işlemler iptal edilmez; İnsan Onay Masası'na (Human-in-the-Loop) aktarılır.
- **Test:** `pytest -v` komutu ile tüm politika kuralları doğrulanır.
</details>
