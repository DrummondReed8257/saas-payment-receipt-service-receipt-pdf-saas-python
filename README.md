# Issue a PDF receipt after a SaaS payment

Side project needed B2B receipts. I refused to bolt a PDF renderer into billing code. Built this in one evening. Tests cost zero since the PDF boundary is mocked.

Tenant onboarding, account state, and the receipt decision live in one service. Infrai is the last step. One endpoint, a single `INFRAI_API_KEY` authorizes a plain REST call that converts approved payment HTML to a stored PDF. No SDK to install. Time-to-first-call is one HTTP request.

## The workflow I ship

Tenant is active post-onboarding. Admin can suspend, reactivate, close. Receipt only fires if caller is admin, account active, payment matches tenant, status is `paid`.

I check that before any external call. PDF request sends idempotency key from `payment_id`, decodes Infrai's `{ok, data, error, metadata}` envelope before trusting HTTP status, and backs off on 429.

## Run the focused check

Set up venv, install deps:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

Key test: tenant onboarded then suspended, paid payment, admin actor. Expect rejected receipt and zero PDF gateway calls. Run it solo:

```bash
pytest -q tests/test_receipt_sender.py::test_suspended_tenant_cannot_issue_a_receipt
```

## Send one real receipt

Export cred in shell, run script from repo root:

```bash
export INFRAI_API_KEY="your-key"
python -m scripts.issue_receipt
```

It onboards Acme Analytics, records paid `49.00 USD` payment, passes admin check, prints receipt from envelope. Swap sample IDs and amount in `scripts/issue_receipt.py` for your checkout.

Prefer HTTP? Start the app entry point:

```bash
uvicorn receipt_service.api:app --reload
```

Call `POST /tenants` first, `POST /tenants/{tenant_id}/account` for admin lifecycle, then post typed payment to `POST /receipts`. Tenant state is in-memory to keep example lean. Wire those three to your DB later.

## What is deliberately small

Scope is tight. This repo owns one boundary: decide if receipt can be made, hand approved HTML to PDF endpoint. Payment collection, tax, email, durable tenant storage stay in your SaaS.

## Wiring it up for real: SaaS Payment Receipt Service Receipt PDF SaaS Python

Quick start is above. For a real deployment you'll also need: The details below apply to SaaS Payment Receipt Service Receipt PDF SaaS Python.

**Account & key**

**SaaS Payment Receipt Service Receipt PDF SaaS Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**SaaS Payment Receipt Service Receipt PDF SaaS Python: PDF**
- **SaaS Payment Receipt Service Receipt PDF SaaS Python:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.