import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from core import calculate_taxes_and_contributions

app = FastAPI()

class DealRequest(BaseModel):
    revenue: float
    expense: float = 0.0
    expense_category: str = "with_vat"  # "with_vat", "without_vat", "no_docs"
    vat_rate: float = 12.0

@app.get("/logo.png")
def get_logo():
    if os.path.exists("logo.png"):
        return FileResponse("logo.png")
    return HTMLResponse(status_code=404)

@app.get("/", response_class=HTMLResponse)
def get_index():
    return """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Расчет сделки (ИП на ОУР с НДС)</title>
    
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <link rel="apple-touch-icon" href="/logo.png">
    <link rel="icon" type="image/png" href="/logo.png">

    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #0b132b;
            margin: 0;
            padding: 16px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .card {
            background: #ffffff;
            width: 100%;
            max-width: 440px;
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
        }
        .header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #e5e5ea;
        }
        .logo {
            width: 44px;
            height: 44px;
            border-radius: 10px;
            object-fit: cover;
        }
        .header h1 {
            font-size: 18px;
            font-weight: 700;
            color: #1c1c1e;
            margin: 0;
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
        input, select {
            width: 100%;
            padding: 12px 14px;
            font-size: 16px;
            border: 1px solid #d1d1d6;
            border-radius: 12px;
            background-color: #f9f9fb;
            outline: none;
        }
        input:focus, select:focus {
            border-color: #007aff;
            background-color: #ffffff;
        }
        .row-group {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 10px;
        }
        .btn {
            width: 100%;
            background-color: #2563eb;
            color: white;
            border: none;
            padding: 14px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 12px;
            cursor: pointer;
            margin-top: 10px;
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
        .res-row {
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            font-size: 14px;
            color: #3a3a3c;
        }
        .res-row.total {
            font-size: 16px;
            font-weight: 700;
            border-top: 1px dashed #e5e5ea;
            margin-top: 6px;
            padding-top: 8px;
            color: #1c1c1e;
        }
        .val-tax { color: #dc2626; font-weight: 600; }
        .val-clean { color: #16a34a; font-weight: 700; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <img src="/logo.png" alt="Лого" class="logo">
            <h1>Расчет сделки (ИП на ОУР с НДС)</h1>
        </div>

        <div class="input-group">
            <label>Сумма от клиента (выручка с учетом НДС):</label>
            <input type="number" id="revenue" placeholder="500000" inputmode="numeric">
        </div>

        <div class="input-group">
            <label>Расход по сделке (поставщику / подрядчику):</label>
            <input type="number" id="expense" placeholder="300000" inputmode="numeric">
        </div>

        <div class="row-group">
            <div class="input-group">
                <label>Категория расхода:</label>
                <select id="expense_cat">
                    <option value="with_vat">В орган / с НДС</option>
                    <option value="without_vat">Без НДС (с актами)</option>
                    <option value="no_docs">Без документов</option>
                </select>
            </div>
            <div class="input-group">
                <label>Ставка НДС:</label>
                <select id="vat_rate">
                    <option value="12">12%</option>
                </select>
            </div>
        </div>

        <button class="btn" onclick="calc()">Рассчитать налоги и маржу</button>

        <div class="results" id="resBox">
            <div class="res-row">
                <span>НДС к уплате:</span>
                <span class="val-tax" id="res_vat">0 ₸</span>
            </div>
            <div class="res-row">
                <span>ИПН (10%):</span>
                <span class="val-tax" id="res_ipn">0 ₸</span>
            </div>
            <div class="res-row total">
                <span>Итого налогов:</span>
                <span class="val-tax" id="res_total">0 ₸</span>
            </div>
            <div class="res-row total" style="border-top: none; padding-top: 4px;">
                <span>Чистая маржа (на руки):</span>
                <span class="val-clean" id="res_clean">0 ₸</span>
            </div>
        </div>
    </div>

    <script>
        async function calc() {
            const req = {
                revenue: parseFloat(document.getElementById('revenue').value) || 0,
                expense: parseFloat(document.getElementById('expense').value) || 0,
                expense_category: document.getElementById('expense_cat').value,
                vat_rate: parseFloat(document.getElementById('vat_rate').value) || 12.0
            };

            try {
                const res = await fetch('/api/calc', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(req)
                });
                const d = await res.json();

                document.getElementById('res_vat').innerText = (d.vat_to_pay || 0).toLocaleString('ru-RU') + ' ₸';
                document.getElementById('res_ipn').innerText = (d.ipn_to_pay || 0).toLocaleString('ru-RU') + ' ₸';
                document.getElementById('res_total').innerText = (d.total_taxes || 0).toLocaleString('ru-RU') + ' ₸';
                document.getElementById('res_clean').innerText = (d.clean_cash || 0).toLocaleString('ru-RU') + ' ₸';

                document.getElementById('resBox').style.display = 'block';
            } catch(e) {
                alert('Ошибка расчета: ' + e);
            }
        }
    </script>
</body>
</html>
"""

@app.post("/api/calc")
def api_calc(data: DealRequest):
    # Преобразуем параметры под оригинальную логику
    exp_with_vat = data.expense if data.expense_category == "with_vat" else 0.0
    exp_without_vat = data.expense if data.expense_category == "without_vat" else 0.0
    exp_no_docs = data.expense if data.expense_category == "no_docs" else 0.0

    return calculate_taxes_and_contributions(
        revenue=data.revenue,
        expense_with_vat=exp_with_vat,
        expense_without_vat=exp_without_vat,
        expense_no_docs=exp_no_docs
    )
