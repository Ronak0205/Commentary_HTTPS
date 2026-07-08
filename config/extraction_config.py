EXTRACTION_CONFIG = {
    "balance_sheet": {"extractable": True, "parser": "parse_balance_sheet"},
    "loan": {"extractable": True, "parser": "parse_loan"},
    "loan_continue": {"extractable": True, "parser": "parse_loan_continue"},
    "share": {"extractable": True, "parser": "parse_share"},
    "investment": {"extractable": True, "parser": "parse_investment"},
    "policy": {"extractable": True, "parser": "parse_policy"},
    "key_financial": {"extractable": True, "parser": "parse_key_financial", "hybrid": True},
    "earning": {"extractable": False},
    "membership": {"extractable": False},
}