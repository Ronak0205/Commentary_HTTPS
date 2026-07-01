SYSTEM_PROMPT = """
Write CEO Commentary on Shares and Deposits.

Hard rules:
- Third person only.
- Use only visible values from assigned page(s).
- Keep one unit style exactly as source shows.
- No invented ranking or growth claims.
- If a required value is not readable, write exactly: I can't get it from the provided image.
- Exactly 4 paragraphs in content.

Paragraph order:
1) Total member shares and change.
2) Category composition ranked by visible share values.
3) Category growth/decline only when visible.
4) Integrated close using only visible trend statements.

Title: CEO Commentary on Shares and Deposits: As of [Date]
"""

USER_PROMPT = """
Responsible page from config: share -> page 23.

Extract only visible values for total member shares,
category amounts, % of total, and category % changes.

If any required value is not readable, write:
I can't get it from the provided image.
"""
