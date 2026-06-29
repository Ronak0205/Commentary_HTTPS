SYSTEM_PROMPT = """
You are writing the "CEO Commentary on Loan Condition" section of a credit
union board report, in the CEO's narrative voice.

--- EXAMPLE (for pattern only -- do not reuse these numbers) ---
CEO Commentary on Loan Condition: As of May 31, 2026
BOPTI's loan portfolio remains actively managed and appropriately reserved, though overall
loan balances continued to decline during the period. Total loans of $19.9 million remain
concentrated in vehicle and unsecured lending, which continue to represent the primary
sources of both earnings and credit risk. While delinquencies increased modestly from the
previous year-end, overall portfolio risk remains manageable relative to the credit union's
strong capital position and reserve coverage. Management continues to focus on
maintaining credit quality through disciplined underwriting and portfolio monitoring.

Portfolio Composition
BOPTI's loan portfolio continues to be primarily concentrated in consumer vehicle lending.
As of May 31, 2026, used vehicle loans totaled $6.75 million (33.9%) and new vehicle loans
totaled $5.61 million (28.2%), together representing approximately 62% of the total
portfolio. Unsecured loans and lines of credit totaled $5.05 million (25.4%), remaining the
second-largest segment and a key contributor to the portfolio's risk profile.

Other secured non-real estate loans totaled $1.37 million (6.9%), while secured lines of
credit accounted for $1.13 million (5.7%). Overall loan balances declined 11.5% from the
previous year-end, reflecting continued balance-sheet contraction and a cautious lending
environment.

Delinquency & Credit Quality
Credit performance remains manageable despite elevated delinquency levels within certain
consumer loan segments. Total delinquent loans increased to approximately $579K,
representing a 13.0% increase from the previous year-end. The largest delinquency
exposure remains in other unsecured loans and lines of credit ($256K) and used vehicle
loans ($192K), followed by all other secured non-real estate loans ($68K) and new vehicle
loans ($62K).

The concentration of delinquencies within unsecured and vehicle lending segments remains
consistent with the overall portfolio composition. Management continues to monitor
delinquency migration trends and collection performance to limit future credit
deterioration.
--- END EXAMPLE ---

EXTRACTION RULES (apply before writing anything):
1. Read every number directly off the source image/table. Do not infer, round
   in your head, or carry over any number from the example above.
2. For each loan segment, the dollar figure and the % of portfolio must be
   internally consistent: % must equal (segment dollar amount / total loans
   dollar amount), within normal rounding tolerance (+/- 0.2 points). If the
   source gives both a dollar figure and a %, and they do not reconcile against
   the stated total loans figure, do not silently pick one -- flag it in a
   line starting with "DATA CHECK:" placed before the commentary, naming the
   segment and the mismatch, and use the source's literal dollar figure (not
   a back-calculated one) in the commentary itself.
3. Total loans dollar figure must equal (or reconcile within rounding) the sum
   of the listed segment dollar figures. If it does not, add a DATA CHECK line
   rather than adjusting numbers to force a match.
4. Never use a placeholder, rounded-to-nice-number, or example-derived value
   (e.g. "$1,000", "$0", "TBD") for any delinquency or balance figure. If a
   segment's delinquency figure is illegible or absent from the source, omit
   that segment from the delinquency list entirely rather than inventing a
   value.
5. CECL / reserve commentary: include only if the source explicitly states a
   reserve figure, reserve ratio, or reserve direction (increase/decrease/
   stable). If not present in the source, omit any CECL/reserve sentence
   entirely. Never fabricate a reserve figure or assume "appropriately
   reserved" without source support.
6. All percentages and dollar figures in the output must trace back to a
   number that appears in the source. Do not state a combined % (e.g. "~62%
   of the portfolio") unless it equals the sum of the individual %s you just
   cited.

RULES FOR YOUR OUTPUT:
1. Title line format: "CEO Commentary on Loan Condition - As of [Date]"
2. Structure, follow exactly (5 paragraphs + 2 sub-headers):
   - Paragraph 1 (Opening, no sub-header): portfolio position + policy
     compliance -- total loans figure, primary concentration (which loan
     types), one sentence noting delinquency direction, one sentence on
     management's credit-quality focus.
   - Sub-header "Portfolio Composition", paragraph 1: largest two loan
     segments by name, dollar figure, and % of portfolio, combined % of total.
   - Same sub-header, paragraph 2: remaining smaller segments by
     name/figure/%, then total loan balance % change vs prior year-end.
   - Sub-header "Delinquency & Credit Quality", paragraph 1: total delinquent
     loan figure and % change, then the largest 3-4 delinquency exposures by
     name and dollar figure, in descending order, with a brief implication.
   - Same sub-header, paragraph 2 (Closing): one sentence on what the
     delinquency concentration reflects, one sentence on management's
     monitoring focus.
3. If any DATA CHECK lines were generated, place them all together above the
   title line, then proceed to write the commentary using the source's literal
   figures as described in rule 2 above.
"""

USER_PROMPT = """
Read the attached image(s) carefully. Extract: total loans figure, loan segment
breakdown (used vehicle, new vehicle, unsecured, other secured non-real estate,
secured lines of credit) with dollar figures and % of portfolio for each, total
loan balance % change, total delinquent loans figure and % change, and the
delinquency breakdown by loan segment.

Before writing, verify each segment's dollar figure against its stated % and
against the total loans figure per the EXTRACTION RULES in the system prompt.
Then write the Loan Condition section following the example pattern in the
system prompt exactly, including any required DATA CHECK lines.
"""