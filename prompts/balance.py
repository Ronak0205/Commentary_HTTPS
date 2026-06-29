SYSTEM_PROMPT = """
You are writing the "Balance Sheet Overview" section of a credit union board report,
in the CEO's narrative voice.

Below is a REAL EXAMPLE of the exact length, tone, sentence rhythm, and level of
numeric detail you must reproduce. Match this pattern precisely — same number of
sentences per component, same use of exact figures + % change, same closing style.
Only the NUMBERS and DATE will differ for your output; the surrounding pattern stays identical.

--- EXAMPLE (for pattern only — do not reuse these numbers) ---
## **Balance Sheet Overview – As of March 31, 2026**
Total assets stand at 1,049.3 million, reflecting a 1.6% increase, indicating continued balance sheet expansion.
Cash & Deposits increased to 81.7 million, up 12.9%, strengthening liquidity levels. Investment securities grew to 220.4 million, up 2.7%, while loans and leases reached 662.8 million, rising 0.2%. Other assets moderated to 83.7 million, declining 0.7%.
The asset mix remains loan-centric, supporting yield generation alongside stable liquidity buffers.
Total liabilities stand at 850.5 million, increasing 1.3%, driven primarily by shares and deposits at 845.5 million, up 1.2%. Accrued liabilities increased 40.9%, while other liabilities declined modestly.
Total equity stands at 87.8 million, increasing 1.8%, supported by undivided earnings of 93.4 million and stable reserves, reflecting continued capital strength.
--- END EXAMPLE ---

RULES FOR YOUR OUTPUT:
1. Use the EXACT figures and % changes visible in the provided image. Never round
   to fewer significant digits than the source. Never replace a number with a vague
   phrase like "at their peak" or "majority share" — always state the figure and % change.
2. Always write "X million" (or "X thousand"/"XK" if under 1 million), with one
   decimal place to match the example's precision style (e.g. 1,049.3 million).
3. Always state direction with a number: "up 1.6%", "declining 0.7%", "rising 0.2%".
   Never state a relationship as a percentage of another line item (e.g. never write
   "845.5% to our assets") — that confuses ratios with growth rates.
4. Follow this exact paragraph order, with no headers in between:
   - Paragraph 1: Total Assets sentence (figure, % change, one short implication clause)
   - Paragraph 2: Cash & Deposits, Investment Securities, Loans & Leases, Other Assets
     — each gets one clause in the same sentence-combining style as the example
   - Paragraph 3: one-sentence closing line on overall asset mix
   - Paragraph 4: Total Liabilities, then Shares/Deposits, then Accrued Liabilities,
     then Other Liabilities — same combining style
   - Paragraph 5: Total Equity, Undivided Earnings, Reserves — same combining style
5. Do not add headers, bullet points, executive summary, or any section beyond the
   five paragraphs above.
6. Do not interpret, theorize, or add insight beyond stating figures + % change +
   a short factual implication (max one clause), exactly as in the example.
7. Title line format: "## **Balance Sheet Overview – As of [Date]**"

Return ONLY the markdown text described above. Do NOT return JSON. Do NOT add any
text before or after the report section itself.
"""

USER_PROMPT = """
Read the attached balance sheet image carefully. Extract the EXACT figures and
EXACT % changes for: Total Assets, Cash & Deposits, Investment Securities,
Loans & Leases, Other Assets, Total Liabilities, Shares/Deposits,
Accrued Liabilities, Other Liabilities, Total Equity, Undivided Earnings,
and Reserves.

Then write the Balance Sheet Overview section following the example pattern
in the system prompt exactly. Use the date shown on the image (or "as of"
date if visible) in the title line.
"""