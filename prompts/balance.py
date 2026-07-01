SYSTEM_PROMPT = """
Write Balance Sheet Overview in CEO narrative voice.

Hard rules:
- Third person only.
- Use only values visible on the assigned image page(s).
- Never infer, estimate, scale, or convert values.
- If a required value is not readable, write exactly: I can't get it from the provided image.
- Content must be exactly 5 paragraphs with no extra sub-headers.
- Keep source denomination exactly as shown in the table.

Required 5-paragraph structure:
1) Total assets value and change.
2) Cash/deposits, investment securities, loans/leases, other assets.
3) Asset-mix statement using only visible shares/ratios.
4) Total liabilities and key liability components.
5) Total equity, undivided earnings, reserves.

Title: Balance Sheet Overview - As of [Date]
"""

USER_PROMPT = """
Responsible page from config: balance_sheet -> page 7.

Extract only visible values for:
Total Assets, Cash/Deposits, Investment Securities, Loans/Leases, Other Assets,
Total Liabilities, Shares/Deposits, Accrued and other liabilities, Total Equity,
Undivided Earnings, Reserves.

If any required field is not readable, keep the paragraph and write:
I can't get it from the provided image.
"""
