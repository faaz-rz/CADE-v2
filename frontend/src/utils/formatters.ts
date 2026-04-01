/**
 * Global Presentation Formatters
 */

/**
 * Formats a raw number into Indian Rupees (e.g. 2100000 -> "₹21,00,000")
 */
export const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(amount);
};

/**
 * Formats a decimal or percentage value smoothly into a percentage string (e.g. 0.342 or 34.2 -> "34.2%")
 */
export const formatPct = (value: number): string => {
    // Determine if the value is already scaled by 100
    const scaledValue = value <= 1.0 && value >= -1.0 ? value * 100 : value;
    return `${scaledValue.toFixed(1)}%`;
};

/**
 * Formats an ISO standard date string cleanly into short string notation (e.g. "2025-01-15T00:00:00" -> "Jan 15, 2025")
 */
export const formatDate = (date: string): string => {
    const d = new Date(date);
    return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    }).format(d);
};
