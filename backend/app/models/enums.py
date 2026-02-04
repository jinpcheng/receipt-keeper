import enum


class ReceiptCategory(str, enum.Enum):
    gas = "gas"
    food = "food"
    office = "office"
    travel = "travel"
    lodging = "lodging"
    entertainment = "entertainment"
    medical = "medical"
    personal = "personal"
    other = "other"


class PaymentType(str, enum.Enum):
    credit_card = "credit_card"
    debit_card = "debit_card"
    cash = "cash"
    transfer = "transfer"
    mobile_pay = "mobile_pay"
    other = "other"


class CardType(str, enum.Enum):
    visa = "visa"
    mastercard = "mastercard"
    amex = "amex"
    discover = "discover"
    other = "other"
    unknown = "unknown"


class ReceiptStatus(str, enum.Enum):
    draft = "draft"
    confirmed = "confirmed"


class ExtractionStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
