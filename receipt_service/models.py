from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AccountStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class PaymentStatus(str, Enum):
    PAID = "paid"
    REFUNDED = "refunded"


class TenantOnboarding(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    tenant_id: str = Field(min_length=1)
    legal_name: str = Field(min_length=1)
    billing_email: str


class AccountChange(BaseModel):
    status: AccountStatus


class Payment(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    payment_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    amount_minor: int = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    paid_at: str = Field(min_length=1)
    status: PaymentStatus


class ReceiptIssueRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    actor_role: str = Field(min_length=1)
    payment: Payment


class TenantView(BaseModel):
    tenant_id: str
    legal_name: str
    billing_email: str
    status: AccountStatus


class ReceiptIssueResult(BaseModel):
    tenant_id: str
    payment_id: str
    receipt: dict[str, Any]

