import pdfplumber
import re

_DATE_RE = re.compile(r"\b(\d{2}-\d{2}-\d{4})\b")
_TOTAL_RE = re.compile(r"^\s*total\b|\btotal\s*$", re.IGNORECASE)
_PCT_CELL_RE = re.compile(r"^-?\d+\.?\d*%$")
_INSTITUTION_RE = re.compile(r"([A-Z][A-Z .&]+(?:CREDIT UNION|FEDERAL CREDIT UNION))")

AMOUNT_RE = re.compile(r'^-?\(?\$?\d{1,3}(?:,\d{3})*(?:\.\d+)?\)?$')
PERCENT_RE = re.compile(r'^-?\(?\d{1,3}(?:\.\d+)?%\)?$')

STOP_MARKERS = ["trend", "power bi desktop", "board report as of"]

def _segments_from_rows(rows, aliases):
    segments = []
    total = None

    for row in rows:
        label_upper = row["label"].upper()
        values = row["values"]

        if _TOTAL_RE.search(row["label"]):
            total = {
                "amount": values[0] if len(values) > 0 else None,
                "pct_change": values[-1] if len(values) > 1 else None,
            }
            # The Total row marks the end of this table -- stop here, before
            # the chart/legend section below it. Scanning past Total is what
            # previously let chart-legend text get re-matched as duplicate
            # segments once the "break on any unmatched row" guard below was
            # relaxed.
            break

        matched = next((name for name, alias in aliases.items() if alias in label_upper), None)
        if matched is None:
            # Skip a corrupted/unmatched row (e.g. page-furniture text like a
            # floating "Report Filter" widget bleeding into a wrapped label)
            # instead of abandoning the rest of the table. Real tables in this
            # report always terminate at a "Total" row (handled above), so it
            # is safe to keep scanning past a single bad label rather than
            # discarding every segment that comes after it.
            continue

        segments.append({
            "label": matched,
            "amount": values[0] if len(values) > 0 else None,
            # Only treat the middle value as a genuine "% of total" figure
            # when the row actually has three columns (amount, % of total,
            # % change). Tables with only two columns (amount, % change --
            # e.g. Delinquency, Charge-Offs, Recoveries) have no printed
            # %-of-total column at all; treating values[1] as one there
            # silently duplicates the % change into "pct" and mislabels it.
            "pct": values[1] if len(values) > 2 else None,
            "pct_change": values[-1] if len(values) > 1 else None,
        })

    return segments, total

EARNING_TOTAL_ALIASES = {
    "net_income": "NET INCOME",
    "interest_income": "INTEREST INCOME",
    "interest_expense": "INTEREST EXPENSE",
    "non_interest_income_total": "NON-INTEREST INCOME",
    "non_interest_expense_total": "NON-INTEREST EXPENSE",
}

LOAN_ALIASES = {
    "used_vehicle": "USED VEHICLE LOANS",
    "new_vehicle": "NEW VEHICLE LOANS",
    "unsecured": "ALL OTHER UNSECURED LOANS",
    "other_secured_non_re": "ALL OTHER SECURED NON-REAL",
    "secured_first_lien": "SECURED BY",  # shortened: trailing-wrap corruption
    # sometimes strips "A FIRST LIEN" off this row's label onto the next row;
    # "SECURED BY" alone is unambiguous against the other loan aliases.
}

SHARE_ALIASES = {
    "regular_shares": "REGULAR SHARES",
    "share_certificates": "SHARE CERTIFICATES",
    "ira_keogh": "IRA/KEOGH",
    "share_drafts": "SHARE DRAFTS",
    "all_other_shares": "ALL OTHER SHARES",
}

CHARGE_OFF_ALIASES = {
    "unsecured": "ALL OTHER UNSECURED LOANS",
    "used_vehicle": "USED VEHICLE LOANS",
    "new_vehicle": "NEW VEHICLE LOANS",
    "other_secured_non_re": "ALL OTHER SECURED NON-REAL",
}

KEY_FIN_ALIASES = {
    "cost_of_funds": "COST OF FUNDS",
    "delinquency_ratio": "DELINQUENT LOANS/TOTAL LOANS",
    "net_charge_off_ratio": "NET CHARGE-OFFS",
    "nim": "NET INTEREST MARGIN",
    "net_margin": "NET MARGIN",
    "net_operating_expense_ratio": "NET OPERATING EXPENSES",
    "net_worth_ratio": "NET WORTH / TOTAL ASSETS",
    "operating_expense_ratio": "OPERATING EXPENSES / AVERAGE",
    "roaa": "RETURN ON AVERAGE ASSETS",
}

INVESTMENT_ALIASES = {
    "htm_debt_securities": "HELD-TO-MATURITY DEBT SECURITIES",
    "other_investments": "OTHER INVESTMENTS",
}

def extract_report_date(pdf_path, page_number=0):
    with pdfplumber.open(pdf_path) as pdf:
        if page_number >= len(pdf.pages):
            return None
        text = pdf.pages[page_number].extract_text() or ""
    match = _DATE_RE.search(text)
    return match.group(1) if match else None

def extract_institution_name(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text() or ""
    match = _INSTITUTION_RE.search(text.upper())
    return match.group(1).title() if match else None

def _clean_number(raw):
    if raw is None:
        return None
    s = str(raw).strip()
    if s in ("", "-", "—", "N/A", "n/a"):
        return None
    negative = s.startswith("(") and s.endswith(")")
    s = s.strip("()").replace("$", "").replace(",", "").replace("%", "").strip()
    if s in ("", "-"):
        return None
    try:
        value = float(s)
    except ValueError:
        return None
    return -value if negative else value


def _is_value_token(token):
    return bool(AMOUNT_RE.match(token) or PERCENT_RE.match(token))


def _split_label_and_values(line):
    tokens = line.split()
    values = []
    i = len(tokens)
    while i > 0 and _is_value_token(tokens[i - 1]):
        values.insert(0, tokens[i - 1])
        i -= 1
    label = " ".join(tokens[:i]).strip()
    return label, values


def _extract_rows_from_page_text(text):
    if not text:
        return []

    rows = []
    pending = None
    label_buffer = []
    started = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        low = line.lower()
        if started and any(marker in low for marker in STOP_MARKERS):
            break

        label_part, value_tokens = _split_label_and_values(line)

        if value_tokens:
            full_label = " ".join(label_buffer + ([label_part] if label_part else [])).strip()
            if pending is not None:
                rows.append(pending)
            pending = {"label": full_label, "values": [_clean_number(v) for v in value_tokens]}
            label_buffer = []
            started = True
        else:
             label_buffer.append(line)

    if pending is not None:
        rows.append(pending)
    return rows


def _extract_rows(pdf_path, page_numbers):
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number in page_numbers:
            if 0 <= page_number < len(pdf.pages):
                text = pdf.pages[page_number].extract_text()
                rows.extend(_extract_rows_from_page_text(text))
    return rows


def _find_row(rows, exact_label=None, contains=None):
    for row in rows:
        norm = row["label"].strip().upper()
        if exact_label:
            el = exact_label.upper()
            # Exact match first (unchanged, fastest path for clean labels).
            # Fall back to a suffix match for labels corrupted by merged
            # page-header text or a preceding row's wrapped continuation
            # text landing in front of this row's real label -- the true
            # field name is still the last token group before the row's
            # numbers, so a " " + label suffix match recovers it safely
            # without opening up false positives on unrelated rows.
            if norm == el or norm.endswith(" " + el):
                return row
        if contains and contains.upper() in norm:
            return row
    return None

def parse_policy(pdf_path, page_numbers):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_numbers[0]]
        raw_tables = page.extract_tables()

    rows = []
    for t in raw_tables:
        for row in t:
            cells = [c.strip() for c in row if c and str(c).strip()]
            if cells:
                rows.append(cells)

    metrics = []
    pending_metric_parts = []
    started = False

    for cells in rows:
        pct_idx = next((i for i, c in enumerate(cells) if _PCT_CELL_RE.match(c)), None)

        if pct_idx is None:
            if started:
                pending_metric_parts.extend(cells)  # wrapped label fragment
            continue

        started = True
        category = cells[0] if pct_idx > 0 else None
        metric_name = " ".join(pending_metric_parts + cells[1:pct_idx]).strip()
        pending_metric_parts = []

        remainder = cells[pct_idx + 1:]
        metrics.append({
            "category": category,
            "metric": metric_name,
            "value": float(cells[pct_idx].replace("%", "")),
            "benchmark": remainder[0] if remainder else None,
            "compliance": remainder[1] if len(remainder) > 1 else None,
        })

    return {"metrics": metrics}

def parse_balance_sheet(pdf_path, page_numbers):
    rows = _extract_rows(pdf_path, page_numbers)
    if not rows:
        return None

    def field(row):
        if not row or not row["values"]:
            return None
        return {
            "amount": row["values"][0] if len(row["values"]) > 0 else None,
            "pct_of_total": row["values"][1] if len(row["values"]) > 1 else None,
            "pct_change": row["values"][2] if len(row["values"]) > 2 else None,
        }

    return {
        "total_assets": field(_find_row(rows, exact_label="ASSETS")),
        "cash_deposits": field(_find_row(rows, exact_label="CASH AND DEPOSITS")),
        "investment_securities": field(_find_row(rows, exact_label="INVESTMENT SECURITIES")),
        "other_investments": field(_find_row(rows, exact_label="OTHER INVESTMENTS")),
        "loans_leases": field(_find_row(rows, exact_label="LOANS AND LEASES")),
        "other_assets": field(_find_row(rows, exact_label="OTHER ASSETS")),
        "total_liabilities": field(_find_row(rows, exact_label="LIABILITIES")),
        "accrued_liabilities": field(_find_row(rows, contains="ACCOUNTS PAYABLE")),
        "shares_deposits": field(_find_row(rows, exact_label="SHARES/DEPOSITS")),
        "total_equity": field(_find_row(rows, exact_label="EQUITY")),
        "undivided_earnings": field(_find_row(rows, exact_label="UNDIVIDED EARNINGS")),
        "reserves": field(_find_row(rows, exact_label="RESERVES")),
        "raw_rows": rows,  # keep for debugging / inspection
    }

def parse_earning(pdf_path, page_numbers):
    rows = _extract_rows(pdf_path, page_numbers)
    totals = {}
    for row in rows:
        label_upper = row["label"].upper()
        for name, alias in EARNING_TOTAL_ALIASES.items():
            if alias in label_upper and name not in totals and row["values"]:
                totals[name] = row["values"][-1]
    return {
        "headline_totals": totals,
        # NOTE: this used to carry a free-text "note" field with pipeline
        # instructions for the model (e.g. "must still be read from the
        # attached image"). That field was reaching the LLM verbatim via
        # commentary.py's json.dumps of extracted_data, and the model
        # echoed its exact phrasing ("chart-legend based", "the attached
        # image") into board-facing commentary. That instruction now lives
        # in earning.py's own SYSTEM_PROMPT (reconciliation checks 3-9)
        # instead of riding along inside the data payload. Do not
        # reintroduce a free-text instructional field here -- if the model
        # needs new guidance, add it to the relevant prompts/*.py file.
    }

def parse_loan(pdf_path, page_numbers):
    """page_numbers[0] = portfolio page, page_numbers[1] = delinquency page."""
    rows_portfolio = _extract_rows(pdf_path, [page_numbers[0]])
    rows_delinq = _extract_rows(pdf_path, [page_numbers[1]]) if len(page_numbers) > 1 else []

    portfolio_segments, total_loans_row = _segments_from_rows(rows_portfolio, LOAN_ALIASES)
    delinquency_segments, total_delinq_row = _segments_from_rows(rows_delinq, LOAN_ALIASES)
    
    portfolio_segments.sort(key=lambda s: s["amount"] or 0, reverse=True)
    top_two = portfolio_segments[:2]
    top_two_combined_pct = sum((s["pct"] or 0) for s in top_two)

    return {
        "portfolio_segments": portfolio_segments,  # now sorted descending
        "top_two_segments": [s["label"] for s in top_two],
        "top_two_combined_pct": round(top_two_combined_pct, 1),
        "total_loans": total_loans_row["amount"] if total_loans_row else None,
        "total_loans_pct_change": total_loans_row["pct_change"] if total_loans_row else None,
        "delinquency_segments": delinquency_segments,
        "total_delinquent_loans": total_delinq_row["amount"] if total_delinq_row else None,
        "total_delinquent_loans_pct_change": total_delinq_row["pct_change"] if total_delinq_row else None,
    }


def parse_loan_continue(pdf_path, page_numbers):
    """page_numbers[0]=charge-offs, [1]=recoveries, [2]=CECL (single figure, not segments)."""
    rows_co = _extract_rows(pdf_path, [page_numbers[0]]) if len(page_numbers) > 0 else []
    rows_rec = _extract_rows(pdf_path, [page_numbers[1]]) if len(page_numbers) > 1 else []
    rows_cecl = _extract_rows(pdf_path, [page_numbers[2]]) if len(page_numbers) > 2 else []

    co_segments, co_total = _segments_from_rows(rows_co, CHARGE_OFF_ALIASES)
    rec_segments, rec_total = _segments_from_rows(rows_rec, CHARGE_OFF_ALIASES)

    cecl_row = next((r for r in rows_cecl if "ALLOWANCE FOR CREDIT LOSSES" in r["label"].upper()), None)

    schedule_date = None
    if len(page_numbers) > 0:
        schedule_date = extract_report_date(pdf_path, page_number=page_numbers[0])
    return {
        "charge_off_segments": co_segments,
        "total_charge_offs": co_total["amount"] if co_total else None,
        "total_charge_offs_pct_change": co_total["pct_change"] if co_total else None,
        "recovery_segments": rec_segments,
        "total_recoveries": rec_total["amount"] if rec_total else None,
        "total_recoveries_pct_change": rec_total["pct_change"] if rec_total else None,
        "cecl_allowance": abs(cecl_row["values"][0]) if cecl_row and cecl_row["values"] else None,
        "cecl_allowance_pct_change": cecl_row["values"][-1] if cecl_row and len(cecl_row["values"]) > 1 else None,
        "schedule_as_of_date": schedule_date,
    }


def parse_share(pdf_path, page_numbers):
    rows = _extract_rows(pdf_path, [page_numbers[0]])
    segments, total = _segments_from_rows(rows, SHARE_ALIASES)
    return {
        "share_segments": segments,
        "total_shares": total["amount"] if total else None,
        "total_shares_pct_change": total["pct_change"] if total else None,
    }


def parse_key_financial(pdf_path, page_numbers):
    # Deliberately only page_numbers[0] (the real table). Pages 13-14 are
    # chart-embedded stat callouts, not gridded rows -- stay on the image
    # flow for those until a dedicated callout parser exists.
    rows = _extract_rows(pdf_path, [page_numbers[0]])
    metrics = {}
    for row in rows:
        label_upper = row["label"].upper()
        for name, alias in KEY_FIN_ALIASES.items():
            if alias in label_upper and name not in metrics:
                metrics[name] = {
                    "value": row["values"][0] if row["values"] else None,
                    "bps_change": row["values"][-1] if len(row["values"]) > 1 else None,
                }
    return {
        "metrics_from_table": metrics,
        # NOTE: see comment in parse_earning above -- a free-text "note"
        # field here previously leaked into commentary output verbatim
        # ("...per chart callout on page 14"). The guidance that
        # solvency_ratio / core_funding_ratio / loans-to-shares / growth
        # metrics are image-only now lives in key_financial.py's own
        # SYSTEM_PROMPT and USER_PROMPT, not in this data payload.
    }


def parse_investment(pdf_path, page_numbers):
    rows = _extract_rows(pdf_path, [page_numbers[0]])
    segments, total = _segments_from_rows(rows, INVESTMENT_ALIASES)
    total_amt = total["amount"] if total else None
    for s in segments:
        s["pct_of_total"] = round(100 * s["amount"] / total_amt, 1) if (s["amount"] and total_amt) else None
        s.pop("pct", None)  # this table has no printed %-of-total column; never fabricate one
    return {
        "investment_segments": segments,
        "total_investments": total_amt,
        "total_investments_pct_change": total["pct_change"] if total else None,
    }

PARSERS = {
    "parse_loan": parse_loan,
    "parse_loan_continue": parse_loan_continue,
    "parse_share": parse_share,
    "parse_balance_sheet": parse_balance_sheet,
    "parse_key_financial": parse_key_financial,
    "parse_policy": parse_policy,
    "parse_investment": parse_investment,
    "parse_earning": parse_earning,
}


def extract_section_data(pdf_path, section_name, page_numbers):
    from config.extraction_config import EXTRACTION_CONFIG

    cfg = EXTRACTION_CONFIG.get(section_name)
    if not cfg or not cfg.get("extractable"):
        return None

    parser = PARSERS.get(cfg.get("parser"))
    if not parser:
        return None

    try:
        return parser(pdf_path, page_numbers)
    except Exception:
        return None