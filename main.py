import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

app = FastAPI()

class DealRequest(BaseModel):
    revenue: float
    expense: float = 0.0
    expense_category: str = "with_vat"
    vat_rate: float = 12.0

@app.get("/logo.png")
def get_logo():
    if os.path.exists("logo.png"):
        return FileResponse("logo.png")
    return HTMLResponse(status_code=404)

@app.get("/", response_class=HTMLResponse)
def get_index():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>index.html not found</h1>"

@app.post("/api/calc")
def api_calc(data: DealRequest):
    vat_output = data.revenue * (data.vat_rate / (100.0 + data.vat_rate)) if data.vat_rate > 0 else 0.0
    rev_net = data.revenue - vat_output

    vat_input = 0.0
    exp_vat_net = 0.0
    expense_without_vat = 0.0

    if data.expense_category == "with_vat":
        vat_input = data.expense * (12.0 / 112.0)
        exp_vat_net = data.expense - vat_input
    elif data.expense_category == "without_vat":
        expense_without_vat = data.expense

    vat_to_pay = max(0.0, vat_output - vat_input)
    taxable_income = max(0.0, rev_net - (exp_vat_net + expense_without_vat))
    ipn_to_pay = taxable_income * 0.10
    total_taxes = vat_to_pay + ipn_to_pay
    clean_cash = data.revenue - data.expense - total_taxes

    return {
        "vat_to_pay": round(vat_to_pay),
        "ipn_to_pay": round(ipn_to_pay),
        "total_taxes": round(total_taxes),
        "clean_cash": round(clean_cash)
    }
