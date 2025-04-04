import re

def is_transaction_line(text):
    return bool(re.match(r"\d{2}-[A-Z][a-z]{2}-\d{4}", text.strip()[:11]))

def clean_amount(amount_str):
    return amount_str.replace(",", "").replace("Dr", "").strip()
