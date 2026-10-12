from html import escape
from typing import Any

from .models import AccountStatus, Payment, PaymentStatus, ReceiptIssueRequest, ReceiptIssueResult, TenantOnboarding, TenantView


class ReceiptDecisionError(ValueError):
    pass


class ReceiptService:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway
        self.tenants: dict[str, TenantView] = {}

    def onboard(self, request: TenantOnboarding) -> TenantView:
        tenant = TenantView(**request.model_dump(), status=AccountStatus.ACTIVE)
        self.tenants[tenant.tenant_id] = tenant
        return tenant

    def change_account(self, tenant_id: str, status: AccountStatus) -> TenantView:
        tenant = self._tenant(tenant_id)
        updated = tenant.model_copy(update={"status": status})
        self.tenants[tenant_id] = updated
        return updated

    def issue(self, request: ReceiptIssueRequest) -> ReceiptIssueResult:
        tenant = self._tenant(request.tenant_id)
        self._authorize_receipt(tenant, request)
        pdf = self.gateway.generate_receipt(self._receipt_html(tenant, request.payment), request.payment.payment_id)
        return ReceiptIssueResult(
            tenant_id=tenant.tenant_id,
            payment_id=request.payment.payment_id,
            receipt=pdf,
        )

    def _tenant(self, tenant_id: str) -> TenantView:
        tenant = self.tenants.get(tenant_id)
        if tenant is None:
            raise ReceiptDecisionError("Tenant must complete onboarding first")
        return tenant

    @staticmethod
    def _authorize_receipt(tenant: TenantView, request: ReceiptIssueRequest) -> None:
        if request.actor_role != "admin":
            raise ReceiptDecisionError("Only a tenant admin can issue a receipt")
        if tenant.status is not AccountStatus.ACTIVE:
            raise ReceiptDecisionError("The tenant account must be active")
        if request.payment.tenant_id != tenant.tenant_id:
            raise ReceiptDecisionError("The payment does not belong to this tenant")
        if request.payment.status is not PaymentStatus.PAID:
            raise ReceiptDecisionError("Only paid payments can receive a receipt")

    @staticmethod
    def _receipt_html(tenant: TenantView, payment: Payment) -> str:
        amount = f"{payment.amount_minor / 100:.2f} {escape(payment.currency.upper())}"
        return (
            "<!doctype html><html><body>"
            "<h1>Payment receipt</h1>"
            f"<p>Customer: {escape(tenant.legal_name)}</p>"
            f"<p>Payment: {escape(payment.payment_id)}</p>"
            f"<p>Paid: {amount}</p>"
            f"<p>Date: {escape(payment.paid_at)}</p>"
            "</body></html>"
        )
