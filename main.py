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
    return """<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover"><title>Расчет сделки (ОУР РК)</title><link rel="icon" href="/logo.png"><link rel="apple-touch-icon" href="/logo.png"><style>:root{--bg:#0b132b;--c:#ffffff;--b:#e2e8f0;--t:#1e293b;--m:#64748b;--i:#f8fafc;--a:#2563eb;--subinfo:#475569}body.dark{--bg:#070b19;--c:#111827;--b:#1f293d;--t:#f3f4f6;--m:#9ca3af;--i:#1f293d;--a:#3b82f6;--subinfo:#94a3b8}*{box-sizing:border-box;-webkit-tap-highlight-color:transparent;font-family:-apple-system,sans-serif}body{margin:0;min-height:100vh;background:var(--bg);display:flex;justify-content:center;align-items:center;padding:12px;color:var(--t)}.card{width:100%;max-width:420px;background:var(--c);border:1px solid var(--b);border-radius:20px;padding:18px 20px;box-shadow:0 10px 25px rgba(0,0,0,0.25)}.head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid var(--b)}.hl{display:flex;align-items:center;gap:10px}.logo{width:38px;height:38px;border-radius:9px;object-fit:cover}.head h1{font-size:16px;margin:0;font-weight:700}.tbtn{background:var(--i);border:1px solid var(--b);border-radius:8px;width:34px;height:34px;cursor:pointer;font-size:15px;color:var(--t)}.grid{display:flex;flex-direction:column;gap:10px}.fld{display:flex;flex-direction:column;gap:3px}.lbl{font-size:12px;font-weight:600;color:var(--m);display:flex;align-items:center;gap:5px}.subcalc{font-size:11px;color:var(--subinfo);min-height:15px;line-height:1.2}.subcalc b{color:var(--t)}.subcalc.warn{color:#ef4444;font-weight:600}.tip{width:16px;height:16px;border-radius:50%;background:var(--i);border:1px solid var(--b);color:var(--m);font-size:11px;font-weight:bold;display:inline-flex;justify-content:center;align-items:center;cursor:pointer;position:relative}.tip:hover,.tip.act{background:var(--a);color:#fff}.tip .pop{display:none;position:absolute;bottom:130%;left:50%;transform:translateX(-50%);width:220px;background:#1e293b;color:#fff;font-size:11px;padding:8px 10px;border-radius:8px;z-index:99;pointer-events:none;line-height:1.35;font-weight:400}.tip:hover .pop,.tip.act .pop{display:block}input,select{width:100%;height:40px;padding:0 12px;font-size:15px;border:1.5px solid var(--b);border-radius:10px;background:var(--i);color:var(--t);outline:none}input:focus,select:focus{border-color:var(--a)}.r2{display:grid;grid-template-columns:2fr 1fr;gap:10px}.calc-btn{width:100%;height:44px;background:var(--a);color:#fff;border:none;font-size:15px;font-weight:600;border-radius:12px;cursor:pointer;margin-top:12px}.res{margin-top:12px;border-top:1px solid var(--b);padding-top:10px;display:none}.row{display:flex;justify-content:space-between;padding:4px 0;font-size:13px;color:var(--m)}.tot{font-size:15px;font-weight:700;border-top:1px dashed var(--b);margin-top:4px;padding-top:6px;color:var(--t)}.red{color:#ef4444;font-weight:600}.grn{color:#10b981;font-weight:700}.mini .head{margin-bottom:6px;padding-bottom:6px}.mini .logo{width:28px;height:28px}.mini .head h1{font-size:13px}.mini .grid{display:grid;grid-template-columns:1fr 1fr;gap:6px}.mini .r2{grid-column:span 2;gap:6px}.mini .lbl{font-size:10px}.mini .subcalc{display:none}.mini input,.mini select{height:32px;font-size:12px;padding:0 8px}.mini .calc-btn{height:36px;font-size:13px;margin-top:8px}</style></head><body><div class="card" id="card"><div class="head"><div class="hl"><img src="/logo.png" alt="Лого" class="logo"><h1>Расчет сделки (ОУР)</h1></div><button class="tbtn" id="tb" onclick="toggleTheme()">🌙</button></div><div class="grid"><div class="fld"><div class="lbl">Сумма от клиента:<span class="tip" onclick="tTip(event,this)">ⓘ<span class="pop">Полная сумма выставленного счета с НДС.</span></span></div><input type="number" id="rev" placeholder="500000" inputmode="numeric" oninput="liveCalc()"><div class="subcalc" id="sub_rev">Чистая выручка: 0 ₸ | НДС: 0 ₸</div></div><div class="fld"><div class="lbl">Расход по сделке:<span class="tip" onclick="tTip(event,this)">ⓘ<span class="pop">Оплата поставщику или субподрядчику.</span></span></div><input type="number" id="exp" placeholder="300000" inputmode="numeric" oninput="liveCalc()"><div class="subcalc" id="sub_exp">Зачет НДС: 0 ₸ | Вычет ИПН: 0 ₸</div></div><div class="r2"><div class="fld"><div class="lbl">Категория расхода:<span class="tip" onclick="tTip(event,this)">ⓘ<span class="pop"><b>С НДС:</b> зачет НДС + вычет ИПН.<br><b>Без НДС:</b> только вычет.<br><b>Без док.:</b> без зачетов.</span></span></div><select id="cat" onchange="liveCalc()"><option value="with_vat">В орган / с НДС</option><option value="without_vat">Без НДС (с актами)</option><option value="no_docs">Без документов</option></select><div class="subcalc" id="sub_cat"></div></div><div class="fld"><div class="lbl">Ставка НДС:<span class="tip" onclick="tTip(event,this)">ⓘ<span class="pop">Ставка НДС сделки (12%, 16% или без НДС).</span></span></div><select id="rate" onchange="liveCalc()"><option value="12">12%</option><option value="16">16%</option><option value="none">Без НДС</option></select></div></div></div><button class="calc-btn" id="btn" onclick="calc()">Рассчитать налоги и маржу</button><div class="res" id="res"><div class="row"><span>НДС к уплате:</span><span class="red" id="r_vat">0 ₸</span></div><div class="row"><span>ИПН (10%):</span><span class="red" id="r_ipn">0 ₸</span></div><div class="row tot"><span>Итого налогов:</span><span class="red" id="r_tot">0 ₸</span></div><div class="row tot" style="border:none;padding-top:4px;"><span>Чистая маржа:</span><span class="grn" id="r_cln">0 ₸</span></div></div></div><script>function toggleTheme(){const isDark=document.body.classList.toggle('dark');localStorage.setItem('mode',isDark?'dark':'light');document.getElementById('tb').innerText=isDark?'☀️':'🌙';}if(localStorage.getItem('mode')==='dark'){document.body.classList.add('dark');document.getElementById('tb').innerText='☀️';}function tTip(e,el){e.stopPropagation();document.querySelectorAll('.tip').forEach(t=>{if(t!==el)t.classList.remove('act');});el.classList.toggle('act');}document.addEventListener('click',()=>document.querySelectorAll('.tip').forEach(t=>t.classList.remove('act')));const fmt=n=>Math.round(n).toLocaleString('ru-RU')+' ₸';function liveCalc(){const rev=parseFloat(document.getElementById('rev').value)||0;const exp=parseFloat(document.getElementById('exp').value)||0;const cat=document.getElementById('cat').value;const rateVal=document.getElementById('rate').value;const rate=rateVal==='none'?0:parseFloat(rateVal)||12;const vatOut=rate>0?rev*(rate/(100+rate)):0;const revNet=rev-vatOut;document.getElementById('sub_rev').innerHTML=`Чистая: <b>${fmt(revNet)}</b> | НДС реализации: <b>${fmt(vatOut)}</b>`;let vatIn=0,expDed=0,warnTxt='';if(cat==='with_vat'){const expRate=rate>0?rate:12;vatIn=exp*(expRate/(100+expRate));expDed=exp-vatIn;warnTxt='Полный зачет НДС и вычет по расходам.';}else if(cat==='without_vat'){expDed=exp;warnTxt='Только вычет ИПН. НДС не зачитывается.';}else{warnTxt='⚠️ Риск: без документов налоги не уменьшаются!';document.getElementById('sub_cat').className='subcalc warn';}if(cat!=='no_docs')document.getElementById('sub_cat').className='subcalc';document.getElementById('sub_exp').innerHTML=`Зачет НДС: <b>${fmt(vatIn)}</b> | Вычет ИПН: <b>${fmt(expDed)}</b>`;document.getElementById('sub_cat').innerText=warnTxt;}liveCalc();async function calc(){document.activeElement.blur();const rVal=document.getElementById('rate').value;const req={revenue:parseFloat(document.getElementById('rev').value)||0,expense:parseFloat(document.getElementById('exp').value)||0,expense_category:document.getElementById('cat').value,vat_rate:rVal==='none'?0.0:(parseFloat(rVal)||12.0)};try{const res=await fetch('/api/calc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(req)});const d=await res.json();document.getElementById('r_vat').innerText=fmt(d.vat_to_pay);document.getElementById('r_ipn').innerText=fmt(d.ipn_to_pay);document.getElementById('r_tot').innerText=fmt(d.total_taxes);document.getElementById('r_cln').innerText=fmt(d.clean_cash);document.getElementById('card').classList.add('mini');document.getElementById('res').style.display='block';document.getElementById('btn').innerText='Пересчитать';}catch(e){alert('Ошибка: '+e);}}</script></body></html>"""

@app.post("/api/calc")
def api_calc(data: DealRequest):
    # Исходящий НДС и чистый доход
    if data.vat_rate > 0:
        vat_output = data.revenue * (data.vat_rate / (100.0 + data.vat_rate))
    else:
        vat_output = 0.0
    rev_net = data.revenue - vat_output

    # Входящий НДС и разрешенные вычеты
    vat_input = 0.0
    deductions = 0.0

    if data.expense_category == "with_vat":
        rate_exp = data.vat_rate if data.vat_rate > 0 else 12.0
        vat_input = data.expense * (rate_exp / (100.0 + rate_exp))
        deductions = data.expense - vat_input
    elif data.expense_category == "without_vat":
        deductions = data.expense
    elif data.expense_category == "no_docs":
        deductions = 0.0

    # 1. НДС к уплате
    vat_to_pay = max(0.0, vat_output - vat_input)

    # 2. ИПН (10%) с налогооблагаемого дохода
    taxable_income = max(0.0, rev_net - deductions)
    ipn_to_pay = taxable_income * 0.10

    # 3. Сумма налогов и чистые деньги
    total_taxes = vat_to_pay + ipn_to_pay
    clean_cash = data.revenue - data.expense - total_taxes

    return {
        "vat_to_pay": round(vat_to_pay),
        "ipn_to_pay": round(ipn_to_pay),
        "total_taxes": round(total_taxes),
        "clean_cash": round(clean_cash)
    }
