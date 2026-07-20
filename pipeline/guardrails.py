"""
guardrails.py

Cross-source conflict detection that must run BEFORE commentary generation.
Known conflicts between two independently-sourced figures -- e.g. the
Shares table vs. the Balance Sheet's shares/deposits control total, or the
board report's non-interest-expense component table vs. an independently
-sourced total -- must be caught and resolved, or explicitly held for
manual review, before the writer model ever sees the data. Letting the
model silently pick one of two disagreeing numbers is the failure mode
this file exists to remove.

Two conflict types, two different resolutions -- deliberately not unified
into one generic "reconcile" function, because they don't have the same
answer available:

  - SHARES vs BALANCE SHEET: this project has a documented source
    priority (the Balance Sheet is the control total for cross-source
    reconciliation). A mismatch is auto-resolved using that priority and
    recorded as a "resolved: true" flag -- generation proceeds using the
    corrected value.

  - EARNINGS non-interest expense vs an EXTERNAL source: no priority is
    defined between two independently-sourced totals (this pipeline
    currently extracts from one PDF; if a second document's figure is
    ever supplied, there's no existing rule for which one wins). A
    genuine mismatch here BLOCKS generation for that section until a
    human confirms which figure is correct. If no external figure is
    supplied at all, this check is a no-op -- it never blocks on data
    you don't have.
"""

from pipeline.validate import _pct_diff


def check_shares_vs_balance_sheet(share_data, balance_sheet_data,
                                   amount_tolerance=0.02, pct_point_tolerance=1.0):
    """
    Compares share_data's total_shares / total_shares_pct_change against
    balance_sheet_data's shares_deposits.amount / .pct_change (the
    documented control source). Auto-resolves using the Balance Sheet
    value on any mismatch in either field independently -- the dollar
    total and the % change are reconciled separately, since a fix to one
    does not imply the other was ever wrong.

    Returns:
        {
            "status": "OK" | "DATA_CHECK",
            "flags": [...],
            "resolved": {"total_shares": ..., "total_shares_pct_change": ...},
            "blocked": False,   # this conflict type always has a defined priority
        }
    """
    if not share_data or not balance_sheet_data:
        return {"status": "OK", "flags": [], "resolved": {}, "blocked": False}

    control = balance_sheet_data.get("shares_deposits") or {}
    control_amount = control.get("amount")
    control_pct_change = control.get("pct_change")

    share_amount = share_data.get("total_shares")
    share_pct_change = share_data.get("total_shares_pct_change")

    resolved_amount = share_amount
    resolved_pct_change = share_pct_change
    flags = []

    amount_diff = _pct_diff(control_amount, share_amount)
    if amount_diff is not None and amount_diff > amount_tolerance:
        flags.append({
            "status": "DATA_CHECK",
            "resolved": True,
            "reason": (
                f"Shares table total ({share_amount:,.0f}) does not reconcile "
                f"with Balance Sheet shares/deposits ({control_amount:,.0f}) -- "
                f"resolved using the Balance Sheet as the control source"
            ),
        })
        resolved_amount = control_amount

    if control_pct_change is not None and share_pct_change is not None:
        if abs(control_pct_change - share_pct_change) > pct_point_tolerance:
            flags.append({
                "status": "DATA_CHECK",
                "resolved": True,
                "reason": (
                    f"Shares table % change ({share_pct_change:.1f}%) does not "
                    f"reconcile with Balance Sheet shares/deposits % change "
                    f"({control_pct_change:.1f}%) -- resolved using the Balance "
                    f"Sheet as the control source"
                ),
            })
            resolved_pct_change = control_pct_change

    return {
        "status": "DATA_CHECK" if flags else "OK",
        "flags": flags,
        "resolved": {
            "total_shares": resolved_amount,
            "total_shares_pct_change": resolved_pct_change,
        },
        "blocked": False,
    }


def check_earning_expense_conflict(headline_totals, external_non_interest_expense=None,
                                    tolerance=0.02):
    """
    Compares the board report's own non_interest_expense_total against an
    independently-sourced figure (e.g. an audited income statement total),
    if one is supplied. Unlike the shares/balance-sheet case, there is no
    default priority between two independently-sourced totals -- a genuine
    mismatch here BLOCKS generation for this section until a human
    confirms which figure is correct.

    Returns:
        {
            "status": "OK" | "DATA_CHECK",
            "flags": [...],
            "resolved": {"non_interest_expense_total": ... or None if blocked},
            "blocked": bool,
        }
    """
    board_total = (headline_totals or {}).get("non_interest_expense_total")

    if external_non_interest_expense is None or board_total is None:
        return {
            "status": "OK", "flags": [],
            "resolved": {"non_interest_expense_total": board_total},
            "blocked": False,
        }

    diff = _pct_diff(board_total, external_non_interest_expense)
    if diff is not None and diff > tolerance:
        return {
            "status": "DATA_CHECK",
            "flags": [{
                "status": "DATA_CHECK",
                "resolved": False,
                "reason": (
                    f"non-interest expense disagrees across sources: board "
                    f"report component table shows {board_total:,.0f}, "
                    f"independent source shows {external_non_interest_expense:,.0f} "
                    f"-- no source priority defined for this conflict, requires "
                    f"manual confirmation before this section can be written"
                ),
            }],
            "resolved": {"non_interest_expense_total": None},
            "blocked": True,
        }

    return {
        "status": "OK", "flags": [],
        "resolved": {"non_interest_expense_total": board_total},
        "blocked": False,
    }


def apply_guardrails(section_name, section_data, context=None):
    """
    Single entry point for pipeline.py / section_run.py to call BEFORE
    handing section_data to generate_commentary(). `context` holds any
    other sections' cleaned data this section's guardrail needs (e.g.
    context["balance_sheet"] for the share guardrail, or
    context["external_non_interest_expense"] for the earning guardrail).

    Returns (section_data, flags, blocked):
      - section_data: the same dict, with any auto-resolved values applied
        in place
      - flags: list of flag dicts to attach to this section's payload
      - blocked: True if generation must NOT proceed for this section
        until a human resolves the conflict
    """
    context = context or {}
    flags = []
    blocked = False

    if section_name == "share":
        result = check_shares_vs_balance_sheet(
            section_data, context.get("balance_sheet")
        )
        flags += result["flags"]
        resolved = result["resolved"]
        if resolved.get("total_shares") is not None:
            section_data["total_shares"] = resolved["total_shares"]
        if resolved.get("total_shares_pct_change") is not None:
            section_data["total_shares_pct_change"] = resolved["total_shares_pct_change"]
        blocked = result["blocked"]

    elif section_name == "earning":
        result = check_earning_expense_conflict(
            section_data.get("headline_totals"),
            external_non_interest_expense=context.get("external_non_interest_expense"),
        )
        flags += result["flags"]
        blocked = result["blocked"]

    return section_data, flags, blocked