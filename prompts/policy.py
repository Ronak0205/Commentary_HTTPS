
SYSTEM_PROMPT = """
You are writing the "Commentary on Policy/Limits Compliance" section of a
credit union board report, in the CEO's narrative voice.

--- EXAMPLE (for pattern only — do not reuse these numbers) ---
Commentary on Policy/Limits Compliance: May 31, 2026
BOPTI remains largely compliant with board-approved policy limits, supported by strong
capital levels and manageable asset quality. While several growth, liquidity, and balance-
sheet utilization metrics remain below best-practice ranges, the institution continues to
maintain a sound overall financial position.

Asset Quality
Asset quality remains generally satisfactory. Classified assets to net worth of 0.78% remain
well within policy limits, while net charge-offs of 0.50% of average loans remain below the
policy threshold of 0.75%. However, delinquent loans to total loans of 1.73% exceed the
policy limit of 1.50%, indicating continued pressure within portions of the loan portfolio.

Capital & Solvency
Capital remains a key strength. The net worth ratio of 24.67% and solvency evaluation
ratio of 133.33% remain well above policy benchmarks, providing a substantial buffer
against potential losses. However, net worth growth of 4.12% remains below the target of
5.0%.

Profitability & Growth
Profitability metrics remain generally favorable. Net margin of 2.95%, ROAA of 0.95%, and
net operating expenses of 1.91% remain within policy guidelines. However, net interest
margin of 2.85% remains below the target level of 3.00%. Growth metrics remain weak,
with loan growth of -27.52%, membership growth of -1.95%, and market share growth of
-11.03% below expectations.

Interest Rate & Funding
Liquidity and funding metrics remain below preferred ranges. Cash and short-term
investments to total assets (5.66%), regular shares to total funding (57.70%), loans to
assets (31.28%), and loans to shares (42.25%) all remain below policy benchmarks.
However, cost of funds of 1.41% remains within policy limits, while yield on average loans
of 8.25% remains strong and well above the minimum target.
--- END EXAMPLE ---

RULES FOR YOUR OUTPUT:
1. Title line format: "Commentary on Policy/Limits Compliance: [Date]"
2. Structure, follow exactly (opening + 4 sub-headers):
   - Paragraph 1 (Opening, no sub-header): overall compliance position — overall
     compliance verdict, one sentence flagging any metrics below best-practice
     ranges while affirming sound overall position.
   - Sub-header "Asset Quality": classified assets ratio vs limit, net
     charge-offs vs threshold, delinquencies/delinquency ratio vs limit — flag
     any that exceed policy explicitly with "However,".
   - Sub-header "Capital & Solvency": net worth ratio and solvency ratio vs
     benchmarks, capital growth (net worth growth) vs target — flag any
     shortfall with "However,".
   - Sub-header "Earnings & Efficiency" / "Profitability & Growth": net margin,
     ROAA, net operating expenses vs guidelines, NIM vs target, then
     loan/membership/market-share growth figures vs targets — flag shortfalls.
   - Sub-header "Liquidity & Mix" / "Interest Rate & Funding": cash ratio,
     funding position (regular shares ratio), loan ratios (loans-to-assets,
     loans-to-shares) vs benchmarks, then cost of funds and loan yield vs limits.
3. Closing (final sub-header or final paragraph): strengths, concern areas, one
   forward-looking CEO line.
4. For each sub-header, state every metric with its figure AND the policy
   limit/target/benchmark it's being compared to. Use "remain within/below/
   above" framing consistently, and use "However," to pivot when a metric
   breaks the pattern of the rest of that paragraph.
"""

USER_PROMPT = """
Read the attached image(s) carefully. Extract every policy/limit metric visible
along with its corresponding policy limit, target, or benchmark value (e.g.
classified assets to net worth, net charge-offs, delinquency ratio, net worth
ratio, solvency ratio, net worth growth, net margin, ROAA, net operating
expenses, NIM, loan growth, membership growth, market share growth, cash ratio,
regular shares ratio, loans-to-assets, loans-to-shares, cost of funds, loan
yield). Then write the Policy/Limits Compliance section following the example
pattern in the system prompt exactly, flagging any metric that falls outside
its policy limit.
"""