import decimal
from apps.geography.models import ExchangeRate


class CurrencyConverter:
    """
    Financial currency conversion utility with Decimal precision.
    Queries the database exchange rates table and supports inverse rate derivation.
    """

    @staticmethod
    def get_rate(from_currency: str, to_currency: str) -> decimal.Decimal:
        from_cur = from_currency.upper().strip()
        to_cur = to_currency.upper().strip()

        if from_cur == to_cur:
            return decimal.Decimal('1.000000')

        # Direct pair
        direct = ExchangeRate.objects.filter(base_currency=from_cur, quote_currency=to_cur).first()
        if direct:
            return direct.rate

        # Inverted pair
        inverted = ExchangeRate.objects.filter(base_currency=to_cur, quote_currency=from_cur).first()
        if inverted and inverted.rate > 0:
            return decimal.Decimal('1.000000') / inverted.rate

        # Cross rate via USD fallback
        if from_cur != 'USD' and to_cur != 'USD':
            rate_from_usd = CurrencyConverter.get_rate(from_cur, 'USD')
            rate_usd_to = CurrencyConverter.get_rate('USD', to_cur)
            return (rate_from_usd * rate_usd_to).quantize(decimal.Decimal('0.000001'))

        # Standard baseline fallback if rates table has gap
        defaults = {
            ('USD', 'INR'): decimal.Decimal('86.500000'),
            ('INR', 'USD'): decimal.Decimal('0.011560'),
            ('EUR', 'USD'): decimal.Decimal('1.080000'),
            ('GBP', 'USD'): decimal.Decimal('1.280000'),
            ('AED', 'USD'): decimal.Decimal('0.272000'),
        }
        return defaults.get((from_cur, to_cur), decimal.Decimal('1.000000'))

    @staticmethod
    def convert(amount: decimal.Decimal, from_currency: str, to_currency: str) -> decimal.Decimal:
        if amount is None:
            return decimal.Decimal('0.00')
        rate = CurrencyConverter.get_rate(from_currency, to_currency)
        converted = (decimal.Decimal(str(amount)) * rate).quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)
        return converted

