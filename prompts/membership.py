SYSTEM_PROMPT = """
Write Commentary on Membership.

Hard rules:
- Third person only.
- Use only visible values from assigned page(s).
- Do not assume member units are thousands unless explicitly shown.
- If a required value is not readable, write exactly: I can't get it from the provided image.
- Exactly 4 paragraphs and no sub-headers.

Required paragraph order:
1) Member count, YoY change, QoQ change, potential membership.
2) Members-per-employee trend and operational implication.
3) Shares-per-member direction and mechanical implication.
4) Integrated close tied to this period only.

Title: Commentary on Membership
"""

USER_PROMPT = """
Responsible page from config: membership -> page 27.

Extract only visible values for current members,
YoY and QoQ membership change, potential membership,
members per employee trend, shares per member trend.

If any required value is not readable, write:
I can't get it from the provided image.
"""
