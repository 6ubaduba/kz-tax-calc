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

        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden; /* Исключаем любой скролл */
            background-color: var(--bg);
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
            color: var(--text);
        }

        body {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 8px;
        }

        .card {
            width: 100%;
            max-width: 400px;
            background: var(--card-bg);
            border-radius: 22px;
            padding: 14px 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            display: flex;
            flex-direction: column;
            transition: all 0.25s ease;
        }

        /* Шапка */
        .header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
            transition: all 0.2s ease;
        }

        .logo {
            width: 44px;
            height: 44px;
            border-radius: 12px;
            object-fit: cover;
            transition: all 0.2s ease;
        }

        .header-info h1 {
            font-size: 16px;
            margin: 0;
            font-weight: 700;
        }

        .header-info p {
            font-size: 11px;
            color: var(--subtext);
            margin: 2px 0 0 0;
        }

        /* Блок полей ввода (в 1 колонку по умолчанию) */
        .inputs-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 8px;
            transition: all 0.25s ease;
        }

        .input-row {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .input-row label {
            font-size: 11px;
            font-weight: 600;
            color: #636366;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .box {
            position: relative;
            display: flex;
            align-items: center;
        }

        .box input {
            width: 100%;
            height: 40px;
            padding: 0 28px 0 10px;
            font-size: 15px;
            font-weight: 600;
            background: #f9f9fb;
            border: 1.5px solid var(--border);
            border-radius: 10px;
            outline: none;
            transition: all 0.2s ease;
        }

        .box input:focus {
            border-color: var(--accent);
            background: #ffffff;
        }

        .box .sym {
            position: absolute;
            right: 8px;
            font-size: 13px;
            color: var(--subtext);
            font-weight: 600;
        }

        /* Кнопка */
        .btn-calc {
            width: 100%;
            height: 44px;
            background: var(--accent);
            color: #fff;
            border: none;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 10px;
            transition: all 0.2s ease;
        }

        .btn-calc:active {
            opacity: 0.85;
        }

        /* Результаты */
        .results-box {
            display: none;
            margin-top: 10px;
            background: #fbfbfd;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 10px 12px;
            animation: fadeIn 0.25s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .clean-banner {
            background: #eefdf2;
            border: 1px solid #bbf7d0;
            border-radius: 10px;
            padding: 8px 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .clean-banner span {
            font-size: 12px;
            font-weight: 600;
            color: #166534;
        }

        .clean-banner strong {
            font-size: 18px;
            font-weight: 800;
            color: var(--green);
        }

        .data-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 4px 0;
            font-size: 12px;
            color: #3a3a3c;
        }

        .data-row strong {
            font-size: 13px;
            color: var(--red);
        }

        .data-row.total {
            border-top: 1px dashed var(--border);
            margin-top: 4px;
            padding-top: 6px;
            font-weight: 700;
        }

        /* КОМПАКТНЫЙ РЕЖИМ ПРИ НАЖАТИИ КНОПКИ */
        .compact-mode .header {
            margin-bottom: 6px;
        }
        .compact-mode .logo {
            width: 28px;
            height: 28px;
            border-radius: 8px;
        }
        .compact-mode .header-info h1 {
            font-size: 13px;
        }
        .compact-mode .header-info p {
            display: none;
        }
        /* Перестройка в сетку 2x2 */
        .compact-mode .inputs-grid {
            grid-template-columns: 1fr 1fr;
            gap: 6px;
        }
        .compact-mode .input-row label {
            font-size: 10px;
        }
        .compact-mode .box input {
            height: 30px;
            font-size: 12px;
            padding: 0 20px 0 6px;
            border-radius: 8px;
        }
        .compact-mode .box .sym {
            font-size: 10px;
            right: 6px;
        }
        .compact-mode .btn-calc {
            height: 34px;
            font-size: 13px;
            margin-top: 6px;
            border-radius: 10px;
        }
    </style>
</head>
<body>

<div class="card" id="mainCard">
    <div class="header">
        <img src="/logo.png" alt="Лого" class="logo">
        <div class="header-info">
            <h1>Налоги РК • Калькулятор</h1>
            <p>ОУР с НДС (12% / 10%)</p>
        </div>
    </div>

    <!-- Сетка полей ввода -->
    <div class="inputs-grid">
        <div class="input-row">
            <label>1. Доход с НДС</label>
            <div class="box">
                <input type="text" id="rev" inputmode="numeric" placeholder="0">
                <span class="sym">₸</span>
            </div>
        </div>

        <div class="input-row">
            <label>2. Расход с НДС</label>
            <div class="box">
                <input type="text" id="exp_v" inputmode="numeric" placeholder="0">
                <span class="sym">₸</span>
            </div>
        </div>

        <div class="input-row">
            <label>3. Расход без НДС</label>
            <div class="box">
                <input type="text" id="exp_nv" inputmode="numeric" placeholder="0">
                <span class="sym">₸</span>
            </div>
        </div>

        <div class="input-row">
            <label>4. Без документов</label>
            <div class="box">
                <input type="text" id="exp_nd" inputmode="numeric" placeholder="0">
                <span class="sym">₸</span>
            </div>
        </div>
    </div>

    <button class="btn-calc" id="calcBtn" onclick="calculate()">Рассчитать</button>

    <!-- Блок результатов -->
    <div class="results-box" id="resBox">
        <div class="clean-banner">
            <span>На руки:</span>
            <strong id="rClean">0 ₸</strong>
        </div>

        <div class="data-row">
            <span>НДС (12%):</span>
            <strong id="rVat">0 ₸</strong>
        </div>
        <div class="data-row">
            <span>ИПН (10%):</span>
            <strong id="rIpn">0 ₸</strong>
        </div>
        <div class="data-row total">
            <span style="color: var(--text);">Всего налогов:</span>
            <strong id="rTotal">0 ₸</strong>
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
        // Прячем клавиатуру смартфона
        document.activeElement.blur();

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
            const d = await res.json();

            document.getElementById('rClean').innerText = fmt(d.clean_cash);
            document.getElementById('rVat').innerText = fmt(d.vat_to_pay);
            document.getElementById('rIpn').innerText = fmt(d.ipn_to_pay);
            document.getElementById('rTotal').innerText = fmt(d.total_taxes);

            // Переключаем в компактный режим 2х2 и показываем расчет
            document.getElementById('mainCard').classList.add('compact-mode');
            document.getElementById('resBox').style.display = 'block';
            document.getElementById('calcBtn').innerText = 'Пересчитать';
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
