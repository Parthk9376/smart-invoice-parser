from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI(title="Invoice Extractor")


class InvoiceRequest(BaseModel):
    text: str


class InvoiceResponse(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


@app.get("/")
def home():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract", response_model=InvoiceResponse)
def extract(req: InvoiceRequest):

    text = req.text or ""

    vendor = ""
    amount = 0.0
    currency = ""
    date = ""

    # ---------------- Vendor ----------------

    vendor_patterns = [
        r'([A-Za-z0-9&.,()\- ]+Industries Ltd\.)',
        r'([A-Za-z0-9&.,()\- ]+Limited)',
        r'([A-Za-z0-9&.,()\- ]+Ltd\.)',
        r'Vendor\s*[:\-]\s*(.+)',
        r'Supplier\s*[:\-]\s*(.+)',
    ]

    for p in vendor_patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            vendor = m.group(1).strip()
            vendor = vendor.split("\n")[0].strip()
            break

    # ---------------- Currency ----------------

    m = re.search(r'\b(USD|EUR|GBP)\b', text, re.IGNORECASE)
    if m:
        currency = m.group(1).upper()

    # ---------------- Date ----------------

    m = re.search(r'\b20\d{2}-\d{2}-\d{2}\b', text)
    if m:
        date = m.group()

    # ---------------- Amount ----------------

    amount_patterns = [

        r'Grand Total\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*\$?\s*([0-9]+(?:\.[0-9]+)?)',

        r'Total Amount\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*\$?\s*([0-9]+(?:\.[0-9]+)?)',

        r'Invoice Amount\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*\$?\s*([0-9]+(?:\.[0-9]+)?)',

        r'Amount Due\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*\$?\s*([0-9]+(?:\.[0-9]+)?)',

        r'Amount\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*\$?\s*([0-9]+(?:\.[0-9]+)?)',

        r'Total\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*\$?\s*([0-9]+(?:\.[0-9]+)?)',

        r'(?:USD|EUR|GBP)\s*([0-9]+(?:\.[0-9]+)?)',

        r'([0-9]+(?:\.[0-9]+)?)\s*(?:USD|EUR|GBP)',
    ]

    for p in amount_patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            amount = float(m.group(1))
            break

    # fallback: largest decimal number
    if amount == 0.0:
        nums = re.findall(r'\d+\.\d+|\d+', text)
        values = []

        for n in nums:
            try:
                values.append(float(n))
            except:
                pass

        if values:
            amount = max(values)

    return InvoiceResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date
    )
