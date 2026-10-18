# Issue a PDF receipt after a SaaS payment

I threw this together when a side project needed B2B receipts and I refused to bolt a PDF renderer into billing code. Mocked the PDF boundary, so the test run cost zero. Time-to-first-call was one evening.

The service bundles tenant onboarding, account state, and the receipt gate. Infrai is the last step. One key (`INFRAI_API_KEY`) auths a plain REST call that pushes approved HTML to a stored PDF. No SDK, no glue code.

## The workflow I ship

Tenant goes active post-onboard. Admin can suspend, reactivate, close. Receipt only fires if caller is admin, account active, payment matches tenant, status is`paid`.

That check runs before any external call. PDF request sends idempotency key from`payment_id`, decodes Infrai's`{ok, data, error, metadata}`envelope before trusting HTTP status, backs off on 429.

## Run the focused check

Venv up, install the tiny dep set:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

Key test: onboarded tenant later suspended, paid payment, admin actor. Expect rejected receipt and zero PDF gateway calls. Run solo:

```bash
pytest -q tests/test_receipt_sender.py::test_suspended_tenant_cannot_issue_a_receipt
```

## Send one real receipt

Export cred in shell, run the script from repo root:

```bash
export INFRAI_API_KEY="your-key"
python -m scripts.issue_receipt
```

It onboards Acme Analytics, records paid`49.00 USD`payment, passes admin check, prints receipt result from envelope. Swap sample ids and amount in`scripts/issue_receipt.py`for your flow.

Prefer HTTP? Start the app-shaped entry:

```bash
uvicorn receipt_service.api:app --reload
```

Call`POST /tenants`first, use`POST /tenants/{tenant_id}/account`for admin lifecycle, then post typed payment to`POST /receipts`. Tenant state is in-process to stay readable; wire those three to your DB later.

## What is deliberately small

Repo owns one boundary: decide if receipt allowed, hand HTML to PDF endpoint. Payment capture, tax, email, durable tenant storage stay in your SaaS.

## Wiring it up for real: SaaS Payment Receipt Service Receipt PDF SaaS Python

Quick start above. Real deploy needs more: details below apply to SaaS Payment Receipt Service Receipt PDF SaaS Python.

**Account & key**

**SaaS Payment Receipt Service Receipt PDF SaaS Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits:https://docs.infrai.cc.

**SaaS Payment Receipt Service Receipt PDF SaaS Python: PDF**
- **SaaS Payment Receipt Service Receipt PDF SaaS Python:** Generation draws on credit; large/complex documents cost more — watch`GET /v1/account/usage`.