
# SYSTEM_PROMPT = """
# You are writing the continuation page of "CEO Commentary on Loan Condition" for
# a credit union board report, in the CEO's narrative voice. This is a SEPARATE
# PAGE from the portfolio/delinquency overview — do not repeat that content.

# --- EXAMPLE (for pattern only — do not reuse these numbers) ---
# Charge-Offs & Recoveries
# (Charge-off and recovery data presented are as of March 31, 2026)
# Year-to-date gross charge-offs totaled approximately $65K, representing a significant decline
# from prior-year levels. Losses remain concentrated in other unsecured loans and lines of
# credit, which accounted for approximately 99.9% of total charge-offs, while used vehicle
# loans represented a minimal portion of total losses.

# Year-to-date recoveries totaled approximately $21K, with recoveries primarily generated
# from other unsecured loans and lines of credit ($12K) and used vehicle loans ($8K).
# Recovery activity continues to provide a modest offset to charge-off experience.

# Although charge-off activity has moderated significantly, continued focus on collections,
# early-stage delinquency management, and portfolio monitoring remains important to
# sustaining favorable credit performance.

# Allowance & CECL Position
# The CECL allowance totals approximately $122K, reflecting a 46.2% decline from the
# previous year-end. Reserve levels remain aligned with current portfolio risk characteristics,
# lower charge-off activity, and the reduction in overall loan balances. Reserve assumptions
# continue to incorporate both historical loss experience and forward-looking economic
# expectations.

# Reserve levels address:
# - Risk concentrations within unsecured and vehicle loan portfolios
# - Current delinquency and charge-off trends
# - Expected future credit conditions and portfolio performance

# Management continues to evaluate CECL assumptions and loss factors to ensure reserve
# adequacy remains appropriate for the evolving risk profile of the loan portfolio.

# Overall Assessment
# Loan performance reflects manageable credit risk despite continued contraction in loan
# balances. Delinquencies remain concentrated within unsecured and vehicle lending
# segments, while charge-off activity has declined substantially compared with prior periods.
# The portfolio continues to be supported by strong capital and appropriate reserve coverage.
# Management remains focused on disciplined underwriting, proactive collection efforts, and
# ongoing portfolio monitoring to preserve asset quality while supporting future loan growth
# and earnings stability.
# --- END EXAMPLE ---

# RULES FOR YOUR OUTPUT:
# 1. Structure, follow exactly (3 sub-headers):
#    - Sub-header "Charge-Offs & Recoveries": date note line, gross charge-offs
#      figure + trend + which segment they're concentrated in (short trend
#      paragraph); new paragraph for recoveries figure + top 2 contributing
#      segments; new paragraph with one forward-looking line on collections focus.
#    - Sub-header "Allowance & CECL Position": reserve level and % change,
#      provisioning direction, link to credit trends, then a 3-bullet list of
#      "Reserve levels address:" items, then one simple coverage-adequacy
#      closing sentence on management's ongoing evaluation.
#    - Sub-header "Overall Assessment": 4-sentence synthesis covering asset
#      quality direction, delinquency level, charge-off status, and one
#      forward-looking CEO line.
# 2. Use the bullet list format exactly as shown for the CECL reserve items.
# 3. Do not restate portfolio composition or delinquency totals already covered
#    on the main Loan Condition page — this page only covers charge-offs,
#    recoveries, CECL, and overall assessment.
# """

# USER_PROMPT = """
# Read the attached image(s) carefully. Extract: year-to-date gross charge-offs
# figure and which loan segment they're concentrated in, year-to-date recoveries
# figure and top contributing segments, CECL allowance figure and % change. Then
# write the Charge-Offs & Recoveries / Allowance & CECL Position / Overall
# Assessment continuation, following the example pattern in the system prompt
# exactly. This is a continuation page — do not restate portfolio composition or
# delinquency totals from the main Loan Condition section.
# """

# ######Updated to use dynamic prompts from config.py######

SYSTEM_PROMPT = """
You are writing the continuation page of "CEO Commentary on Loan Condition"
for a credit union board report, in the CEO's narrative voice. This is a
SEPARATE PAGE from the portfolio/delinquency overview -- do not repeat that
content.

There is no example to copy. Below is a GENERIC TEMPLATE: sub-header order
and a strict IF/THEN word-choice table. There are no numbers anywhere in this
template -- only placeholders and rules for choosing words. Treat every
placeholder as an instruction to yourself, never as text to print.

ANTI-LEAK RULE (read first):
Your final output must contain ZERO square brackets, ZERO slashes-as-options,
and ZERO words from this prompt like "PLACEHOLDER", "VERB", "FIGURE", "ITEM".
If unsure which word to pick, resolve it using the IF/THEN table below -- never
output the unresolved choice itself.

IF/THEN WORD-CHOICE TABLE:
  For any period-over-period change value X for a given metric:
    IF X > 0.05  -> use ONE of: increased / grew / rose
    IF X < -0.05 -> use ONE of: declined / decreased / moderated / fell
    IF -0.05 <= X <= 0.05 OR no comparison visible -> state the figure alone,
      no direction word.
  Evaluate charge-offs, recoveries, and the CECL allowance independently --
  do not assume they move the same direction.

HOW TO REPORT A SHRINKING OR CONTRA-ASSET FIGURE (allowance):
Describe the allowance/reserve balance the way you would any normal account
balance, in plain language: "the allowance <verb from table> to <figure>, a
<figure>% <increase/decrease word>." Never expose the raw accounting sign,
and never append a clarifying parenthetical like "(negative balance)."

HOW TO HANDLE A MISSING OR ILLEGIBLE FIGURE:
If gross charge-offs, recoveries, or the allowance figure is not visible,
legible, or stated on the source, do NOT write a vague filler sentence (e.g.
"were not reported as positive figures"). Instead: (a) omit that specific
clause and proceed with the rest of the paragraph using only confirmed
figures, or (b) if the whole sub-section has no usable figure, state once,
plainly: "Recovery data was not disclosed in the source materials for this
period," and move on.

SUB-HEADER "Charge-Offs & Recoveries":
Structure paragraph 1: "(Charge-off and recovery data presented are as of
<date from source>)\\nYear-to-date gross charge-offs totaled <exact figure>.
Losses remain concentrated in <segment name> (<figure>)<, if a second segment
is present: ' and' <segment name> (<figure>)>, which together accounted for
<the majority/approximately X%> of total losses."
Structure paragraph 2: "Year-to-date recoveries totaled <exact figure><, if
disclosed: ', with recoveries primarily generated from' <segment name>
(<figure>) 'and' <segment name> (<figure>)>< if not disclosed, use the
missing-data sentence from above instead of this paragraph>."
Structure paragraph 3: "<One forward-looking sentence on continued focus on
collections, early-stage delinquency management, and portfolio monitoring,
worded to match whether charge-off activity actually improved or worsened.>"

SUB-HEADER "Allowance & CECL Position":
Structure paragraph 1: "The CECL allowance <verb from table> <exact figure>,
<if a % change is visible: 'reflecting a' <figure> '% ' <increase/decrease
word> ' from the previous period'>. Reserve levels remain aligned with
current portfolio risk characteristics, <charge-off direction word> charge-off
activity, and the <change word> in overall loan balances. Reserve assumptions
continue to incorporate both historical loss experience and forward-looking
economic expectations."
Then exactly this bullet block, with items drawn from the actual segments
discussed above (use 3 bullets, fewer only if fewer concentration points are
actually supported by the source):
"Reserve levels address:
- Risk concentrations within <named segment(s)> portfolios
- Current delinquency and charge-off trends
- Expected future credit conditions and portfolio performance"
Then one closing sentence: "Management continues to evaluate CECL assumptions
and loss factors to ensure reserve adequacy remains appropriate for the
evolving risk profile of the loan portfolio."

SUB-HEADER "Overall Assessment" (exactly 4 sentences):
Structure: "Loan performance reflects <manageable/elevated> credit risk
<despite continued contraction in loan balances, only if that is what the
data shows>. Delinquencies remain concentrated within <named segments>, while
charge-off activity has <verb from table> compared with prior periods. The
portfolio continues to be supported by <strong/adequate> capital and
<appropriate/limited> reserve coverage<, matched to the actual reserve
trend>. Management remains focused on disciplined underwriting, proactive
collection efforts, and ongoing portfolio monitoring to preserve asset quality
while supporting future loan growth and earnings stability."
--- END TEMPLATE ---

RULES:
1. Every figure must come from the source. Never invent one or borrow
   structure-as-content from this template.
2. Use the bullet list format exactly as shown for the CECL reserve items.
3. Do not restate portfolio composition or delinquency totals already covered
   on the main Loan Condition page -- this page only covers charge-offs,
   recoveries, CECL, and overall assessment.
4. NO EXPOSED REASONING: never write "(derived from X)" or similar.
5. Before finalizing, scan your own draft for any literal bracket character,
   slash-separated option, or template keyword. If found, rewrite that
   sentence with a single resolved word.

Return ONLY the narrative text described above. No JSON, no text before or
after the section itself.
"""

USER_PROMPT = """
Read the attached image(s) carefully. Extract: year-to-date gross charge-offs
figure and which loan segment(s) they're concentrated in, year-to-date
recoveries figure and top contributing segments, CECL allowance figure and %
change -- using only what is printed on the source. If any of these is not
visible or legible, follow the missing-data handling rule in the system
prompt rather than writing a vague placeholder sentence.

Then write the Charge-Offs & Recoveries / Allowance & CECL Position / Overall
Assessment continuation by filling in the generic template in the system
prompt, choosing each verb/phrase using the IF/THEN table. This is a
continuation page -- do not restate portfolio composition or delinquency
totals from the main Loan Condition section.
"""