import csv
import re

from pypdf import PdfReader

# Path to the PDF
pdf_path = "/home/dislove/ACGS-2/main.pdf"

# Read the PDF
reader = PdfReader(pdf_path)
text = ""
for page in reader.pages:
    text += page.extract_text()

# Define patterns to match for claims
patterns = [
    r"we show",
    r"our system achieves",
]

# Find all claims
claims = []
for pattern in patterns:
    matches = re.finditer(pattern + r".*", text, re.IGNORECASE)
    for match in matches:
        claims.append(match.group().strip())

# Create CSV file
csv_path = "/home/dislove/ACGS-2/research/validation/claims.csv"
with open(csv_path, "w", newline="") as csvfile:
    fieldnames = ["claim_id", "section", "original_text"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for idx, claim in enumerate(claims, start=1):
        # Placeholder section, since parsing sections would be more complex
        writer.writerow({"claim_id": idx, "section": "N/A", "original_text": claim})
