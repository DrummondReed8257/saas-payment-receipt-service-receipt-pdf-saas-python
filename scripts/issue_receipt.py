from receipt_service.infrai_pdf import InfraiPdfClient
from receipt_service.models import Payment, PaymentStatus, ReceiptIssueRequest, TenantOnboarding
from receipt_service.receipt_sender import ReceiptService


def main() -> None:
    service = ReceiptService(InfraiPdfClient())
    service.onboard(
        TenantOnboarding(
            tenant_id="tenant-acme",
            legal_name="Acme Analytics Ltd",
            billing_email="billing@acme.example",
        )
    )
    result = service.issue(
        ReceiptIssueRequest(
            tenant_id="tenant-acme",
            actor_role="admin",
            payment=Payment(
                payment_id="pay-2026-0042",
                tenant_id="tenant-acme",
                amount_minor=4900,
                currency="usd",
                paid_at="2026-09-06",
                status=PaymentStatus.PAID,
            ),
        )
    )
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()

