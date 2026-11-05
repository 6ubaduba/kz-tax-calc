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
    return """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Расчет сделки (ИП на ОУР с НДС)</title>
    <meta name="apple-mobile-web-app-capable" content="yes">
    <link rel="apple-touch-icon" href="/logo.png"><link rel="icon" href="/logo.png">
    <style>
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body { margin: 0; min-height: 100vh; background: #0b132b; font-family: -apple-system, sans-serif; display: flex; justify-content: center; align-items: center; padding: 10px; color: #1c1c1e; }
        .card { width: 100%; max-width: 420px; background: #fff; border-radius: 20px; padding: 18px 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.25); }
        .header { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid #e5e5ea; }
        .logo { width: 44px; height: 44px; border-radius: 10px; object-fit: cover; }
        .header h1 { font-size: 17px; margin: 0; font-weight: 700; }
        .grid { display: flex; flex-direction: column; gap: 10px; }
        .field { display: flex; flex-direction: column; gap: 4px; }
        .lbl { font-size: 12px; font-weight: 600; color: #3a3a3c; display: flex; align-items: center; gap: 5px; }
        .tip { width: 16px; height: 16px; border-radius: 50%; background: #e5e5ea; color: #636366; font-size: 11px; font-weight: bold; display: inline-flex; justify-content: center; align-items: center; cursor: pointer; position: relative; }
        .tip:hover, .tip.act { background: #2563eb; color: #fff; }
        .tip .pop { display: none; position: absolute; bottom: 130%; left: 50%; transform: translateX(-50%); width: 220px; background: #1f2937; color: #fff; font-size: 11px; padding: 8px 10px; border-radius: 8px; z-index: 99; pointer-events: none; line-height: 1.35; font-weight: 400; }
        .tip:hover .pop, .tip.act .pop { display: block; }
        input, select { width: 100%; height: 42px; padding: 0 12px; font-size: 15px; border: 1.5px solid #d1d1d6; border-radius: 10px; background: #f9f9fb; outline: none; }
        input:focus, select:focus { border-color: #2563eb; background: #fff; }
        .row2 { display: grid; grid-template-columns: 2fr 1fr; gap: 10px; }
        .btn { width: 100%; height: 44px; background: #2563eb; color: #fff; border: none; font-size: 15px; font-weight: 600; border-radius: 12px; cursor: pointer; margin-top: 12px; }
        .btn:active { opacity: 0.85; }
        .res { margin-top: 10px; border-top: 1px solid #e5e5ea; padding-top: 10px; display: none; }
        .r-row { display: flex; justify-content: space-between; padding: 5px 0; font-size: 13px; color: #3a3a3c; }
        .r-row.tot { font-size: 15px; font-weight: 700; border-top: 1px dashed #e5e5ea; margin-top: 4px; padding-top: 6px; }
        .r-red { color: #dc2626; font-weight: 600; }
        .r-grn { color: #16a34a; font-weight: 700; }
        .mini .header { margin-bottom: 6px; padding-bottom: 6px; }
        .mini .logo { width: 30px; height: 30px; }
        .mini .header h1 { font-size: 14px; }
        .mini .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
        .mini .row2 { grid-column: span 2; gap: 6px; }
        .mini .lbl { font-size: 10px; }
        .mini input, .mini select { height: 32px; font-size: 12px; padding: 0 8px; }
        .mini .btn { height: 36px; font-size: 13px; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="card" id="card">
        <div class="header">
            <img src="/logo.png" alt="Лого" class="logo">
            <h1>Расчет сделки (ИП на ОУР с НДС)</h1>
        </div>
        <div class="grid">
            <div class="field">
                <div class="lbl">Сумма от клиента:
                    <span class="tip" onclick="tTip(event,this)">ⓘ<span class="pop">Полная сумма выставленного счета или оплаты от клиента с НДС.</span></span>
                </div>
                <input type="number" id="rev" placeholder="500000" inputmode="numeric">
            </div>
            <div class="field">
                <div class="lbl">Расход по сделке:
                    <span class="tip" onclick="tTip(event,this)">ⓘ<span class="pop">Оплата поставщику или подрядчику за товары/услуги.</span></span>
                </div>
                <input type="number" id="exp" placeholder="300000" inputmode="numeric">
            </div>
            <div class="row2">
                <div class="field">
                    <div class="lbl">Категория расхода:
                        <span class="tip" onclick="tTip(event,this)">ⓘ<span class="pop"><b>С НДС:</b> зачет НДС + вычет ИПН.<br><b>Без НДС:</b> только вычет ИПН.<br><b>Без док.:</b> без зачетов.</span></span>
                    </div>
                    <select id="cat">
                        <option value="with_vat">В орган / с НДС</option>
                        <option value="without_vat">Без НДС (с актами)</option>
                        <option value="no_docs">Без документов</option>
                    </select>
                </div>
                <div class="field">
                    <div class="lbl">Ставка НДС:
                        <span class="tip" onclick="tTip(event,this)">ⓘ<span class="pop">Ставка НДС по сделке (в РК стандартно 12%).</span></span>
                    </div>
                    <select id="rate">
                        <option value="12">12%</option>
                        <option value="0">0%</option>
                        <option value="none">Без НДС</option>
                    </select>
                </div>
            </div>
        </div>
        <button class="btn" id="btn" onclick="calc()">Рассчитать налоги и маржу</button>
        <div class="res" id="res">
            <div class="r-row"><span>НДС к уплате:</span><span class="r-red" id="r_vat">0 ₸</span></div>
            <div class="r-row"><span>ИПН (10%):</span><span class="r-red" id="r_ipn">0 ₸</span></div>
            <div class="r-row tot"><span>Итого налогов:</span><span class="r-red" id="r_tot">0 ₸</span></div>
            <div class="r-row tot" style="border:none; padding-top:4px;"><span>Чистая маржа:</span><span class="r-grn" id="r_cln">0 ₸</span></div>
        </div>
    </div>
    <script>
        function tTip(e, el) {
            e.stopPropagation();
            document.querySelectorAll('.tip').forEach(t => { if(t !== el) t.classList.remove('act'); });
            el.classList.toggle('act');
        }
        document.addEventListener('click', () => document.querySelectorAll('.tip').forEach(t => t.classList.remove('act')));

        async function calc() {
            document.activeElement.blur();
            const rVal = document.getElementById('rate').value;
            const req = {
                revenue: parseFloat(document.getElementById('rev').value) || 0,
                expense: parseFloat(document.getElementById('exp').value) || 0,
                expense_category: document.getElementById('cat').value,
                vat_rate: rVal === 'none' ? 0.0 : (parseFloat(rVal) || 12.0)
            };
            try {
                const res = await fetch('/api/calc', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(req) });
                const d = await res.json();
                document.getElementById('r_vat').innerText = (d.vat_to_pay ||
