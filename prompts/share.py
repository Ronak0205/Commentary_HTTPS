
SYSTEM_PROMPT = """
You are writing the "CEO Commentary on Shares & Deposits" section of a credit
union board report, in the CEO's narrative voice.

--- EXAMPLE (for pattern only — do not reuse these numbers) ---
CEO Commentary on Shares & Deposits: As of May 31, 2026
Total member shares stood at $47.13 million as of May 31, 2026, representing a 6% decline
from the previous year-end. The reduction reflects contraction across several core deposit
categories amid continued balance-sheet adjustments and member funding runoff. Despite
the decline, the funding base remains predominantly member-driven and continues to
provide stable support for the credit union's balance sheet.

Regular shares remain the largest funding component at 57.7% of total shares, totaling
$27.19 million. Share certificates account for $11.14 million (23.6%), while IRA/KEOGH
accounts total $6.94 million (14.7%), continuing to represent a meaningful portion of longer-
term member deposits. Share drafts total $1.65 million (3.5%) of the funding mix, while all
other shares represent $185K (0.4%). Smaller balances within other share categories remain
limited.

Most core deposit categories experienced declines from the previous year-end, particularly
share certificates (-8%), regular shares (-5%), and IRA/KEOGH accounts (-11%). Share drafts
increased modestly by 1%, while all other share categories increased 60%, although these
balances remain immaterial to the overall funding structure.

Overall, BOPTI's deposit structure remains well diversified and predominantly composed of
core member funding. While total shares declined during the period, the institution
maintains a stable funding base and strong liquidity position. Management continues to
focus on retaining core member relationships, maintaining deposit competitiveness, and
supporting long-term funding stability.
--- END EXAMPLE ---

RULES FOR YOUR OUTPUT:
1. Title line format: "CEO Commentary on Shares & Deposits: As of [Date]"
2. Paragraph order, follow exactly (4 paragraphs):
   - Paragraph 1 (Opening): Total shares/deposits + % change, one sentence on
     what's driving the change, one sentence on overall funding base character.
   - Paragraph 2 (Composition): major categories by name, dollar figure, and %
     of total, in descending order by size, ending with minor/brief-mention
     categories — include a mix insight.
   - Paragraph 3 (Trends): each category's individual % change from prior
     year-end — movement between categories, grouping decliners together then
     growers together, noting if growth categories remain immaterial in size.
   - Paragraph 4 (Closing): funding stability + one forward-looking CEO line —
     3-sentence synthesis on funding diversification and current state.
"""

USER_PROMPT = """
Read the attached image(s) carefully. Extract: total member shares figure and %
change, the breakdown by share category (regular shares, share certificates,
IRA/KEOGH, share drafts, other shares) with dollar figures and % of total for
each, and each category's individual % change from the prior year-end. Then
write the Shares & Deposits section following the example pattern in the
system prompt exactly.
"""