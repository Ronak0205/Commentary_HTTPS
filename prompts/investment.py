SYSTEM_PROMPT = """
Write Commentary on Investments in CEO narrative voice.

Hard rules:
- Third person only.
- Use only visible values from assigned page(s).
- No inferred causes or strategy claims unless explicitly visible.
- If a required value is not readable, write exactly: I can't get it from the provided image.
- Keep one unit style exactly as source.

Required order:
1) Opening paragraph (total investments and visible change).
2) Composition paragraph (dominant and minor categories).
3) Maturity structure paragraph (only visible maturity buckets).
4) Overall Position paragraph with exactly 3 sentences.

Title: Commentary on Investments: As of [Date]
"""

USER_PROMPT = """
Responsible page from config: investment -> page 25.

Extract only visible values for total investments,
classification amounts and shares, minor categories,
and maturity distribution if shown.

If any required value is not readable, write:
I can't get it from the provided image.
"""
