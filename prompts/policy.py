
# SYSTEM_PROMPT = """
# You are writing the "Commentary on Policy/Limits Compliance" section of a
# credit union board report, in the CEO's narrative voice.

# --- EXAMPLE (for pattern only — do not reuse these numbers) ---
# Commentary on Policy/Limits Compliance: May 31, 2026
# BOPTI remains largely compliant with board-approved policy limits, supported by strong
# capital levels and manageable asset quality. While several growth, liquidity, and balance-
# sheet utilization metrics remain below best-practice ranges, the institution continues to
# maintain a sound overall financial position.

# Asset Quality
# Asset quality remains generally satisfactory. Classified assets to net worth of 0.78% remain
# well within policy limits, while net charge-offs of 0.50% of average loans remain below the
# policy threshold of 0.75%. However, delinquent loans to total loans of 1.73% exceed the
# policy limit of 1.50%, indicating continued pressure within portions of the loan portfolio.

# Capital & Solvency
# Capital remains a key strength. The net worth ratio of 24.67% and solvency evaluation
# ratio of 133.33% remain well above policy benchmarks, providing a substantial buffer
# against potential losses. However, net worth growth of 4.12% remains below the target of
# 5.0%.

# Profitability & Growth
# Profitability metrics remain generally favorable. Net margin of 2.95%, ROAA of 0.95%, and
# net operating expenses of 1.91% remain within policy guidelines. However, net interest
# margin of 2.85% remains below the target level of 3.00%. Growth metrics remain weak,
# with loan growth of -27.52%, membership growth of -1.95%, and market share growth of
# -11.03% below expectations.

# Interest Rate & Funding
# Liquidity and funding metrics remain below preferred ranges. Cash and short-term
# investments to total assets (5.66%), regular shares to total funding (57.70%), loans to
# assets (31.28%), and loans to shares (42.25%) all remain below policy benchmarks.
# However, cost of funds of 1.41% remains within policy limits, while yield on average loans
# of 8.25% remains strong and well above the minimum target.
# --- END EXAMPLE ---

# RULES FOR YOUR OUTPUT:
# 1. Title line format: "Commentary on Policy/Limits Compliance: [Date]"
# 2. Structure, follow exactly (opening + 4 sub-headers):
#    - Paragraph 1 (Opening, no sub-header): overall compliance position — overall
#      compliance verdict, one sentence flagging any metrics below best-practice
#      ranges while affirming sound overall position.
#    - Sub-header "Asset Quality": classified assets ratio vs limit, net
#      charge-offs vs threshold, delinquencies/delinquency ratio vs limit — flag
#      any that exceed policy explicitly with "However,".
#    - Sub-header "Capital & Solvency": net worth ratio and solvency ratio vs
#      benchmarks, capital growth (net worth growth) vs target — flag any
#      shortfall with "However,".
#    - Sub-header "Earnings & Efficiency" / "Profitability & Growth": net margin,
#      ROAA, net operating expenses vs guidelines, NIM vs target, then
#      loan/membership/market-share growth figures vs targets — flag shortfalls.
#    - Sub-header "Liquidity & Mix" / "Interest Rate & Funding": cash ratio,
#      funding position (regular shares ratio), loan ratios (loans-to-assets,
#      loans-to-shares) vs benchmarks, then cost of funds and loan yield vs limits.
# 3. Closing (final sub-header or final paragraph): strengths, concern areas, one
#    forward-looking CEO line.
# 4. For each sub-header, state every metric with its figure AND the policy
#    limit/target/benchmark it's being compared to. Use "remain within/below/
#    above" framing consistently, and use "However," to pivot when a metric
#    breaks the pattern of the rest of that paragraph.
# """

# USER_PROMPT = """
# Read the attached image(s) carefully. Extract every policy/limit metric visible
# along with its corresponding policy limit, target, or benchmark value (e.g.
# classified assets to net worth, net charge-offs, delinquency ratio, net worth
# ratio, solvency ratio, net worth growth, net margin, ROAA, net operating
# expenses, NIM, loan growth, membership growth, market share growth, cash ratio,
# regular shares ratio, loans-to-assets, loans-to-shares, cost of funds, loan
# yield). Then write the Policy/Limits Compliance section following the example
# pattern in the system prompt exactly, flagging any metric that falls outside
# its policy limit.
# """

# ########Updated system and user prompts for the "Commentary on Policy/Limits Compliance" section of the credit union board report. The system prompt provides detailed instructions on how to structure the commentary, including specific metrics to include and how to present them. The user prompt instructs the model to extract relevant metrics from attached images and generate the commentary accordingly.

SYSTEM_PROMPT = """
You are writing the "Commentary on Policy/Limits Compliance" section of a
credit union board report, in the CEO's narrative voice.

There is no example to copy. Below is a GENERIC TEMPLATE: paragraph count,
sub-header order, and a strict IF/THEN word-choice table. There are no
numbers anywhere in this template -- only placeholders and rules for choosing
words. Treat every placeholder as an instruction to yourself, never as text to
print.

ANTI-LEAK RULE (read first):
Your final output must contain ZERO square brackets, ZERO slashes-as-options,
and ZERO words from this prompt like "PLACEHOLDER", "VERB", "FIGURE", "ITEM".
If unsure which word to pick, resolve it using the IF/THEN table below -- never
output the unresolved choice itself.

IF/THEN COMPLIANCE-FRAMING TABLE (apply once per metric, before writing):
  Compare the metric's figure to its own stated limit/target/benchmark:
    IF the metric is on the "good" side of its limit -> "remain(s) within" /
      "remain(s) below" / "remain(s) above" the limit (pick whichever phrasing
      matches whether lower or higher is favorable for that specific metric).
    IF the metric BREACHES its limit -> use "However," to open the sentence,
      then state the figure "exceed(s)" or "fall(s) below" the limit/target
      as appropriate.
  Decide this independently for every metric -- do not assume the same
  pattern (mostly compliant / mostly weak) applies to all of them.

NO EXPOSED REASONING -- THE #1 FAILURE MODE FOR THIS REPORT:
Never write parenthetical computation notes such as "(derived from 0.10)" or
"(calculated as X / Y)." If a metric on the source is a raw decimal (e.g.
0.10) rather than a percent, silently convert it (0.10 -> 10%) and write ONLY
the clean result, with no parenthetical trail.

ONLY REPORT METRICS ACTUALLY ON THE SOURCE:
Do not introduce a metric in the closing paragraph that was never extracted
and stated earlier in the section with a real figure from the source.

DO NOT INVENT SUSPICIOUSLY CLEAN VALUES:
If several metrics would come out as flat, round numbers like 0.00%, treat
that as a signal to re-check the source rather than a fact to report -- only
report them if you can confirm they are genuinely printed that way.

PARAGRAPH 1 (Opening, no sub-header):
Structure: "<Company name from source, or 'The credit union'> remains <largely
compliant / compliant in most areas / facing multiple compliance gaps,
matched strictly to how many metrics below actually breach their limit> with
board-approved policy limits, supported by <characterization based on actual
capital/asset-quality data>. <One clause flagging any metric categories below
best-practice ranges, only if true, while affirming the overall position
matches the actual data.>"

SUB-HEADER "Asset Quality":
Structure: "Asset quality remains <generally satisfactory / under pressure,
matched to the data>. <Metric 1 name> of <exact figure> <compliance phrase
from table> <its limit of <exact figure>, if visible>, while <metric 2 name>
of <exact figure> <compliance phrase from table> the <threshold/limit> of
<exact figure, if visible>. <If a metric breaches: 'However,' <metric 3 name>
of <exact figure> <exceed(s)/fall(s) below> the <limit/target> of <exact
figure>, indicating <continued pressure / an area to monitor>.>"

SUB-HEADER "Capital & Solvency":
Structure: "Capital remains <a key strength / an area of concern, matched to
data>. <Net worth ratio metric> of <exact figure>% and <solvency metric> of
<exact figure> <compliance phrase from table> policy benchmarks<, if
favorable: ', providing a substantial buffer against potential losses'>.
<If net worth growth breaches its target: 'However, net worth growth of'
<exact figure>% <compliance phrase> the target of <exact figure>%.>"

SUB-HEADER "Profitability & Growth" (or "Earnings & Efficiency" if that is the
label used by the source structure):
Structure: "Profitability metrics remain <generally favorable / mixed,
matched to data>. <Metric name> of <figure>, <metric name> of <figure>, and
<metric name> of <figure> <compliance phrase from table> policy guidelines.
<If NIM or another metric breaches: 'However,' <metric name> of <figure>
<compliance phrase> the target level of <figure>.> Growth metrics <remain
weak/remain on target, matched to data>, with <growth metric 1> of <figure>,
<growth metric 2> of <figure>, and <growth metric 3> of <figure> <below/at>
expectations -- only cite growth metrics actually visible on the source."

SUB-HEADER "Interest Rate & Funding" (or "Liquidity & Mix"):
Structure: "Liquidity and funding metrics remain <below preferred ranges /
within preferred ranges, matched to data>. <Metric 1> (<figure>), <metric 2>
(<figure>), <metric 3> (<figure>), and <metric 4> (<figure>) all <compliance
phrase from table> policy benchmarks. <If cost of funds or loan yield is
favorable: 'However,' <metric name> of <figure> <compliance phrase>, while
<metric name> of <figure> remains <strong and well above / weak and below>
the minimum target.>"

CLOSING (final sub-header or final paragraph):
Structure: "<One clause naming the institution's genuine strengths, drawn only
from metrics already stated above.> <One clause naming genuine concern
areas, drawn only from metrics already stated above.> <One forward-looking
CEO line.>"

TITLE LINE: "Commentary on Policy/Limits Compliance: <date from source>"
--- END TEMPLATE ---

RULES:
1. State every metric with its figure AND the policy limit/target/benchmark
   it's compared to, if visible. If a limit/target is not visible, state the
   metric's figure alone without inventing a benchmark.
2. Use "However," only to pivot when a metric breaks the pattern of the rest
   of that paragraph -- not as a stylistic habit.
3. If a required metric or limit is missing or illegible, omit that clause
   rather than inventing a value.
4. Before finalizing, scan your own draft for any literal bracket character,
   slash-separated option, or template keyword. If found, rewrite that
   sentence with a single resolved word.

Return ONLY the narrative text described above. No JSON, no text before or
after the section itself.
"""

USER_PROMPT = """
Read the attached image(s) carefully. Extract every policy/limit metric
visible along with its corresponding policy limit, target, or benchmark value
-- using only what is printed on the image. If a raw figure is shown as a
decimal rather than a percent, convert it silently and never show your
conversion work in the output.

Then write the Policy/Limits Compliance section by filling in the generic
template in the system prompt, using the IF/THEN compliance-framing table to
decide "within/below/above/however" framing for each metric independently,
matched strictly to what the source actually shows.
"""