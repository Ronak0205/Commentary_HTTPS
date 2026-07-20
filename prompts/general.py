DATA_CHECK_CONTAINMENT_RULE = """
DATA CHECK CONTAINMENT (strict): If you cannot reconcile a figure, you have
exactly two options: (1) silently use the figure you can verify and omit
the one you cannot, or (2) place a single DATA CHECK line above the title,
stating only the mismatch in one factual sentence (e.g. "DATA CHECK: loan
segment total does not reconcile with stated total loans figure"). Never
do either of these inside a body paragraph. Never expose your own
reasoning process about why a number might be wrong, what you compared it
against, or what you think the "real" figure should be -- no phrases like
"this appears to be," "note that," "however, based on," or "this indicates
a DATA CHECK." If a figure is unreconcilable, the reader sees either a
clean flag above the title or nothing at all -- never your working-out.
"""
BENCHMARK_TONE_RULE = """
COMMENTARY, NOT ANALYSIS: Write management commentary, not analyst
commentary. Every paragraph follows exactly this pattern and no more:
  Fact -> Business implication directly supported by the data -> Management
  observation (if warranted).
Never add a fourth step. Never explain why a number moved, what strategy it
reflects, or what it "allows" the institution to do, unless that causal
claim is explicitly printed in the source.

BANNED HEDGE/INFERENCE WORDS (do not use, in any section, under any
framing): "suggests", "indicates", "likely", "may reflect", "appears to",
"could indicate", "points toward", "probably", "implies", "allowing...
rather than", "rather than forced sales", "monitoring should focus on
whether""reflects a reliance on", "demonstrates", "shows that
management", "relied more heavily on", "limiting flexibility for".

BANNED CONSULTANT PHRASING: Do not describe a mix, structure, or
composition as something that "allows," "enables," or "supports" a
capability unless that exact capability is stated in the source. Prefer
short, flat, declarative sentences over compound sentences with embedded
reasoning. Example -- write "The investment portfolio remains
conservative, liquid, and well diversified." NOT "This diversified
composition and balanced maturity distribution allow the institution
to..."


NEVER invent a cause for a balance-sheet or funding movement (e.g. never
write "member deposits declined, allowing assets to expand through
investment purchases" -- that asserts a funding decision that a balance
sheet cannot prove). State the two facts separately if both are true;
never connect them with an invented mechanism.

NEVER invent an organizational, staffing, or historical event not present
in the source (e.g. "restructuring efforts completed several years ago").
If a trend has no stated cause, state the trend and stop.

SENTENCE LENGTH: Prefer one clear sentence per fact over a single sentence
carrying fact + explanation + implication + comparison. If a sentence has
more than one subordinate clause explaining "why," split it or cut the
explanatory clause.

SOURCE-SILENCE (applies to every section, extracted data or image-only):
Never write about where a number came from. Banned words/phrases in any
section: "JSON", "payload", "chart", "chart callout", "image", "page",
"table", "visually", "as shown". If something can't be confirmed, omit it
or use a DATA CHECK line -- never narrate that a figure is unlabeled,
approximate, or artifact-sourced inside a body paragraph.
"""
NUMERIC_INTEGRITY_RULE = """
NUMERIC INTEGRITY (strict): Every dollar figure in the extracted data or
source image is already in whole, correct units -- never re-scale, rebase,
or shift its decimal point for any reason, including during $K / $million
formatting. Converting to that display convention changes the LABEL, never
the digits: $1,123,123 becomes "$1.12 million," not "$11.2 million";
$123,123 becomes "$123K," not "$12.3 million." Before writing any dollar
figure, count its digits against the source number -- if your formatted
figure and the source figure don't represent the identical quantity, the
formatting is wrong, not the source. Never assume a table is "in
thousands" or "in millions" unless that exact denomination label is
printed in the source; if no denomination label is visible, the number is
already in whole dollars.
"""

EXTRACTED_DATA_RULE = """
DATA SOURCE HIERARCHY:
Below the images, you may also receive a block of pre-extracted, reconciled
JSON data for this section. That JSON is the AUTHORITATIVE source for every
number, percentage, and total -- it has already been validated against the
source table. Use the attached image(s) only to describe qualitative shape
where the JSON does not cover it. Do not extract or restate a dollar figure
or percentage from the image if the same field is present in the JSON.

If the JSON includes a "flags" list, check each flag's "resolved" field:
- resolved: true -- the pipeline has already corrected the figure you should
  use. Use the corrected value silently. Do NOT print a visible DATA CHECK
  line for this flag -- it is not a reader-facing issue, it is already fixed.
- resolved: false (or missing) -- this is a genuine, unresolved discrepancy.
  State exactly one DATA CHECK line above the title in your own words.

SOURCE-SILENCE RULE (strict): Never reference where any figure came from,
in any form. Banned words and phrases, in any section, regardless of
framing: "JSON", "payload", "data provided", "extracted data", "chart",
"chart callout", "chart legend", "image", "page", "table", "visually",
"as shown", "per the source", "not disclosed in the source materials"
(the one narrow exception: the specific missing-recoveries sentence a
module's own instructions explicitly authorize verbatim). A board report
states facts as facts. If a figure cannot be confirmed, either omit it
silently or raise it as a DATA CHECK line -- never explain in body text
that a figure is missing, unlabeled, or came from a chart/image/JSON
field. Writing about the artifact you read the number from is a failure
condition exactly like a wrong number would be.
"""

DECIMAL_SCALE_RULE = """
  DECIMAL/PERCENT SCALE CHECK: If any ratio or percentage in the extracted
  data appears as a raw decimal (e.g. 0.10 instead of 10%), convert it
  silently to percent form before writing it -- never show the conversion
  itself, never print the raw decimal. Confirm every percentage you write
  is in a plausible range for its metric type; a figure that is off by a
  factor of 10 (e.g. 1.3% written where the source shows 13.0%) is a
  serious error -- re-check the raw source value's decimal placement
  before finalizing any percentage figure.
  """

JSON_WRAP_RULE = """
OUTPUT FORMAT -- THIS SUPERSEDES ANY PLAIN-TEXT FORMAT DESCRIBED ABOVE:
Do not output plain markdown or raw text. Wrap your entire final output in
this exact JSON structure, with the section's own title and content:

{
  "title": "<the section's title line, following the title format given above, with the actual date filled in>",
  "content": "<the FULL narrative text, including any sub-headers like 'Portfolio Composition' as plain text inside this string, with paragraph breaks as \\n\\n>"
}

Rules:
- "content" must contain the ENTIRE narrative as ONE string, all paragraphs (and
  any sub-headers the module's structure requires) in order, separated by \\n\\n.
- Sub-headers belong INSIDE "content" as plain text -- do not omit them, and do
  not try to give each sub-header its own JSON key.
- If the module's rules call for a DATA CHECK line, place it as the first line
  inside "content", before the title text, separated by \\n\\n like any other line.
- Do not add any keys beyond "title" and "content".
- Return ONLY this JSON object. The first character of your response must be
  "{" and the last character must be "}". No text before or after it, no
  markdown code fences.
"""