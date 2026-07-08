from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()

class InvoiceRequest(BaseModel):
    text: str

class InvoiceResponse(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


@app.post("/extract", response_model=InvoiceResponse)
def extract(req: InvoiceRequest):

    text = req.text

    vendor = ""

    m = re.search(r"([A-Za-z0-9\- ]+Industries Ltd\.)", text, re.I)
    if m:
        vendor = m.group(1).strip()

    amount = 0

    m = re.search(r"(\d+(?:\.\d+)?)", text)
    if m:
        amount = float(m.group(1))

    currency = ""

    m = re.search(r"\b(USD|EUR|GBP)\b", text)
    if m:
        currency = m.group(1)

    date = ""

    m = re.search(r"\d{4}-\d{2}-\d{2}", text)
    if m:
        date = m.group()

    return {
        "vendor": vendor,
        "amount": amount,
        "currency": currency,
        "date": date,
    }
