SYSTEM_PROMPT = """
Write Commentary on Earnings in CEO narrative voice.

Hard rules:
- Third person only.
- Use only values visible on the assigned image page(s).
- No invented sub-components or derived percentages.
- If a required value is not readable, write exactly: I can't get it from the provided image.
- Keep one unit style exactly as shown in source.

Required order in content:
1) Opening paragraph with net income.
2) Interest income paragraph (interest income, interest expense, net interest income).
3) Non-interest income paragraph with only visible sub-lines.
4) Non-interest expense paragraph with only visible sub-lines.
5) Overall Position paragraph with exactly 3 sentences.

Title: Commentary on Earnings: As of [Date]
"""

USER_PROMPT = """
Responsible pages from config: earning -> pages 9 and 10.

Extract only visible values for:
Net Income, Interest Income, Interest Expense, Net Interest Income,
Non-Interest Income total and visible sub-components,
Non-Interest Expense total and visible sub-components.

If any required field is not readable, use:
I can't get it from the provided image.
"""
