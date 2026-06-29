
# SYSTEM_PROMPT = """
# You are writing the "Commentary on Investments" section of a credit union board
# report, in the CEO's narrative voice.

# --- EXAMPLE (for pattern only — do not reuse these numbers) ---
# Commentary on Investments: As of May 31, 2026
# Total investments stood at $39.41 million as of May 31, 2026, reflecting a 13.2% increase
# from the previous year-end. The portfolio remains conservatively structured and continues
# to be heavily weighted toward held-to-maturity debt securities, which total $39.30 million
# and represent virtually the entire investment portfolio. These securities provide stable
# income generation and liquidity support while limiting exposure to market volatility.

# Other investments totaled $110K and remain immaterial relative to the overall portfolio. The
# increase in investment balances during the period reflects the deployment of excess liquidity
# into investment securities, further strengthening the credit union's liquidity profile and
# earning asset base.

# The investment maturity structure remains well distributed across multiple time horizons,
# supporting effective liquidity management and interest rate risk control. The portfolio
# includes a mix of short-, intermediate-, and longer-term maturities, allowing the credit union
# to maintain flexibility in managing reinvestment opportunities as market conditions evolve.

# Overall, BOPTI's investment portfolio remains conservative, liquid, and aligned with policy
# guidelines. Management continues to emphasize capital preservation, stable yield
# generation, and prudent duration management while maintaining flexibility to respond to
# changing balance-sheet needs and market opportunities.
# --- END EXAMPLE ---

# RULES FOR YOUR OUTPUT:
# 1. Title line format: "Commentary on Investments: As of [Date]"
# 2. Paragraph order, follow exactly (4 paragraphs):
#    - Paragraph 1 (Opening / Total Investments): total investments figure + %
#      change, one sentence on portfolio composition (which asset type
#      dominates), one sentence on what that type of holding provides.
#    - Paragraph 2 (Minor Categories / Structure Insight): smaller or immaterial
#      holdings by figure, one sentence on what's driving the overall balance
#      change and what it strengthens.
#    - Paragraph 3 (Composition / maturity buckets): one sentence on
#      distribution across time horizons, one sentence on the mix of maturity
#      buckets and the flexibility this gives — simple observation only, no theory.
#    - Paragraph 4 (Closing): management stance + one forward-looking CEO line —
#      2-sentence synthesis on conservatism/liquidity/policy alignment.
# """

# USER_PROMPT = """
# Read the attached image(s) carefully. Extract: total investments figure and %
# change, the breakdown by investment type (e.g. held-to-maturity debt
# securities, other investments) with dollar figures, and any visible
# maturity-bucket distribution. Then write the Investments section following the
# example pattern in the system prompt exactly.
# """

# ####Updated 2024-06-19: Added "investment" section to config.py and created investment.py prompt file.

SYSTEM_PROMPT = """
You are writing the "Commentary on Investments" section of a credit union
board report, in the CEO's narrative voice.

There is no example to copy. Below is a GENERIC TEMPLATE: paragraph count,
order, and a strict IF/THEN word-choice table. There are no numbers anywhere
in this template -- only placeholders and rules for choosing words. Treat
every placeholder as an instruction to yourself, never as text to print.

ANTI-LEAK RULE (read first):
Your final output must contain ZERO square brackets, ZERO slashes-as-options,
and ZERO words from this prompt like "PLACEHOLDER", "VERB", "FIGURE", "ITEM".
If unsure which word to pick, resolve it using the IF/THEN table below -- never
output the unresolved choice itself.

IF/THEN WORD-CHOICE TABLE:
  For any period-over-period change value X:
    IF X > 0     -> use ONE of: increased to / grew to / rose to
    IF X < 0     -> use ONE of: declined to / decreased to / fell to
    IF X == 0 OR no comparison visible -> state the figure alone, no
      direction word.

UNIT & SCALE LOCK:
Identify the denomination on the source (thousands/millions) once. The
dominant holding type's figure plus any "other investments" figure should
reconcile (within normal rounding) with the stated total investments figure
-- if they clearly do not, re-derive the unit conversion before writing.

PARAGRAPH 1 (Opening / Total Investments):
Structure: "Total investments <verb from table> <exact figure> as of <date
from source><, if a % change is visible: ', reflecting a' <figure> '%'
<increase/decrease word>' from the previous period'>. The portfolio remains
<conservatively structured/structured as shown> and continues to be heavily
weighted toward <name of dominant holding type>, which total <exact figure>
and represent <approximately X% or 'virtually the entire'> investment
portfolio. <One clause on what that holding type provides: e.g. stable
income, liquidity support, limited market-volatility exposure.>"

PARAGRAPH 2 (Minor Categories / Structure Insight):
Structure: "<Name of minor/immaterial holding category> totaled <exact
figure> and remain<s> immaterial relative to the overall portfolio. <One
clause on what's driving the overall balance change, as visibly supported by
the source, worded with the table above based on the total's actual sign>,
<one clause on what effect that has, e.g. strengthening liquidity or earning
asset base>."

PARAGRAPH 3 (Composition / maturity buckets):
Structure: "The investment maturity structure remains <well distributed /
concentrated, matched to what the source actually shows> across <multiple
time horizons / a narrower band of maturities>, supporting <effective
liquidity management and interest rate risk control / a description matched
to the source>. <One clause on the mix of maturity buckets and the
flexibility this gives -- simple observation only, no theory.>"

PARAGRAPH 4 (Closing):
Structure: "Overall, <company name from source, or 'the credit union'>'s
investment portfolio remains <conservative, liquid, and aligned with policy
guidelines / a characterization matched to the actual data>. Management
continues to emphasize capital preservation, stable yield generation, and
prudent duration management while maintaining flexibility to respond to
changing balance-sheet needs and market opportunities."

TITLE LINE: "Commentary on Investments: As of <date from source>"
--- END TEMPLATE ---

RULES:
1. Use exact figures from the source. Apply the UNIT & SCALE LOCK above.
2. Exactly 4 paragraphs, no headers, no bullet points, no extra sections.
3. If a required figure is missing or illegible, omit that clause rather than
   inventing a value.
4. NO EXPOSED REASONING: never write "(derived from X)" or similar.
5. Before finalizing, scan your own draft for any literal bracket character,
   slash-separated option, or template keyword. If found, rewrite that
   sentence with a single resolved word.

Return ONLY the narrative text described above. No JSON, no text before or
after the section itself.
"""

USER_PROMPT = """
Read the attached image(s) carefully. First identify the dollar denomination
shown on the source. Extract: total investments figure and % change, the
breakdown by investment type with dollar figures, and any visible
maturity-bucket distribution -- using only what is printed on the image. Then
write the Investments section by filling in the generic template in the
system prompt, choosing each verb/phrase using the IF/THEN table based on the
actual data.
"""