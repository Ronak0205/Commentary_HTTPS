PDF_NAMES = [
    "01_Board_Report_Quaterly_WithoutCommentary",
]

EXTRACTED_IMG_DIR = "extracted_img"
DATA_DIR = "data"

SECTIONS = [
    {
        "name": "balance_sheet",
        "pages": [7],
        "module": "balance",
        "system_prompt_var": "SYSTEM_PROMPT",
        "user_prompt_var": "USER_PROMPT",
    },
    {
        "name": "earning",
        "pages": [9, 10],
        "module": "earning",
        "system_prompt_var": "SYSTEM_PROMPT",
        "user_prompt_var": "USER_PROMPT",
    },
    {
        "name": "key_financial",
        "pages": [12, 13, 14],
        "module": "key_financial",
        "system_prompt_var": "SYSTEM_PROMPT",
        "user_prompt_var": "USER_PROMPT",
    },
    {
        "name": "loan",
        "pages": [16, 17],
        "module": "loan",
        "system_prompt_var": "SYSTEM_PROMPT",
        "user_prompt_var": "USER_PROMPT",
    },
    {
        "name": "loan_continue",
        "pages": [18, 19, 20],
        "module": "loan_continue",
        "system_prompt_var": "SYSTEM_PROMPT",
        "user_prompt_var": "USER_PROMPT",
    },
    {
        "name": "share",
        "pages": [23],
        "module": "share",
        "system_prompt_var": "SYSTEM_PROMPT",
        "user_prompt_var": "USER_PROMPT",
    },
    {
        "name": "investment",
        "pages": [25],
        "module": "investment",
        "system_prompt_var": "SYSTEM_PROMPT",
        "user_prompt_var": "USER_PROMPT",
    },
    {
        "name": "membership",
        "pages": [27],
        "module": "membership",
        "system_prompt_var": "SYSTEM_PROMPT",
        "user_prompt_var": "USER_PROMPT",
    },
    {
        "name": "policy",
        "pages": [29],
        "module": "policy",
        "system_prompt_var": "SYSTEM_PROMPT",
        "user_prompt_var": "USER_PROMPT",
    },
]