import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from core import calculate_tax_details

app = FastAPI()

class CalculationRequest(BaseModel):
    revenue: float
    expense_with_vat: float = 0.0
    expense_without_vat: float = 0.0
    expense_no_docs: float = 0.0

@app.get("/logo.png")
def get_logo():
    if os.path.exists("logo.png"):
        return FileResponse("logo.png")
    return HTMLResponse(status_code=404)

@app.get("/", response_class=HTMLResponse)
def get_index():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Налоги РК • Калькулятор</title>
        
        <link rel="apple-touch-icon" href="/logo.png">
        <link rel="icon" type="image/png" href="/logo.png">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        <meta name="apple-mobile-web-app-title" content="Налоги РК">

        <style>
            * { box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
                background-color: #f2f2f7;
                margin: 0;
                padding: 16px;
                display: flex;
                justify-content: center;
                -webkit-user-select: none;
                user-select: none;
            }
            .card {
                background: #ffffff;
                width: 100%;
                max-width: 440px;
                border-radius: 24px;
                padding: 24px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
            }
            .header {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                margin-bottom: 20px;
            }
            .logo {
                width: 76px;
                height: 76px;
                border-radius: 18px;
                object-fit: cover;
                box-shadow: 0 4px 12px rgba(0, 168, 204, 0.25);
                margin-bottom: 10px;
            }
            .header h1 {
                font-size: 20px;
                font-weight: 700;
                color: #1c1c1e;
                margin: 0;
            }
            .header p {
                font-size: 13px;
                color: #8e8e93;
                margin: 4px 0 0 0;
            }
            .input-group {
                margin-bottom: 14px;
            }
            label {
                display: block;
                font-size: 13px;
                font-weight: 600;
                color: #3a3a3c;
                margin-bottom: 6px;
            }
            input {
                width: 100%;
                padding: 12px 14px;
                font-size: 16px;
                border: 1px solid #d1d1d6;
                border-radius: 12px;
                background-color: #f9f9fb;
                outline: none;
                transition: border-color 0.2s, background-color 0.2s;
            }
            input:focus {
                border-color: #007aff;
                background-color: #ffffff;
            }
            .btn {
                width: 100%;
                background: linear-gradient(135deg, #007aff, #0056b3);
                color: white;
                border: none;
                padding: 14px;
                font-size: 16px;
                font-weight: 600;
                border-radius: 14px;
                cursor: pointer;
                margin-top: 10px;
                box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
            }
            .btn:active {
                opacity: 0.85;
            }
            .results {
                margin-top: 20px;
                border-top: 1px solid #e5e5ea;
                padding-top: 14px;
                display: none;
            }
            .row {
                display: flex;
                justify-content: space-between;
                padding: 6px 0;
                font-size: 14px;
                color: #3a3a3c;
            }
            .row.bold {
                font-weight: 700;
                color: #1c1c1e;
                font-size: 15px;
                border-top: 1px dashed #e5e5ea;
                margin-top: 6px;
                padding-top: 8px;
            }
            .row.final {
                font-size: 16px;
                font-weight: 800;
                padding-top: 10px;
                border-top: 2px solid #e5e5ea;
            }
            .tax-val { color: #ff3b30; }
            .net-val { color: #34c759; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <img src="/logo.png" alt="Логотип" class="logo">
                <h1>Налоги РК • Калькулятор</h1>
                <p>ИП на ОУР с НДС (12% / 10%)</p>
            </div>

            <div class="input-group">
                <label>Доход с НДС (₸):</label>
                <input type="number" id="revenue" placeholder="0" inputmode="numeric">
            </div>

            <div class="input-group">
                <label>Расход с НДС (с документами, ₸):</label>
                <input type="number" id="exp_vat" placeholder="0" inputmode="numeric">
            </div>

            <div class="input-group">
                <label>Расход без НДС (с актами/ЭСФ, ₸):</label>
                <input type="number" id="exp_novat" placeholder="0" inputmode="numeric">
            </div>

            <div class="input-group">
                <label>Расход без документов (невычет, ₸):</label>
                <input type="number" id="exp_nodocs" placeholder="0" inputmode="numeric">
            </div>

            <button class="btn" onclick="calc()">Рассчитать налоги</button>

            <div class="results" id="res">
                <div class="row"><span>НДС к уплате:</span><span id="res_vat" class="tax-val">0 ₸</span></div>
                <div class="row"><span>ИПН (10% с чистой прибыли):</span><span id="res_ipn" class="tax-val">0 ₸</span></div>
                <div class="row bold"><span>Итого налогов:</span><span id="res_total_tax" class="tax-val">0 ₸</span></div>
                <div class="row final"><span>Чистый остаток на руках:</span><span id="res_clean" class="net-val">0 ₸</span></div>
            </div>
        </div>

        <script>
            async function calc() {
                const req = {
                    revenue: parseFloat(document.getElementById('revenue').value) || 0,
                    expense_with_vat: parseFloat(document.getElementById('exp_vat').value) || 0,
                    expense_without_vat: parseFloat(document.getElementById('exp_novat').value) || 0,
                    expense_no_docs: parseFloat(document.getElementById('exp_nodocs').value) || 0
                };

                try {
                    const res = await fetch('/api/calc', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(req)
                    });
                    const d = await res.json();

                    document.getElementById('res_vat').innerText = d.vat_to_pay.toLocaleString('ru-RU') + ' ₸';
                    document.getElementById('res_ipn').innerText = d.ipn_to_pay.toLocaleString('ru-RU') + ' ₸';
                    document.getElementById('res_total_tax').innerText = d.total_taxes.toLocaleString('ru-RU') + ' ₸';
                    document.getElementById('res_clean').innerText = d.clean_cash.toLocaleString('ru-RU') + ' ₸';

                    document.getElementById('res').style.display = 'block';
                    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                } catch(e) {
                    alert('Ошибка расчета: ' + e);
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/calc")
def api_calc(data: CalculationRequest):
    return calculate_tax_details(
        revenue=data.revenue,
        expense_with_vat=data.expense_with_vat,
        expense_without_vat=data.expense_without_vat,
        expense_no_docs=data.expense_no_docs
    )
