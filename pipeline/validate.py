def _pct_diff(a, b):
    if a in (None, 0) or b is None:
        return None
    return abs(a - b) / abs(a)


def _drop_none(flag):
    return [flag] if flag else []


def _amt(field):
    return field.get("amount") if isinstance(field, dict) else field


def validate_segment_sum(segments, stated_total, tolerance=0.02, label="segments"):
    if stated_total is None:
        return None
    amounts = [s["amount"] for s in segments if s.get("amount") is not None]
    if not amounts:
        return None
    segment_sum = sum(amounts)
    diff = _pct_diff(stated_total, segment_sum)
    if diff is not None and diff > tolerance:
        return {
            "status": "DATA_CHECK",
            "resolved": False,
            "reason": (
                f"{label} sum to {segment_sum:,.1f}, stated total is "
                f"{stated_total:,.1f} ({diff * 100:.1f}% mismatch)"
            ),
        }
    return None


def validate_percent_composition(segments, tolerance=2.0):
    pcts = [s["pct"] for s in segments if s.get("pct") is not None]
    if not pcts:
        return None
    total_pct = sum(pcts)
    if abs(total_pct - 100) > tolerance:
        return {
            "status": "DATA_CHECK",
            "resolved": False,
            "reason": f"segment percentages sum to {total_pct:.1f}%, not ~100%",
        }
    return None


def validate_cross_source(control_value, other_value, control_label, other_label, tolerance=0.02):
    if control_value is None or other_value is None:
        return {"status": "OK", "value": control_value}
    diff = _pct_diff(control_value, other_value)
    if diff is not None and diff > tolerance:
        return {
            "status": "DATA_CHECK",
            "resolved": True,
            "reason": (
                f"{other_label} total ({other_value:,.1f}) does not reconcile "
                f"with {control_label} figure ({control_value:,.1f}) --"
                f"resolved using {control_label} as the control value"
            ),
            "value": control_value,
        }
    return {"status": "OK", "value": control_value}


def validate_delinquency_segments(delinquency_segments, total_delinquent, tolerance=0.02):
    flags = []
    if total_delinquent is not None:
        for seg in delinquency_segments:
            amt = seg.get("amount")
            if amt is not None and amt > total_delinquent:
                flags.append({
                    "status": "DATA_CHECK",
                    "resolved": False,
                    "reason": (
                        f"segment '{seg['label']}' ({amt:,.1f}) exceeds total "
                        f"delinquent loans ({total_delinquent:,.1f}) -- likely unit mismatch"
                    ),
                })
        sum_flag = validate_segment_sum(delinquency_segments, total_delinquent, tolerance,
                                         label="delinquency segments")
        if sum_flag:
            flags.append(sum_flag)
            total_delinquent = None  # don't pass through an irreconcilable total
    return flags, total_delinquent


def validate_recoveries_vs_chargeoffs(recoveries_total, gross_chargeoffs_total):
    if recoveries_total is None or gross_chargeoffs_total in (None, 0):
        return None
    if recoveries_total >= gross_chargeoffs_total * 0.9:
        return {
            "status": "DATA_CHECK",
            "resolved": False,
            "reason": (
                f"recoveries ({recoveries_total:,.1f}) are atypically close to or "
                f"exceed gross charge-offs ({gross_chargeoffs_total:,.1f}) -- verify"
            ),
        }
    return None


def validate_equity_components(undivided_earnings, reserves, total_equity, tolerance=0.05):
    if total_equity is None:
        return None
    if undivided_earnings is not None and undivided_earnings > total_equity:
        return {
            "status": "DATA_CHECK",
            "resolved": False,
            "reason": (
                f"undivided earnings ({undivided_earnings:,.1f}) exceeds total "
                f"equity ({total_equity:,.1f}) -- likely misread unit"
            ),
        }
    if undivided_earnings is not None and reserves is not None:
        combined = undivided_earnings + reserves
        diff = _pct_diff(total_equity, combined)
        if diff is not None and diff > tolerance and combined > total_equity:
            return {
                "status": "DATA_CHECK",
                "resolved": False,
                "reason": (
                    f"undivided earnings + reserves ({combined:,.1f}) exceeds total "
                    f"equity ({total_equity:,.1f}) beyond normal rounding"
                ),
            }
    return None


def validate_scale_plausibility(value, reference, max_ratio=3, label="figure"):
    if value is None or reference in (None, 0):
        return None
    if abs(value) > abs(reference) * max_ratio:
        return {
            "status": "DATA_CHECK",
            "resolved": False,
            "reason": (
                f"{label} ({value:,.1f}) is implausibly large relative to reference "
                f"({reference:,.1f}) -- likely unit/decimal error"
            ),
        }
    return None

def validate_earning_segments(income_segments, income_total, expense_segments, expense_total, tolerance=0.02):
    """
    Reconciles the earning_extract sub-component segments against
    parse_earning()'s own headline_totals (table-sourced, authoritative).
    Mirrors validate_segment_sum()'s existing pattern used for loan/share/
    investment segments.

    On mismatch, the offending segment list is dropped (mirrors
    validate_delinquency_segments()'s handling of an irreconcilable total)
    so the commentary writer is never handed a breakdown it cannot trust --
    it falls back to the headline total alone, per earning.py's
    reconciliation-gate instruction.
    """
    flags = []

    income_flag = validate_segment_sum(
        income_segments or [], income_total, tolerance, label="non-interest income segments"
    )
    if income_flag:
        flags.append(income_flag)
        income_segments = []

    expense_flag = validate_segment_sum(
        expense_segments or [], expense_total, tolerance, label="non-interest expense segments"
    )
    if expense_flag:
        flags.append(expense_flag)
        expense_segments = []

    return flags, income_segments, expense_segments

def validate_section(section_name, extracted):
    if not extracted:
        return None

    flags = []
    try:
        if section_name == "loan":
            flags += _drop_none(validate_segment_sum(
                extracted.get("portfolio_segments", []), extracted.get("total_loans"),
                label="portfolio segments"))
            flags += _drop_none(validate_percent_composition(extracted.get("portfolio_segments", [])))
            d_flags, total_delinquent = validate_delinquency_segments(
                extracted.get("delinquency_segments", []), extracted.get("total_delinquent_loans"))
            flags += d_flags
            extracted["total_delinquent_loans"] = total_delinquent 
            
        elif section_name == "earning":
          totals = extracted.get("headline_totals", {})
          ni = totals.get("net_income")
          ii = totals.get("interest_income")
          ie = totals.get("interest_expense")
          if ni is not None and ii is not None and ie is not None:
              implied_spread = ii - ie
 
              flags += _drop_none(validate_scale_plausibility(
                 ni, implied_spread, max_ratio=5, label="net income vs. interest spread"))  

          income_segments = extracted.get("non_interest_income_segments")
          expense_segments = extracted.get("non_interest_expense_segments")
          if income_segments is not None or expense_segments is not None:
              seg_flags, resolved_income, resolved_expense = validate_earning_segments(
                  income_segments,
                  totals.get("non_interest_income_total"),
                  expense_segments,
                  totals.get("non_interest_expense_total"),
              )
              flags += seg_flags
              extracted["non_interest_income_segments"] = resolved_income
              extracted["non_interest_expense_segments"] = resolved_expense
           
        elif section_name == "loan_continue":
            gross = sum(s["amount"] or 0 for s in extracted.get("charge_off_segments", [])) or None
            recov = sum(s["amount"] or 0 for s in extracted.get("recovery_segments", [])) or None
            flags += _drop_none(validate_recoveries_vs_chargeoffs(recov, gross))

        elif section_name == "share":
            flags += _drop_none(validate_segment_sum(
                extracted.get("share_segments", []), extracted.get("total_shares"),
                label="share segments"))
            flags += _drop_none(validate_percent_composition(extracted.get("share_segments", [])))

        elif section_name == "balance_sheet":
            total_assets = _amt(extracted.get("total_assets"))
            total_liab = _amt(extracted.get("total_liabilities"))
            total_equity = _amt(extracted.get("total_equity"))
            if total_assets and total_liab and total_equity:
                flags += _drop_none(validate_scale_plausibility(
                    total_liab + total_equity, total_assets, max_ratio=1.2,
                    label="liabilities + equity"))
            flags += _drop_none(validate_equity_components(
                _amt(extracted.get("undivided_earnings")),
                _amt(extracted.get("reserves")), total_equity))

        elif section_name == "investment":
            flags += _drop_none(validate_segment_sum(
                extracted.get("investment_segments", []), extracted.get("total_investments"),
                label="investment segments"))

    except Exception:
        pass

    return {"status": "DATA_CHECK" if flags else "OK", "data": extracted, "flags": flags}