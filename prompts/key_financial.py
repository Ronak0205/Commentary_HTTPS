SYSTEM_PROMPT = """
Write Commentary on Key Financial Performance.

Hard rules:
- Third person only.
- Use only visible source metrics from assigned page(s).
- Keep metric format exactly as shown (percent, ratio, bps if explicitly shown).
- Never rescale values and never multiply percentages.
- If a required metric is not readable, write exactly: I can't get it from the provided image.

Required block order:
Opening
Capital and Solvency
Asset Quality
Profitability
Funding and Growth
Overall Position (exactly 3 sentences)

Title: Commentary on Key Financial Performance - [Date]
"""

USER_PROMPT = """
Responsible pages from config: key_financial -> pages 12, 13, 14.

Extract only visible values and shown changes for:
net worth ratio, solvency ratio, delinquent loans ratio, net charge-offs,
ROAA, NIM, net operating expenses ratio, loans-to-shares,
loan growth, shares/deposits growth, core funding ratio.

If any required metric is not readable, write:
I can't get it from the provided image.
"""
