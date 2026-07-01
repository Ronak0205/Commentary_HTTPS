SYSTEM_PROMPT = """
Write Commentary on Policy/Limits Compliance.

Hard rules:
- Third person only.
- Use only visible values, limits/targets, and statuses.
- Never mark compliance unless metric and limit are both visible.
- If a required value is not readable, write exactly: I can't get it from the provided image.

Use exactly this order:
opening summary paragraph
Asset Quality
Capital and Solvency
Profitability and Growth
Interest Rate and Funding
closing paragraph

Title: Commentary on Policy/Limits Compliance: [Date]
"""

USER_PROMPT = """
Responsible page from config: policy -> page 29.

Extract only visible policy metrics with value,
limit/target, and status.

If any required metric is not readable, write:
I can't get it from the provided image.
"""
