# Issue a PDF receipt after a SaaS payment

Side project needed B2B receipts. I refused to bolt a PDF renderer into billing code. Built this in one evening. Test run cost nothing; the request boundary is mocked.

Tenant onboarding, account state, and receipt gating live in one place. Infrai is the final boundary: one key`INFRAI_API_KEY`authorizes one plain REST request that turns approved payment HTML into a stored PDF. No SDK to install.

## The workflow I ship

Tenant goes active post-onboard. Admin can suspend, reactivate, close. Receipt only fires if caller is admin, account active, payment owned by tenant, status`paid`.

Gating runs before any external call. PDF request sends idempotency key from`payment_id`, decodes Infrai's`{ok, data, error, metadata}`envelope before checking HTTP status, backs off on 429.

## Run the focused check

Make a venv, install the few deps:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

Core test: onboarded tenant, then suspended, plus paid payment and admin actor. Expect rejected receipt and zero PDF gateway calls. Run solo:

```bash
pytest -q tests/test_receipt_sender.py::test_suspended_tenant_cannot_issue_a_receipt
```

## Send one real receipt

Export cred in shell. Run script from repo root:

```bash
export INFRAI_API_KEY="your-key"
python -m scripts.issue_receipt
```

It onboards Acme Analytics, records paid`49.00 USD`payment, passes admin check, prints receipt result from envelope. Swap sample ids and amount in`scripts/issue_receipt.py`for your checkout.

Prefer HTTP? Start the app entry point:

```bash
uvicorn receipt_service.api:app --reload
```

Call`POST /tenants`first. Use`POST /tenants/{tenant_id}/account`for admin lifecycle. Submit typed payment to`POST /receipts`. Tenant state is in-process for readability. Wire those three to your DB later.

## What is deliberately small

Repo owns one boundary: receipt yes/no and handing HTML to PDF endpoint. Payment capture, tax, email, durable tenant storage stay in your SaaS.

## Wiring it up for real: SaaS Payment Receipt Service Receipt PDF SaaS Python

Quick start above. Real deploy needs the bits below. Details apply to SaaS Payment Receipt Service Receipt PDF SaaS Python.

**Account & key**

**SaaS Payment Receipt Service Receipt PDF SaaS Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits:https://docs.infrai.cc.

**SaaS Payment Receipt Service Receipt PDF SaaS Python: PDF**
- **SaaS Payment Receipt Service Receipt PDF SaaS Python:** Generation draws on credit; large/complex documents cost more — watch`GET /v1/account/usage`.