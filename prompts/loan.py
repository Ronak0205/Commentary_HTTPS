SYSTEM_PROMPT = """
Write CEO Commentary on Loan Condition.

Hard rules:
- Third person only.
- Use only visible values from assigned page(s).
- No CECL discussion in this section.
- Do not fabricate delinquency statements.
- If a required value is not readable, write exactly: I can't get it from the provided image.

Required structure:
1) Opening paragraph.
2) Portfolio Composition paragraph.
3) Delinquency and Credit Quality paragraph.

Title: CEO Commentary on Loan Condition - As of [Date]
"""

USER_PROMPT = """
Responsible pages from config: loan -> pages 16 and 17.

Extract only visible values for:
Total loans, top segment amounts and shares,
total delinquent loans, visible delinquent segment values.

If a required value is not readable, write:
I can't get it from the provided image.
"""
