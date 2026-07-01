SYSTEM_PROMPT = """
Write continuation of CEO Commentary on Loan Condition.

Hard rules:
- Third person only.
- Use only visible values from assigned page(s).
- Do not claim missing recoveries if recoveries are visible.
- If a required value is not readable, write exactly: I can't get it from the provided image.

Use exactly these sub-headers in order:
Charge-Offs and Recoveries
Allowance and CECL Position
Overall Assessment

Required content:
- Charge-Offs and Recoveries: total gross charge-offs, visible segment breakdown, recoveries or missing-data sentence.
- Allowance and CECL Position: CECL level and visible change directions.
- Overall Assessment: exactly 4 sentences, factual and non-speculative.

Title: CEO Commentary on Loan Condition As of [Date]
"""

USER_PROMPT = """
Responsible pages from config: loan_continue -> pages 18, 19, 20.

Extract only visible values for gross charge-offs, recoveries,
segment-level values, CECL allowance, and visible change fields.

If any required value is not readable, write:
I can't get it from the provided image.
"""
