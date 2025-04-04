import pdfplumber
import pandas as pd 
import re
from collections import defaultdict
from pathlib import Path
import re

def extract_table_from_page(page):
    lines = page.extract_text().split("\n")
    table_rows = []
    i = 0

    while i < len(lines) - 1:
        line1 = lines[i].strip()
        line2 = lines[i + 1].strip()

        # Check if line1 starts with a valid date
        if re.match(r"\d{2}-[A-Z][a-z]{2}-\d{4}", line1[:11]):
            # Merge both lines
            full_line = f"{line1} {line2}"

            # Extract Date and Type
            date_match = re.match(r"(\d{2}-[A-Z][a-z]{2}-\d{4})\s+([TC])", line1)
            if not date_match:
                i += 1
                continue

            date = date_match.group(1)
            txn_type = date_match.group(2)

            # Extract Balance (value before "Dr")
            balance_match = re.search(r'([\d,]+\.\d+)\s*Dr', full_line)
            balance = balance_match.group(1) if balance_match else ""

            # Extract Amount (just before balance)
            amount_match = re.findall(r'([\d,]+\.\d+)', full_line)
            amount = amount_match[-2] if len(amount_match) >= 2 else ""

            # Remove date, type, amount and balance to get description
            description_part = re.sub(rf"{date}\s+{txn_type}", '', full_line, 1)
            description_part = description_part.replace(amount, "").replace(balance, "").replace("Dr", "").strip()

            row = {
                "Date": date,
                "Type": txn_type,
                "Description": description_part,
                "Amount": amount,
                "Balance": balance
            }

            table_rows.append(row)
            i += 2  # Skip next line (since we consumed 2 lines)
        else:
            i += 1

    return table_rows

def group_words_by_line(words, y_tolerance=3):
    lines = defaultdict(list)
    for word in words:
        y = round(word['top'] / y_tolerance)
        lines[y].append(word)
    return [sorted(line, key=lambda w: w['x0']) for line in sorted(lines.values(), key=lambda l: l[0]['top'])]

def extract_pdf_tables(pdf_path, output_path):
    all_rows = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_rows = extract_table_from_page(page)
            all_rows.extend(page_rows)

    df = pd.DataFrame(all_rows)
    df.to_excel(output_path, index=False)
    print(f"Extracted to: {output_path}")

if __name__ == "__main__":
    input_pdf = "sample_input/test3.pdf"
    output_file = "output/extracted_tables.xlsx"
    Path("output").mkdir(exist_ok=True)
    extract_pdf_tables(input_pdf, output_file)
