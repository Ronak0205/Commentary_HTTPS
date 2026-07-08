
import pdfplumber
import re

_TOTAL_RE = re.compile(r"^\s*total\b", re.IGNORECASE)
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

        if _TOTAL_RE.match(row["label"]):
            total = {
                "amount": values[0] if len(values) > 0 else None,
                "pct_change": values[-1] if len(values) > 1 else None,
            }
            continue

        matched = next((name for name, alias in aliases.items() if alias in label_upper), None)
        if matched is None:
            if segments or total is not None:
                break  # we've moved past the real table into chart noise
            continue  # header/title rows before the table starts

        segments.append({
            "label": matched,
            "amount": values[0] if len(values) > 0 else None,
            "pct": values[1] if len(values) > 1 else None,
            "pct_change": values[-1] if len(values) > 2 else (values[1] if len(values) == 2 else None),
        })

    return segments, total


LOAN_ALIASES = {
    "used_vehicle": "USED VEHICLE LOANS",
    "new_vehicle": "NEW VEHICLE LOANS",
    "unsecured": "ALL OTHER UNSECURED LOANS",
    "other_secured_non_re": "ALL OTHER SECURED NON-REAL",
    "secured_first_lien": "SECURED BY A FIRST LIEN",
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
    started = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        low = line.lower()
        if started and any(marker in low for marker in STOP_MARKERS):
            break

        label, value_tokens = _split_label_and_values(line)

        if value_tokens:
            # finalize whatever was pending, start a new row
            if pending and pending["label"]:
                rows.append(pending)
            pending = {
                "label": label,
                "values": [_clean_number(v) for v in value_tokens],
            }
            started = True
        else:
            if pending is not None:
                pending["label"] = f"{pending['label']} {line}".strip()

    if pending and pending["label"]:
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
        if exact_label and norm == exact_label.upper():
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

    return {
        "charge_off_segments": co_segments,
        "total_charge_offs": co_total["amount"] if co_total else None,
        "total_charge_offs_pct_change": co_total["pct_change"] if co_total else None,
        "recovery_segments": rec_segments,
        "total_recoveries": rec_total["amount"] if rec_total else None,
        "total_recoveries_pct_change": rec_total["pct_change"] if rec_total else None,
        "cecl_allowance": abs(cecl_row["values"][0]) if cecl_row and cecl_row["values"] else None,
        "cecl_allowance_pct_change": cecl_row["values"][-1] if cecl_row and len(cecl_row["values"]) > 1 else None,
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
        "note": "solvency_ratio, classified_assets_to_net_worth, core_funding_ratio, "
                "loan_to_share_ratio, loan/share/membership growth are NOT in this "
                "payload -- they only appear as chart callouts on pages 13-14 and "
                "must still be read from the attached images.",
    }


def parse_policy(pdf_path, page_numbers):
    rows = _extract_rows(pdf_path, page_numbers)
    return {"raw_rows": rows} if rows else None


def parse_investment(pdf_path, page_numbers):
    rows = _extract_rows(pdf_path, page_numbers)
    return {"raw_rows": rows} if rows else None

def parse_investment(pdf_path, page_numbers):
    rows = _extract_rows(pdf_path, [page_numbers[0]])
    segments, total = _segments_from_rows(rows, INVESTMENT_ALIASES)
    return {
        "investment_segments": segments,
        "total_investments": total["amount"] if total else None,
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