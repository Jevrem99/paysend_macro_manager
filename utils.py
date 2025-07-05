import re
import datetime

def is_phone_number(term):
    pattern = re.compile(r'[+\d()\-./\s]{7,}')
    return bool(pattern.match(term))

def is_transaction_number(term):
    pattern = re.compile(r'1[0-9]{8}00')
    return bool(pattern.match(term))

def format_phone_number(term):
    return ''.join(filter(str.isdigit, term))

def extract_number(value):
    match = re.search(r'[\d,]+(?:\.\d+)?', value)
    return float(match.group().replace(',', '')) if match else 0

def extract_currency(value):
    match = re.search(r'[^\d,]+$', value)
    return match.group().strip() if match else ''

def format_date(date_str):
    date = datetime.strptime(date_str, '%d/%m/%Y')
    day = date.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return f"{day}{suffix} of {date.strftime('%B %Y')}"