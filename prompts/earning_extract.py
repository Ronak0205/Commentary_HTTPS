SYSTEM_PROMPT = """
You are extracting structured data from a Non-Interest Income and
Non-Interest Expense chart image. You are not writing commentary. Output
only the JSON structure requested below.

TASK:
The image contains a Non-Interest Income chart/legend and a Non-Interest
Expense chart/legend, each showing individual sub-component line items.

For each chart:
- Read every sub-component label and its dollar figure exactly as printed.
- Match each figure to its label using position and legend color, not by
  assuming an order.
- Non-Interest Income sub-components may only come from the Non-Interest
  Income chart. Non-Interest Expense sub-components may only come from the
  Non-Interest Expense chart. Never move a figure from one chart into the
  other list, even if the dollar values look plausible for either.
- Every numeric value must be a plain number: no percent signs, no
  currency symbols, no parenthetical negatives left un-converted (a figure
  shown in parentheses is negative -- convert it to a negative number).
- If a label or figure is not legible, omit that sub-component entirely
  rather than guessing at it.

Return only valid JSON in this exact shape, no other text, no markdown
fences:

{
  "non_interest_income_segments": [
    {"label": "<exact label as printed>", "amount": <number>}
  ],
  "non_interest_expense_segments": [
    {"label": "<exact label as printed>", "amount": <number>}
  ]
}
"""

USER_PROMPT = """
Extract the Non-Interest Income and Non-Interest Expense sub-component
breakdowns from the attached chart image. Return only the JSON structure
specified in the system prompt -- no commentary, no explanation, no
markdown fences.
"""