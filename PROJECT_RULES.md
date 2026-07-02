# Financial Commentary AI - Project Rules

Version: 1.0

---

# Project Objective

This project develops production-quality prompts that generate executive financial commentary for credit unions and community banks from structured financial statement data.

The objective is NOT to generate attractive writing.

The objective is to generate commentary that is:

- Factually correct
- Numerically accurate
- Internally consistent
- Executive focused
- Suitable for CEO and Board reporting
- Repeatable across institutions

Every prompt revision must improve quality without introducing regressions.

---

# Primary Goal

Transform financial tables into management commentary.

The commentary should answer:

- What changed?
- Why does it matter?
- What should management monitor?
- What are the business implications?

rather than simply describing numbers.

---

# Executive Audience

Assume every output will be read by:

- CEO
- CFO
- Board of Directors
- Executive Committee
- Regulators

Write accordingly.

---

# Writing Philosophy

The commentary should read like it was written by an experienced banking executive.

Never sound like:

- OCR extraction
- Data narration
- Financial statement footnotes
- AI-generated summaries

Every paragraph should provide interpretation, not just observation.

---

# Materiality Principle

Prioritize material movements.

Ignore insignificant fluctuations unless they explain a larger trend.

Avoid discussing immaterial line items simply because they exist.

---

# Evidence Rule

Every statement must be supported by source data.

Never invent:

- causes
- trends
- risks
- management decisions
- business strategies
- future expectations

unless directly supported.

If evidence is missing,
say less,
not more.

---

# Interpretation Hierarchy

Always follow this order:

Observation

↓

Evidence

↓

Business implication

↓

Management relevance

↓

Forward-looking consideration (only when justified)

Never stop at observation alone.

---

# Executive Commentary Principle

Do not merely describe numbers.

Explain why they matter.

Weak:

"Loans increased 5%."

Better:

"Loan growth strengthened earning assets while increasing exposure to credit risk."

---

# Section Independence

Each section should be complete on its own.

Avoid repeating identical explanations across multiple sections.

Each section should contribute new insight.

---

# Consistency Rules

Terminology must remain consistent.

Examples:

Use one naming convention.

Do not alternate between:

Shares
Deposits
Funding

unless appropriate.

Likewise:

Loans and Leases

should remain consistent.

---

# Numerical Validation Rules

Before producing commentary validate:

✓ Percentages

✓ Totals

✓ Ratios

✓ Growth rates

✓ Policy comparisons

✓ Unit conversions

Never trust calculated percentages without verification.

---

# Unit Consistency

Never mix

millions

thousands

billions

within the same explanation unless explicitly required.

Always verify conversions.

---

# Policy Validation

Never state:

Above target

Below target

Within policy

Outside policy

without comparing the actual numbers.

Never rely on wording alone.

---

# Percentage Validation

Never describe portfolio composition without calculating it.

Never estimate.

Never round excessively.

---

# Trend Validation

Only describe:

Increasing

Declining

Stable

Accelerating

Decelerating

when supported by multiple periods.

Avoid trend language from a single observation.

---

# Causation Rule

Do not assume cause.

Instead write

"may reflect"

"is consistent with"

"appears driven by"

only when evidence exists.

---

# Materiality Filter

Before mentioning any metric ask:

Would a CEO care?

If not,

omit it.

---

# Strategic Thinking

Whenever possible explain:

Liquidity implications

Capital implications

Profitability implications

Credit implications

Funding implications

Risk implications

instead of repeating figures.

---

# Executive Prioritization

Discuss important issues first.

Typical order:

Capital

Liquidity

Asset Quality

Profitability

Growth

Operations

Minor details last.

---

# Regression Prevention Rules

This project must never lose previously solved improvements.

Every prompt revision must preserve:

- factual accuracy
- mathematical validation
- executive tone
- section structure
- terminology
- business interpretation
- consistency

Do not sacrifice one quality to improve another.

---

# Regression Checklist

Before accepting any prompt revision verify:

□ Existing strengths remain intact

□ No solved issue has reappeared

□ No new contradictions introduced

□ No calculations became incorrect

□ No wording became more generic

□ Executive usefulness improved

□ Commentary remains evidence based

---

# Known Historical Regressions

Examples of regressions that must never return:

- Incorrect portfolio percentages
- Incorrect policy comparisons
- Wrong unit conversions
- Unsupported business explanations
- Data narration replacing interpretation
- Contradictory trend statements
- Repetition across sections
- Excessive discussion of immaterial movements
- Mixing QoQ and YoY without clarification
- Invented management conclusions

Whenever a new regression is discovered:

1. Add it to this document.
2. Explain why it occurred.
3. Add a permanent prevention rule.

This file is the single source of truth for quality standards.

---

# Prompt Improvement Rule

Claude should never rewrite prompts blindly.

Instead:

1. Identify the weakness.
2. Explain why it occurs.
3. Recommend the smallest effective prompt change.
4. Verify no regression is introduced.
5. Preserve all previous improvements.

Prompt evolution should be incremental, not destructive.

---

# Quality Standard

The benchmark is commentary suitable for inclusion in a real Board Report.

If forced to choose:

Accuracy > Interpretation > Executive insight > Style.

Style should never come at the expense of correctness.