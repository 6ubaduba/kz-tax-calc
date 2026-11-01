from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from core import calculate_deal

app = FastAPI(title="Калькулятор сделок ИП на НДС", version="3.0")

class DealRequest(BaseModel):
    revenue_gross: float = Field(..., example=500000)
    expense_gross: float = Field(..., example=300000)
    expense_type: str = Field("with_vat", example="with_vat")
    vat_rate: float = Field(0.12, example=0.12)

@app.get("/", response_class=HTMLResponse)
def index_page():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Калькулятор сделки ИП (ОУР + НДС)</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #1e293b; padding: 15px; margin: 0; }
            .container { max-width: 580px; margin: 0 auto; background: #ffffff; padding: 24px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.25); }
            h2 { margin-top: 0; color: #0f172a; font-size: 20px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
            label { display: block; margin: 12px 0 4px; font-weight: 600; font-size: 14px; color: #334155; }
            input[type="number"], select { width: 100%; padding: 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; box-sizing: border-box; font-size: 16px; outline: none; background: #f8fafc; }
            input[type="number"]:focus, select:focus { border-color: #2563eb; background: #fff; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
            button { width: 100%; margin-top: 20px; padding: 14px; background: #2563eb; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 700; cursor: pointer; }
            button:hover { background: #1d4ed8; }
            .result-card { margin-top: 20px; background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 18px; display: none; }
            .group-title { font-weight: 700; font-size: 13px; text-transform: uppercase; color: #64748b; margin: 12px 0 6px; }
            .row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px dashed #cbd5e1; font-size: 14px; }
            .highlight-green { background: #dcfce7; border-left: 5px solid #16a34a; padding: 12px; border-radius: 6px; margin-top: 15px; font-size: 17px; font-weight: 700; color: #14532d; }
            .highlight-blue { background: #eff6ff; border-left: 5px solid #2563eb; padding: 10px; border-radius: 6px; margin-top: 10px; font-size: 13px; color: #1e40af; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Расчет сделки (ИП на ОУР с НДС)</h2>
            
            <label>Сумма от клиента (выручка с учетом НДС):</label>
            <input type="number" id="revenue" value="500000">

            <label>Расход по сделке (поставщику / подрядчику):</label>
            <input type="number" id="expense" value="300000">

            <div class="grid">
                <div>
                    <label>Категория расхода:</label>
                    <select id="expense_type">
                        <option value="with_vat">В орган / с НДС</option>
                        <option value="no_vat">В орган / без НДС</option>
                        <option value="no_docs">Эксперту / без документов</option>
                    </select>
                </div>
                <div>
                    <label>Ставка НДС:</label>
                    <select id="vat_rate">
                        <option value="0.12" selected>12%</option>
                        <option value="0.16">16% (расчет формулы 16/116)</option>
                    </select>
                </div>
            </div>

            <button onclick="calculate()">Рассчитать налоги и маржу</button>

            <div id="results" class="result-card">
                <div class="group-title">НДС</div>
                <div class="row"><span>С реализации:</span><b id="vat_out">0 ₸</b></div>
                <div class="row"><span>В зачёт:</span><b id="vat_in">0 ₸</b></div>
                <div class="row"><span>НДС к уплате:</span><b id="vat_pay">0 ₸</b></div>

                <div class="group-title">ИПН (10% от чистой базы)</div>
                <div class="row"><span>Доход без НДС:</span><b id="rev_net">0 ₸</b></div>
                <div class="row"><span>Расход без НДС (к вычету):</span><b id="exp_deduct">0 ₸</b></div>
                <div class="row"><span>Налогооблагаемая прибыль:</span><b id="profit_taxable">0 ₸</b></div>
                <div class="row"><span>ИПН к уплате:</span><b id="ipn_pay">0 ₸</b></div>

                <div class="group-title">Итоги по сделке</div>
                <div class="row"><span>Итого налогов (НДС + ИПН):</span><b id="total_tax" style="color: #dc2626;">0 ₸</b></div>
                <div class="row"><span>Маржинальность:</span><b id="margin">0%</b></div>

                <div class="highlight-green" id="net_profit">Чистыми на руки: 0 ₸</div>
                <div class="highlight-blue" id="cash_check">Сверка по кэшу: ...</div>
            </div>
        </div>

        <script>
            function fmt(num) {
                return Number(num).toLocaleString('ru-RU') + ' ₸';
            }

            async function calculate() {
                const payload = {
                    revenue_gross: parseFloat(document.getElementById('revenue').value) || 0,
                    expense_gross: parseFloat(document.getElementById('expense').value) || 0,
                    expense_type: document.getElementById('expense_type').value,
                    vat_rate: parseFloat(document.getElementById('vat_rate').value)
                };

                const res = await fetch('/calculate-deal', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();

                document.getElementById('results').style.display = 'block';
                document.getElementById('vat_out').innerText = fmt(data['НДС']['НДС с реализации']);
                document.getElementById('vat_in').innerText = fmt(data['НДС']['НДС в зачет']);
                document.getElementById('vat_pay').innerText = fmt(data['НДС']['НДС к уплате']);

                document.getElementById('rev_net').innerText = fmt(data['ИПН']['Доход без НДС']);
                document.getElementById('exp_deduct').innerText = fmt(data['ИПН']['Расход, принятый на вычет']);
                document.getElementById('profit_taxable').innerText = fmt(data['ИПН']['Налогооблагаемая прибыль']);
                document.getElementById('ipn_pay').innerText = fmt(data['ИПН']['ИПН (10%) к уплате']);

                document.getElementById('total_tax').innerText = fmt(data['Итого налогов (НДС + ИПН)']);
                document.getElementById('margin').innerText = data['Маржинальность от оборота'];
                document.getElementById('net_profit').innerText = 'Чистыми на руки: ' + fmt(data['Чистая прибыль (на руки)']);
                document.getElementById('cash_check').innerText = 'Сверка по кэшу: ' + data['Сверка по кэшу'];
            }
        </script>
    </body>
    </html>
    """

@app.post("/calculate-deal")
def calculate_deal_endpoint(data: DealRequest):
    return calculate_deal(
        revenue_gross=data.revenue_gross,
        expense_gross=data.expense_gross,
        expense_type=data.expense_type,
        vat_rate=data.vat_rate
    )
