import pytest

from receipt_service.models import AccountStatus, Payment, PaymentStatus, ReceiptIssueRequest, TenantOnboarding
from receipt_service.receipt_sender import ReceiptDecisionError, ReceiptService


class RecordingGateway:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def generate_receipt(self, html: str, payment_id: str) -> dict:
        self.calls.append((html, payment_id))
        return {"job_id": "job-receipt-42"}


def paid_request() -> ReceiptIssueRequest:
    return ReceiptIssueRequest(
        tenant_id="tenant-acme",
        actor_role="admin",
        payment=Payment(
            payment_id="pay-42",
            tenant_id="tenant-acme",
            amount_minor=4900,
            currency="usd",
            paid_at="2026-09-06",
            status=PaymentStatus.PAID,
        ),
    )


def test_suspended_tenant_cannot_issue_a_receipt() -> None:
    gateway = RecordingGateway()
    service = ReceiptService(gateway)
    service.onboard(TenantOnboarding(tenant_id="tenant-acme", legal_name="Acme Ltd", billing_email="billing@acme.example"))
    service.change_account("tenant-acme", AccountStatus.SUSPENDED)

    with pytest.raises(ReceiptDecisionError, match="account must be active"):
        service.issue(paid_request())

    assert gateway.calls == []


def test_active_tenant_admin_gets_a_receipt_request() -> None:
    gateway = RecordingGateway()
    service = ReceiptService(gateway)
    service.onboard(TenantOnboarding(tenant_id="tenant-acme", legal_name="Acme Ltd", billing_email="billing@acme.example"))

    result = service.issue(paid_request())

    assert result.receipt == {"job_id": "job-receipt-42"}
    assert gateway.calls[0][1] == "pay-42"
    assert "49.00 USD" in gateway.calls[0][0]

