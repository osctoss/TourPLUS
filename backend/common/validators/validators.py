import decimal
from django.core.exceptions import ValidationError


def validate_positive_amount(value: decimal.Decimal) -> None:
    if value < decimal.Decimal('0.00'):
        raise ValidationError('Amount must be non-negative.')


def validate_currency_code(code: str) -> None:
    if not code or len(code) != 3 or not code.isupper():
        raise ValidationError('Currency code must be a 3-letter ISO-4217 uppercase string.')

