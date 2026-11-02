export const CURRENCY_SYMBOLS: Record<string, string> = {
  USD: '$',
  INR: '₹',
  EUR: '€',
  GBP: '£',
  AED: 'AED ',
  CAD: 'CA$',
  AUD: 'AU$',
};

export function formatCurrency(
  amount: number | string | null | undefined,
  currency: string = 'USD'
): string {
  if (amount === null || amount === undefined || amount === '') {
    return `${CURRENCY_SYMBOLS[currency] || currency + ' '}0.00`;
  }
  const numeric = typeof amount === 'number' ? amount : parseFloat(amount);
  if (isNaN(numeric)) {
    return `${CURRENCY_SYMBOLS[currency] || currency + ' '}0.00`;
  }
  const symbol = CURRENCY_SYMBOLS[currency] || `${currency} `;
  return `${symbol}${numeric.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}
