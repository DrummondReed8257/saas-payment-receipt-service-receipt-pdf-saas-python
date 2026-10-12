from fastapi import FastAPI, HTTPException

from .infrai_pdf import InfraiError, InfraiPdfClient
from .models import AccountChange, ReceiptIssueRequest, ReceiptIssueResult, TenantOnboarding, TenantView
from .receipt_sender import ReceiptDecisionError, ReceiptService

service = ReceiptService(InfraiPdfClient())
app = FastAPI(title="SaaS receipt issuer")


@app.post("/tenants", response_model=TenantView, status_code=201)
def onboard_tenant(request: TenantOnboarding) -> TenantView:
    return service.onboard(request)


@app.post("/tenants/{tenant_id}/account", response_model=TenantView)
def change_tenant_account(tenant_id: str, request: AccountChange) -> TenantView:
    try:
        return service.change_account(tenant_id, request.status)
    except ReceiptDecisionError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/receipts", response_model=ReceiptIssueResult, status_code=201)
def issue_receipt(request: ReceiptIssueRequest) -> ReceiptIssueResult:
    try:
        return service.issue(request)
    except ReceiptDecisionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except InfraiError as exc:
        client_status = exc.status_code if 400 <= exc.status_code < 500 else 502
        raise HTTPException(status_code=client_status, detail={"code": exc.code, "message": str(exc)}) from exc

