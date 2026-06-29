
SYSTEM_PROMPT = """
You are writing the continuation page of "CEO Commentary on Loan Condition" for
a credit union board report, in the CEO's narrative voice. This is a SEPARATE
PAGE from the portfolio/delinquency overview — do not repeat that content.

--- EXAMPLE (for pattern only — do not reuse these numbers) ---
Charge-Offs & Recoveries
(Charge-off and recovery data presented are as of March 31, 2026)
Year-to-date gross charge-offs totaled approximately $65K, representing a significant decline
from prior-year levels. Losses remain concentrated in other unsecured loans and lines of
credit, which accounted for approximately 99.9% of total charge-offs, while used vehicle
loans represented a minimal portion of total losses.

Year-to-date recoveries totaled approximately $21K, with recoveries primarily generated
from other unsecured loans and lines of credit ($12K) and used vehicle loans ($8K).
Recovery activity continues to provide a modest offset to charge-off experience.

Although charge-off activity has moderated significantly, continued focus on collections,
early-stage delinquency management, and portfolio monitoring remains important to
sustaining favorable credit performance.

Allowance & CECL Position
The CECL allowance totals approximately $122K, reflecting a 46.2% decline from the
previous year-end. Reserve levels remain aligned with current portfolio risk characteristics,
lower charge-off activity, and the reduction in overall loan balances. Reserve assumptions
continue to incorporate both historical loss experience and forward-looking economic
expectations.

Reserve levels address:
- Risk concentrations within unsecured and vehicle loan portfolios
- Current delinquency and charge-off trends
- Expected future credit conditions and portfolio performance

Management continues to evaluate CECL assumptions and loss factors to ensure reserve
adequacy remains appropriate for the evolving risk profile of the loan portfolio.

Overall Assessment
Loan performance reflects manageable credit risk despite continued contraction in loan
balances. Delinquencies remain concentrated within unsecured and vehicle lending
segments, while charge-off activity has declined substantially compared with prior periods.
The portfolio continues to be supported by strong capital and appropriate reserve coverage.
Management remains focused on disciplined underwriting, proactive collection efforts, and
ongoing portfolio monitoring to preserve asset quality while supporting future loan growth
and earnings stability.
--- END EXAMPLE ---

RULES FOR YOUR OUTPUT:
1. Structure, follow exactly (3 sub-headers):
   - Sub-header "Charge-Offs & Recoveries": date note line, gross charge-offs
     figure + trend + which segment they're concentrated in (short trend
     paragraph); new paragraph for recoveries figure + top 2 contributing
     segments; new paragraph with one forward-looking line on collections focus.
   - Sub-header "Allowance & CECL Position": reserve level and % change,
     provisioning direction, link to credit trends, then a 3-bullet list of
     "Reserve levels address:" items, then one simple coverage-adequacy
     closing sentence on management's ongoing evaluation.
   - Sub-header "Overall Assessment": 4-sentence synthesis covering asset
     quality direction, delinquency level, charge-off status, and one
     forward-looking CEO line.
2. Use the bullet list format exactly as shown for the CECL reserve items.
3. Do not restate portfolio composition or delinquency totals already covered
   on the main Loan Condition page — this page only covers charge-offs,
   recoveries, CECL, and overall assessment.
"""

USER_PROMPT = """
Read the attached image(s) carefully. Extract: year-to-date gross charge-offs
figure and which loan segment they're concentrated in, year-to-date recoveries
figure and top contributing segments, CECL allowance figure and % change. Then
write the Charge-Offs & Recoveries / Allowance & CECL Position / Overall
Assessment continuation, following the example pattern in the system prompt
exactly. This is a continuation page — do not restate portfolio composition or
delinquency totals from the main Loan Condition section.
"""