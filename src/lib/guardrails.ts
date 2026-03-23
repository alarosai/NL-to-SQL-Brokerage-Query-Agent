export const DESTRUCTIVE_KEYWORDS = [
  'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE',
  'REPLACE', 'CREATE', 'RENAME', 'EXEC'
];

export const PII_KEYWORDS = ['SSN', 'SOCIAL SECURITY', 'PASSWORD', 'EMAIL', 'PHONE'];

export function checkGuardrails(query: string): { isValid: boolean, reason?: string } {
  const upperQuery = query.toUpperCase();

  // 1. Destructive statements
  for (const keyword of DESTRUCTIVE_KEYWORDS) {
    const regex = new RegExp(`\\b${keyword}\\b`, 'i');
    if (regex.test(query)) {
      return { 
        isValid: false, 
        reason: 'I can only run read-only queries on this database. Destructive operations are not permitted.' 
      };
    }
  }

  // 2. Out of scope / PII / Security
  for (const keyword of PII_KEYWORDS) {
    const regex = new RegExp(`\\b${keyword}\\b`, 'i');
    if (regex.test(query)) {
      if (keyword === 'PASSWORD' || keyword === 'ADMIN') {
         return { isValid: false, reason: 'I can only help with brokerage data queries.' };
      }
      return { isValid: false, reason: 'That field is not available in this dataset. PII is excluded.' };
    }
  }

  if (upperQuery.includes('ADMIN PASSWORD')) {
     return { isValid: false, reason: 'I can only help with brokerage data queries.' };
  }

  return { isValid: true };
}

export const DB_SCHEMA = `
Table: instruments
Columns: ticker (TEXT PRIMARY KEY), name (TEXT), asset_class (TEXT), exchange (TEXT)
Description: Real NASDAQ/NYSE tickers with company names

Table: prices
Columns: ticker (TEXT), date (TEXT), open (REAL), high (REAL), low (REAL), close (REAL), volume (INTEGER)
Description: Historical OHLCV market data

Table: accounts
Columns: account_id (INTEGER PRIMARY KEY), name (TEXT), country (TEXT), account_type (TEXT), created_at (TEXT)
Description: Synthetic brokerage accounts. Does NOT contain SSN, email, or passwords.

Table: orders
Columns: order_id (INTEGER PRIMARY KEY), account_id (INTEGER), ticker (TEXT), side (TEXT - 'buy' or 'sell'), qty (INTEGER), price (REAL), status (TEXT), created_at (TEXT)
Description: Historical trade orders

Table: positions
Columns: account_id (INTEGER), ticker (TEXT), shares_held (INTEGER), avg_cost (REAL), last_updated (TEXT)
Description: Aggregated positions derived from filled orders
`;
