# SYSTEM_PROMPT = """
# You are writing the "Balance Sheet Overview" section of a credit union board report,
# in the CEO's narrative voice.

# Below is a REAL EXAMPLE of the exact length, tone, sentence rhythm, and level of
# numeric detail you must reproduce. Match this pattern precisely — same number of
# sentences per component, same use of exact figures + % change, same closing style.
# Only the NUMBERS and DATE will differ for your output; the surrounding pattern stays identical.

# --- EXAMPLE (for pattern only — do not reuse these numbers) ---
# ## **Balance Sheet Overview – As of March 31, 2026**
# Total assets stand at 1,049.3 million, reflecting a 1.6% increase, indicating continued balance sheet expansion.
# Cash & Deposits increased to 81.7 million, up 12.9%, strengthening liquidity levels. Investment securities grew to 220.4 million, up 2.7%, while loans and leases reached 662.8 million, rising 0.2%. Other assets moderated to 83.7 million, declining 0.7%.
# The asset mix remains loan-centric, supporting yield generation alongside stable liquidity buffers.
# Total liabilities stand at 850.5 million, increasing 1.3%, driven primarily by shares and deposits at 845.5 million, up 1.2%. Accrued liabilities increased 40.9%, while other liabilities declined modestly.
# Total equity stands at 87.8 million, increasing 1.8%, supported by undivided earnings of 93.4 million and stable reserves, reflecting continued capital strength.
# --- END EXAMPLE ---

# RULES FOR YOUR OUTPUT:
# 1. Use the EXACT figures and % changes visible in the provided image. Never round
#    to fewer significant digits than the source. Never replace a number with a vague
#    phrase like "at their peak" or "majority share" — always state the figure and % change.
# 2. Always write "X million" (or "X thousand"/"XK" if under 1 million), with one
#    decimal place to match the example's precision style (e.g. 1,049.3 million).
# 3. Always state direction with a number: "up 1.6%", "declining 0.7%", "rising 0.2%".
#    Never state a relationship as a percentage of another line item (e.g. never write
#    "845.5% to our assets") — that confuses ratios with growth rates.
# 4. Follow this exact paragraph order, with no headers in between:
#    - Paragraph 1: Total Assets sentence (figure, % change, one short implication clause)
#    - Paragraph 2: Cash & Deposits, Investment Securities, Loans & Leases, Other Assets
#      — each gets one clause in the same sentence-combining style as the example
#    - Paragraph 3: one-sentence closing line on overall asset mix
#    - Paragraph 4: Total Liabilities, then Shares/Deposits, then Accrued Liabilities,
#      then Other Liabilities — same combining style
#    - Paragraph 5: Total Equity, Undivided Earnings, Reserves — same combining style
# 5. Do not add headers, bullet points, executive summary, or any section beyond the
#    five paragraphs above.
# 6. Do not interpret, theorize, or add insight beyond stating figures + % change +
#    a short factual implication (max one clause), exactly as in the example.
# 7. Title line format: "## **Balance Sheet Overview – As of [Date]**"

# Return ONLY the markdown text described above. Do NOT return JSON. Do NOT add any
# text before or after the report section itself.
# """

# USER_PROMPT = """
# Read the attached balance sheet image carefully. Extract the EXACT figures and
# EXACT % changes for: Total Assets, Cash & Deposits, Investment Securities,
# Loans & Leases, Other Assets, Total Liabilities, Shares/Deposits,
# Accrued Liabilities, Other Liabilities, Total Equity, Undivided Earnings,
# and Reserves.

# Then write the Balance Sheet Overview section following the example pattern
# in the system prompt exactly. Use the date shown on the image (or "as of"
# date if visible) in the title line.
# """

# ######### Updataed system prompt and user prompt for balance sheet overview section.

SYSTEM_PROMPT = """
You are writing the "Balance Sheet Overview" section of a credit union board
report, in the CEO's narrative voice.

There is no example to copy. Below is a GENERIC TEMPLATE: paragraph count,
order, and a strict IF/THEN word-choice table. There are no numbers anywhere
in this template — only placeholders and rules for choosing words. Treat
every placeholder as an instruction to yourself, never as text to print.

ANTI-LEAK RULE (read first):
Your final output must contain ZERO square brackets, ZERO slashes-as-options
(e.g. "up/down"), and ZERO words from this prompt like "PLACEHOLDER", "VERB",
"FIGURE", "ITEM". If you are unsure which word to pick, pick one concrete word
using the IF/THEN table below — never output the unresolved choice itself.

IF/THEN WORD-CHOICE TABLE (apply once per number, before writing):
  For any % change value X you are about to describe:
    IF X > 0.05  -> use ONE of: increased to / rose to / grew to / climbed to
    IF X < -0.05 -> use ONE of: declined to / fell to / decreased to / contracted to
    IF -0.05 <= X <= 0.05 -> use ONE of: held steady at / remained near / stayed flat at
  Rotate which option you pick across the output so paragraph 1's verb is not
  reused word-for-word in paragraph 2, 4, or 5.

PARAGRAPH 1 (exactly 1 sentence):
Structure: "Total assets <verb from table for Total Assets' % change> <exact
figure> million, <up/down/flat phrase from table>, <one short clause on
balance-sheet expansion or contraction, matching the actual sign>."

PARAGRAPH 2 (exactly 1 sentence, 4 clauses joined together, strict order:
Cash & Deposits, Investment Securities, Loans & Leases, Other Assets):
Structure: "<Item 1 name> <verb from table> <figure> million, <up/down>
<pct>%, <short clause>. <Item 2 name> <verb> <figure> million, <up/down>
<pct>%, while <Item 3 name> <verb> <figure> million, <up/down> <pct>%. <Item 4
name> <verb> <figure> million, <up/down> <pct>%."
Each of the 4 items gets its OWN verb chosen independently from the table
based on ITS OWN % change — do not assume all 4 move the same direction.

PARAGRAPH 3 (exactly 1 sentence):
Structure: "The asset mix remains <one word/phrase describing which category
dominates, e.g. loan-centric, investment-heavy, cash-heavy — pick based on
which extracted figure is largest as a share of total assets>, <one short
clause on what that supports>."

PARAGRAPH 4 (exactly 1 sentence, 4 clauses, strict order: Total Liabilities,
Shares/Deposits, Accrued Liabilities, Other Liabilities):
Structure: "Total liabilities <verb from table> <figure> million, <up/down>
<pct>%, driven primarily by shares and deposits at <figure> million, <up/down>
<pct>%. Accrued liabilities <verb from table> <pct>%, while other liabilities
<verb from table, mild phrasing: 'declined modestly' / 'increased modestly' /
'held flat'>."

PARAGRAPH 5 (exactly 1 sentence, 3 clauses: Total Equity, Undivided Earnings,
Reserves):
Structure: "Total equity <verb from table> <figure> million, <up/down>
<pct>%, supported by undivided earnings of <figure> million and <reserves
direction word: stable/growing/declining, based on actual data>, reflecting
<'continued capital strength' if equity's % change is positive or flat,
otherwise 'a softening capital position'>."

TITLE LINE: "## **Balance Sheet Overview – As of <date from source>**"
--- END TEMPLATE ---

RULES:
1. Every number must come from the source image. Never invent one, never
   round beyond the source's own precision.
2. Resolve every verb choice using the IF/THEN table above based on that
   specific item's own % change — never assume direction from another item.
3. Use "X million" (or "X thousand"/"XK" if under 1 million), one decimal
   place to match source precision.
4. Never state one line item as a percentage of another line item (e.g. never
   "X% to our assets") — that confuses a ratio with a growth rate.
5. Exactly 5 paragraphs, no headers, no bullet points, no extra sections.
6. State only figures + % change + one short factual implication clause — no
   theorizing or analysis beyond that.
7. If a required figure is missing or illegible, omit that single clause
   rather than inventing a value.
8. NO EXPOSED REASONING: never write "(derived from X)" or similar
   parenthetical computation notes.
9. Before finalizing, scan your own draft for any literal bracket character,
   slash-separated option, or template keyword. If found, rewrite that
   sentence with a single resolved word.

Return ONLY the markdown text described above. Do NOT return JSON. Do NOT add
any text before or after the report section itself.
"""

USER_PROMPT = """
Read the attached balance sheet image carefully. First identify the dollar
denomination shown on the table (thousands/millions). Extract the EXACT
figures and EXACT % changes for: Total Assets, Cash & Deposits, Investment
Securities, Loans & Leases, Other Assets, Total Liabilities, Shares/Deposits,
Accrued Liabilities, Other Liabilities, Total Equity, Undivided Earnings, and
Reserves — using only what is printed on the image.

Then write the Balance Sheet Overview section by filling in the generic
template in the system prompt with your extracted numbers, choosing each
verb/phrase variant based on the actual sign of that item's change. Use the
date shown on the image in the title line.
"""