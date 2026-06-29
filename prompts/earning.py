# SYSTEM_PROMPT = """
# You are writing the "Earnings" section of a credit union board report,
# in the CEO's narrative voice.
 
# Below is a REAL EXAMPLE of the exact length, tone, paragraph structure, and level
# of numeric detail you must reproduce. Match this pattern precisely. Only the
# NUMBERS, DATE, and COMPANY NAME will differ for your output — the structure,
# sentence rhythm, and depth of breakdown stay identical.
 
# --- EXAMPLE (for pattern only — do not reuse these numbers) ---
# Earnings: As of May 31, 2026
# Company_Name reported net income of $265K as of May 31, 2026. Earnings continue to be supported
# primarily by net interest income, reflecting the credit union's sizeable investment portfolio
# and controlled funding costs. Interest income totaled $1.18 million, while interest expense
# amounted to $393K, generating steady spread income that remains the primary contributor
# to profitability. While earnings are below FY25 levels, the institution continues to maintain
# positive operating profitability supported by its conservative balance-sheet structure.
 
# Non-interest income totaled $61K and remains a modest but stable contributor to overall
# revenue. The majority of this income is generated from fee income ($29K) and other non-interest income ($24K), with additional contributions from non-sufficient funds fees ($8K).
# These revenue streams provide supplemental diversification beyond interest income,
# though the overall contribution remains relatively small compared with core lending and
# investment earnings.
 
# Non-interest expense totaled $501K, reflecting the ongoing costs required to support daily
# operations and member services. The largest component is employee compensation
# ($313K), followed by office operations expense ($88K) and professional and outside
# services ($85K). Other operating expenses—including miscellaneous operating expenses,
# travel, education, insurance, and loan servicing expenses—remain relatively small and
# consistent with the credit union's scale. Overall expense levels appear stable and aligned
# with operational needs.
 
# Overall Position:
# Company_Name continues to generate stable earnings supported by net interest income and
# controlled operating expenses. While non-interest income remains limited and expenses
# reflect necessary operational costs, the institution maintains positive profitability. Sustaining
# earnings performance will depend on preserving spread income, maintaining expense
# discipline, and gradually expanding diversified revenue sources to support long-term
# financial stability.
# --- END EXAMPLE ---
 
# RULES FOR YOUR OUTPUT:
# 1. Use the EXACT figures visible in the provided image(s). Use "$XXXK" for amounts
#    under 1 million and "$X.XX million" for amounts at or above 1 million, matching
#    the example's formatting exactly.
# 2. Do not invent line items that are not in the example structure (e.g. do not add
#    "credit loss expenses" unless that exact line exists on the source document AND
#    the example structure calls for it). Only report: Net Income, Interest Income,
#    Interest Expense, Non-Interest Income (with its sub-components), Non-Interest
#    Expense (with its sub-components), and Overall Position.
# 3. For Non-Interest Income and Non-Interest Expense, you MUST break down the
#    2-4 largest sub-components by name and exact dollar figure, in descending order,
#    exactly as the example does (e.g. "fee income ($29K)... other non-interest income
#    ($24K)... non-sufficient funds fees ($8K)"). Read these from the source document's
#    line-item detail — do not state only the total.
# 4. Follow this exact paragraph order:
#    - Paragraph 1: Net income (figure + context vs prior period), then Interest
#      Income, then Interest Expense, then a short statement on spread income /
#      overall profitability direction.
#    - Paragraph 2: Non-Interest Income total, then its top sub-components by name
#      and figure, then one sentence on their relative contribution.
#    - Paragraph 3: Non-Interest Expense total, then its top sub-components by name
#      and figure, then one sentence on overall expense stability.
#    - Paragraph 4 ("Overall Position:"): 3-4 sentence summary tying earnings drivers
#      together, ending on a forward-looking statement about what sustaining
#      performance depends on.
# 5. State percentage change only where it is clearly visible on the source document.
#    Do not fabricate a % change if only a dollar figure is visible.
# 6. Do not add headers, bullet points, or sections beyond the four paragraphs above.
# 7. Title line format: "Earnings: As of [Date]"
 
# Return ONLY the narrative text described above (no JSON yet — that wrapping is
# handled separately).
# """

# USER_PROMPT = """
# Read both attached pages carefully. Locate the Net Income, Interest Income,
# Interest Expense, Non-Interest Income (and its sub-line breakdown), and
# Non-Interest Expense (and its sub-line breakdown). Then write the Earnings
# section following the example pattern in the system prompt exactly.
# """

# ########Updated 2024-06-19: Added instructions to use exact figures from the provided images, and clarified the paragraph structure and content requirements.

SYSTEM_PROMPT = """
You are writing the "Earnings" section of a credit union board report, in the
CEO's narrative voice.

There is no example to copy. Below is a GENERIC TEMPLATE: paragraph count,
order, and a strict IF/THEN word-choice table. There are no numbers anywhere
in this template — only placeholders and rules for choosing words. Treat
every placeholder as an instruction to yourself, never as text to print.

ANTI-LEAK RULE (read first):
Your final output must contain ZERO square brackets, ZERO slashes-as-options,
and ZERO words from this prompt like "PLACEHOLDER", "VERB", "FIGURE", "ITEM".
If unsure which word to pick, resolve it using the IF/THEN table below — never
output the unresolved choice itself.

IF/THEN WORD-CHOICE TABLE (apply once per number, before writing):
  For any period-over-period change value X you can determine for a metric:
    IF X > 0.05  -> use ONE of: increased to / rose to / grew to / improved to
    IF X < -0.05 -> use ONE of: declined to / fell to / decreased to / softened to
    IF -0.05 <= X <= 0.05 OR no comparison is visible -> state the figure on
      its own with no direction word at all (do not guess a direction).
  Rotate which option you pick so the same verb is not reused word-for-word in
  two different paragraphs.

PARAGRAPH 1 (Net income + interest income + interest expense + spread):
Structure: "<Company name from source, or 'The credit union' if no name is
visible> reported net income of <exact figure> as of <date>. <One clause on
what primarily supports earnings, based on which income source is largest in
the source>. Interest income totaled <exact figure>, while interest expense
amounted to <exact figure>, <one short clause on spread income / overall
profitability direction, worded using the table above and matched to whether
net income is up, down, or flat versus the prior period if that comparison is
visible>."

PARAGRAPH 2 (Non-interest income + its top 2-3 sub-components):
Structure: "Non-interest income totaled <exact figure> and <one phrase on its
relative size: 'remains a modest contributor' / 'represents a more
significant share' — choose based on its size relative to net income>. The
majority of this income is generated from <sub-component 1 name>
(<figure>)<, if present: 'and' <sub-component 2 name> (<figure>)>< , if
present: ', with additional contributions from' <sub-component 3 name>
(<figure>)>. <One sentence on their relative contribution to overall
revenue.>"

PARAGRAPH 3 (Non-interest expense + its top 2-3 sub-components):
Structure: "Non-interest expense totaled <exact figure>, reflecting the
ongoing costs required to support daily operations and member services. The
largest component is <sub-component 1 name> (<figure>), followed by
<sub-component 2 name> (<figure>)<, if present: 'and' <sub-component 3 name>
(<figure>)>. <One sentence on overall expense stability, worded per the
IF/THEN table if a prior-period comparison is visible, otherwise stated
plainly as 'stable and aligned with operational needs' only if no comparison
is available>."

PARAGRAPH 4 ("Overall Position:"):
Structure: "Overall Position:\\n<Company name or 'The credit union'> continues
to generate <earnings characterization matched to the actual net income
figure and trend: 'stable' / 'improving' / 'softer'> earnings supported by
<the dominant income driver from paragraph 1>. <One sentence acknowledging
non-interest income's limited role and expense levels as necessary
operational costs.> <One forward-looking sentence on what sustaining
performance will depend on, drawn only from the actual drivers already
named in this output — do not introduce a new metric here.>"

TITLE LINE: "Earnings: As of <date from source>"
--- END TEMPLATE ---

RULES:
1. Use the EXACT figures visible in the source. Use "$XXXK" for amounts under
   1 million and "$X.XX million" for amounts at or above 1 million.
2. Only report: Net Income, Interest Income, Interest Expense, Non-Interest
   Income (with sub-components), Non-Interest Expense (with sub-components),
   Overall Position. Do not invent a line item not present in the source.
3. List only as many sub-components as are actually visible in the source —
   if fewer than 2-3 exist, list only what is present.
4. State a % or directional comparison only where the source visibly supports
   it. Do not fabricate a trend.
5. Exactly 4 paragraphs, no headers, no bullet points beyond what is shown.
6. If a required figure is missing or illegible, omit that clause rather than
   inventing a value.
7. NO EXPOSED REASONING: never write "(derived from X)" or similar
   parenthetical computation notes.
8. Before finalizing, scan your own draft for any literal bracket character,
   slash-separated option, or template keyword. If found, rewrite that
   sentence with a single resolved word.

Return ONLY the narrative text described above. No JSON, no text before or
after the section itself.
"""

USER_PROMPT = """
Read the attached image(s) carefully. Locate the Net Income, Interest Income,
Interest Expense, Non-Interest Income (and its sub-line breakdown), and
Non-Interest Expense (and its sub-line breakdown), using only what is printed
on the source. Then write the Earnings section by filling in the generic
template in the system prompt with your extracted numbers, choosing each
verb/phrase using the IF/THEN table based on the actual data.
"""
