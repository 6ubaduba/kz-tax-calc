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
    return """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Налоги РК • Калькулятор</title>
    
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="Налоги РК">
    <link rel="apple-touch-icon" href="/logo.png">
    <link rel="icon" type="image/png" href="/logo.png">

    <style>
        :root {
            --bg: #f2f2f7;
            --card-bg: #ffffff;
            --accent: #007aff;
            --text: #1c1c1e;
            --subtext: #8e8e93;
            --border: #e5e5ea;
            --red: #ff3b30;
            --green: #34c759;
        }

        * {
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 12px 14px;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
        }

        .app-card {
            width: 100%;
            max-width: 420px;
            background: var(--card-bg);
            border-radius: 24px;
            padding: 16px 18px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
        }

        .header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 14px;
        }

        .logo {
            width: 46px;
            height: 46px;
            border-radius: 12px;
            object-fit: cover;
            box-shadow: 0 2px 8px rgba(0, 122, 255, 0.2);
        }

        .header-text h1 {
            font-size: 17px;
            font-weight: 700;
            margin: 0;
        }

        .header-text p {
            font-size: 12px;
            color: var(--subtext);
            margin: 2px 0 0 0;
        }

        /* Блок свернутых данных */
        .compact-summary {
            display: none;
            background: #f8f9fa;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 10px 14px;
            margin-bottom: 12px;
            justify-content: space-between;
            align-items: center;
        }

        .compact-summary span {
            font-size: 13px;
            color: var(--subtext);
        }

        .compact-summary strong {
            font-size: 15px;
            color: var(--text);
            margin-left: 4px;
        }

        .btn-edit {
            background: none;
            border: none;
            color: var(--accent);
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            padding: 4px 8px;
        }

        /* Форма ввода */
        .form-body {
            transition: max-height 0.3s ease, opacity 0.2s ease;
        }

        .field {
            margin-bottom: 10px;
        }

        .field label {
            display: block;
            font-size: 12px;
            font-weight: 600;
            color: #48484a;
            margin-bottom: 4px;
        }

        .field .input-box {
            position: relative;
            display: flex;
            align-items: center;
        }

        .field input {
            width: 100%;
            height: 44px;
            padding: 8px 36px 8px 14px;
            font-size: 16px;
            font-weight: 600;
            border: 1.5px solid var(--border);
            border-radius: 12px;
            background-color: #f9f9fb;
            outline: none;
        }

        .field input:focus {
            border-color: var(--accent);
            background-color: #ffffff;
        }

        .field .curr {
            position: absolute;
            right: 14px;
            color: var(--subtext);
            font-weight: 600;
        }

        .btn-main {
            width: 100%;
            height: 48px;
            background: linear-gradient(135deg, #007aff, #0056b3);
            color: #fff;
            border: none;
            border-radius: 14px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 6px;
            box-shadow: 0 4px 12px rgba(0, 122, 255, 0.25);
        }

        .btn-main:active {
            opacity: 0.85;
        }

        /* Результаты во весь экран карточки */
        .result-card {
            display: none;
            animation: fadeIn 0.25s ease forwards;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.98); }
            to { opacity: 1; transform: scale(1); }
        }

        .hero-banner {
            background: #f0fdf4;
            border: 1.5px solid #bbf7d0;
            border-radius: 16px;
            padding: 14px;
            text-align: center;
            margin-bottom: 14px;
        }

        .hero-banner .title {
            font-size: 12px;
            font-weight: 600;
            color: #166534;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .hero-banner .amount {
            font-size: 26px;
            font-weight: 800;
            color: var(--green);
            margin-top: 4px;
        }

        .details-list {
            background: #fbfbfd;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 12px 14px;
        }

        .row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            font-size: 13px;
            color: #48484a;
        }

        .row strong {
            font-size: 14px;
            color: var(--text);
        }

        .row.tax strong {
            color: var(--red);
        }

        .row.divider {
            border-top: 1px dashed var(--border);
            margin-top: 4px;
            padding-top: 10px;
        }
    </style>
</head>
<body>

<div class="app-card">
    <div class="header">
        <img src="/logo.png" alt="Лого" class="logo">
        <div class="header-text">
            <h1>Налоги РК • Калькулятор</h1>
            <p>ИП на ОУР с НДС (12% / 10%)</p>
        </div>
    </div>

    <!-- Компактная плашка при показе результата -->
    <div class="compact-summary" id="compactBar">
        <div>
            <span>Доход:</span>
            <strong id="barRevenue">0 ₸</strong>
        </div>
        <button class="btn-edit" onclick="toggleEdit()">Изменить данные ✎</button>
    </div>

    <!-- Основная форма ввода -->
    <div class="form-body" id="formInputs">
        <div class="field">
            <label>Доход с НДС</label>
            <div class="input-box">
                <input type="text" id="rev" inputmode="numeric" placeholder="0">
                <span class="curr">₸</span>
            </div>
        </div>

        <div class="field">
            <label>Расход с НДС (с документами)</label>
            <div class="input-box">
                <input type="text" id="exp_v" inputmode="numeric" placeholder="0">
                <span class="curr">₸</span>
            </div>
        </div>

        <div class="field">
            <label>Расход без НДС (акты, ЭСФ)</label>
            <div class="input-box">
                <input type="text" id="exp_nv" inputmode="numeric" placeholder="0">
                <span class="curr">₸</span>
            </div>
        </div>

        <div class="field">
            <label>Расход без документов (невычет)</label>
            <div class="input-box">
                <input type="text" id="exp_nd" inputmode="numeric" placeholder="0">
                <span class="curr">₸</span>
            </div>
        </div>

        <button class="btn-main" onclick="calculate()">Рассчитать</button>
    </div>

    <!-- Результаты (занимают всё окно без прокрутки) -->
    <div class="result-card" id="resultsView">
        <div class="hero-banner">
            <div class="title">Чистый остаток на руках</div>
            <div class="amount" id="resClean">0 ₸</div>
        </div>

        <div class="details-list">
            <div class="row tax">
                <span>НДС к уплате (12%):</span>
                <strong id="resVat">0 ₸</strong>
            </div>
            <div class="row tax">
                <span>ИПН (10% с чистой прибыли):</span>
                <strong id="resIpn">0 ₸</strong>
            </div>
            <div class="row divider tax">
                <span style="font-weight: 600; color: var(--text);">Всего налогов в бюджет:</span>
                <strong style="font-size: 15px;" id="resTotalTax">0 ₸</strong>
            </div>
        </div>
    </div>
</div>

<script>
    const fmt = num => Math.round(num).toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, " ") + " ₸";
    const clean = val => parseFloat(val.replace(/\\s+/g, '')) || 0;

    ['rev', 'exp_v', 'exp_nv', 'exp_nd'].forEach(id => {
        const inp = document.getElementById(id);
        inp.addEventListener('input', () => {
            let val = inp.value.replace(/\\D/g, '');
            inp.value = val === '' ? '' : Number(val).toLocaleString('ru-RU');
        });
    });

    async function calculate() {
        const payload = {
            revenue: clean(document.getElementById('rev').value),
            expense_with_vat: clean(document.getElementById('exp_v').value),
            expense_without_vat: clean(document.getElementById('exp_nv').value),
            expense_no_docs: clean(document.getElementById('exp_nd').value)
        };

        try {
            const res = await fetch('/api/calc', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            // Заполняем данные
            document.getElementById('barRevenue').innerText = fmt(payload.revenue);
            document.getElementById('resClean').innerText = fmt(data.clean_cash);
            document.getElementById('resVat').innerText = fmt(data.vat_to_pay);
            document.getElementById('resIpn').innerText = fmt(data.ipn_to_pay);
            document.getElementById('resTotalTax').innerText = fmt(data.total_taxes);

            // Сворачиваем форму и открываем результат во весь экран
            document.getElementById('formInputs').style.display = 'none';
            document.getElementById('compactBar').style.display = 'flex';
            document.getElementById('resultsView').style.display = 'block';
        } catch(e) {
            alert('Ошибка расчета: ' + e);
        }
    }

    function toggleEdit() {
        document.getElementById('formInputs').style.display = 'block';
        document.getElementById('compactBar').style.display = 'none';
        document.getElementById('resultsView').style.display = 'none';
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
